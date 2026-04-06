from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from antifraud.app.schemas.schemas import (
    TransactionCreate, TransactionResponse, FraudAlertResponse, RiskProfileResponse,
    BiometricStartRequest, BiometricStartResponse, BiometricCallbackRequest,
    MockBiometricVerifyRequest, MockBiometricVerifyResponse,
    FaceVerifyRequest, FaceVerifyResponse
)
from antifraud.app.models.models import Transaction, FraudAlert, UserDevice, FaceProfile
import numpy as np
from antifraud.app.core.db import get_db
from antifraud.app.services.velocity import VelocityCheckService
from antifraud.app.services.geo import GeoCheckService
from antifraud.app.services.device import DeviceRiskService
from antifraud.app.services.scoring import ScoringEngine
from antifraud.app.services.biometric import BiometricService
from antifraud.app.rules.base import VelocityRule, GeoRule, DeviceRule

router = APIRouter()

from antifraud.app.services.orchestrator import AntifraudOrchestrator

@router.post("/transactions/check", response_model=TransactionResponse)
async def check_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
    orchestrator = AntifraudOrchestrator(db)
    return await orchestrator.process_transaction(transaction)

@router.get("/fraud/alerts", response_model=List[FraudAlertResponse])
def get_fraud_alerts(db: Session = Depends(get_db), limit: int = 100):
    return db.query(FraudAlert).order_by(FraudAlert.created_at.desc()).limit(limit).all()

@router.get("/user/risk-profile/{user_id}", response_model=RiskProfileResponse)
def get_user_risk_profile(user_id: str, db: Session = Depends(get_db)):
    v_service = VelocityCheckService()
    d_service = DeviceRiskService(db)
    
    # Get stats from Redis and DB
    total_30m = v_service.get_count("user", user_id, 1800)
    failed_attempts = v_service.get_failed_attempts(user_id)
    devices = d_service.get_user_devices(user_id)
    
    # Last transaction status
    last_tx = db.query(Transaction).filter(Transaction.user_id == user_id).order_by(Transaction.timestamp.desc()).first()
    
    return {
        "user_id": user_id,
        "total_transactions_30m": total_30m,
        "failed_attempts": failed_attempts,
        "risk_score": last_tx.risk_score if last_tx else 0.0,
        "status": last_tx.status if last_tx else "UNKNOWN",
        "known_devices": [d.device_id for d in devices]
    }

# Biometric Endpoints
@router.post("/biometric/start-verification", response_model=BiometricStartResponse)
async def start_biometric_verification(request: BiometricStartRequest, db: Session = Depends(get_db)):
    service = BiometricService(db)
    try:
        return service.create_session(request.transaction_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/biometric/callback")
async def biometric_callback(request: BiometricCallbackRequest, db: Session = Depends(get_db)):
    service = BiometricService(db)
    success = service.handle_callback(request)
    if not success:
        raise HTTPException(status_code=400, detail="Invalid session or status")
    return {"status": "accepted"}

# Mock Biometric Provider for Simulation
@router.post("/biometric/mock-verify", response_model=MockBiometricVerifyResponse)
async def mock_biometric_verify(request: MockBiometricVerifyRequest):
    """Simulates MyID biometric verification."""
    # Logic: verified if match_score > 0.8 and liveness is True
    is_verified = request.match_score > 0.8 and request.liveness_result
    
    return MockBiometricVerifyResponse(
        verified=is_verified,
        match_score=request.match_score,
        liveness=request.liveness_result
    )

@router.post("/antifraud/verify", response_model=FaceVerifyResponse)
async def verify_face(request: FaceVerifyRequest, db: Session = Depends(get_db)):
    """
    Centralized face verification endpoint.
    Compares provided encoding against the stored profile in PostgreSQL.
    """
    profile = db.query(FaceProfile).filter(FaceProfile.user_id == request.user_id).first()
    if not profile:
        return FaceVerifyResponse(status="error", message="Face profile not found", match=False)
    
    try:
        stored_encoding = np.frombuffer(profile.face_encoding, dtype=np.float64)
        sample_encoding = np.array(request.face_encoding, dtype=np.float64)
        
        # Calculate Euclidean distance
        distance = np.linalg.norm(stored_encoding - sample_encoding)
        is_match = bool(distance < 0.35) # Adjusted threshold
        
        if not is_match:
            raise HTTPException(status_code=401, detail="Face did not match")
            
        return FaceVerifyResponse(
            status="success",
            message="Verification completed",
            match=True
        )
    except HTTPException:
        raise
    except Exception as e:
        return FaceVerifyResponse(status="error", message=f"Verification failed: {str(e)}", match=False)
