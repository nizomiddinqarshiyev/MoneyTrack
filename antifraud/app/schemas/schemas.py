from datetime import datetime
from pydantic import BaseModel, Field, IPvAnyAddress
from typing import Optional, List
from uuid import UUID

class TransactionBase(BaseModel):
    transaction_id: str
    user_id: str
    sender_card: str
    receiver_card: str
    amount: float = Field(gt=0)
    currency: str = Field(min_length=3, max_length=3)
    timestamp: datetime
    sender_country: str = Field(min_length=2, max_length=2)
    receiver_country: str = Field(min_length=2, max_length=2)
    ip_address: str
    device_id: str
    channel: str

class TransactionCreate(TransactionBase):
    pass

class TransactionResponse(TransactionBase):
    id: UUID
    status: str
    risk_score: float
    
    class Config:
        from_attributes = True

class FraudAlertResponse(BaseModel):
    id: int
    transaction_id: Optional[int]
    user_id: int
    risk_level: str
    reasons: List[str]
    created_at: datetime

    class Config:
        from_attributes = True

class RiskProfileResponse(BaseModel):
    user_id: str
    total_transactions_30m: int
    failed_attempts: int
    risk_score: float
    status: str
    known_devices: List[str]

class BiometricStartRequest(BaseModel):
    transaction_id: str

class BiometricStartResponse(BaseModel):
    session_id: str
    verification_url: str

class BiometricCallbackRequest(BaseModel):
    session_id: str
    status: str  # SUCCESS, FAILED
    signature: str

class MockBiometricVerifyRequest(BaseModel):
    session_id: str
    user_id: str
    match_score: float = Field(ge=0, le=1)
    liveness_result: bool

class MockBiometricVerifyResponse(BaseModel):
    verified: bool
    match_score: float
    liveness: bool

class FaceVerifyRequest(BaseModel):
    user_id: int
    face_encoding: List[float]

class FaceVerifyResponse(BaseModel):
    status: str
    message: str
    match: bool
