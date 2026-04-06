from uuid import uuid4
from sqlalchemy.orm import Session
from antifraud.app.models.models import Transaction, FraudAlert
from antifraud.app.schemas.schemas import BiometricStartResponse, BiometricCallbackRequest
import logging

logger = logging.getLogger("biometric_service")

class BiometricService:
    def __init__(self, db: Session):
        self.db = db

    def create_session(self, transaction_id: str) -> BiometricStartResponse:
        transaction = self.db.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()
        if not transaction:
            raise ValueError("Transaction not found")

        session_id = str(uuid4())
        transaction.biometric_session_id = session_id
        transaction.biometric_status = "PENDING"
        self.db.commit()

        # In a real MyID integration, we would call their API here.
        # For now, we point to our mock verification endpoint.
        verification_url = f"http://localhost:8000/api/v1/biometric/mock-verify?session_id={session_id}"
        
        return BiometricStartResponse(session_id=session_id, verification_url=verification_url)

    def handle_callback(self, request: BiometricCallbackRequest) -> bool:
        transaction = self.db.query(Transaction).filter(Transaction.biometric_session_id == request.session_id).first()
        if not transaction:
            logger.error(f"Biometric session not found: {request.session_id}")
            return False

        # Verify signature logic would go here
        # For simulation, we assume signature is valid

        if request.status == "SUCCESS":
            transaction.biometric_status = "COMPLETED"
            # Reduce risk score for successful biometric
            transaction.risk_score -= 20
            if transaction.risk_score < 30:
                transaction.status = "APPROVED"
        else:
            transaction.biometric_status = "FAILED"
            transaction.status = "DECLINED"
            # Log fraud alert
            alert = FraudAlert(
                transaction_id=transaction.transaction_id,
                user_id=transaction.user_id,
                rule_name="BiometricFailure",
                severity="HIGH",
                description="Biometric verification failed for high-risk transaction"
            )
            self.db.add(alert)

        self.db.commit()
        logger.info(f"Biometric callback handled for session {request.session_id}: {request.status}")
        return True
