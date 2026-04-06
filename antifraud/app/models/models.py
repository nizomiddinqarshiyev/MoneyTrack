from datetime import datetime
from uuid import uuid4
from sqlalchemy import Column, String, Float, DateTime, Integer, JSON, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, relationship

class Base(DeclarativeBase):
    pass

class Transaction(Base):
    __tablename__ = "transactions_transaction"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    transaction_id = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(String, index=True, nullable=False)
    sender_card = Column(String, index=True, nullable=False)
    receiver_card = Column(String, index=True, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    sender_country = Column(String(2), nullable=False)
    receiver_country = Column(String(2), nullable=False)
    ip_address = Column(String, nullable=False)
    device_id = Column(String, index=True, nullable=False)
    channel = Column(String, nullable=False)
    status = Column(String, default="PENDING")  # PENDING, APPROVED, DECLINED, OTP_REQUIRED
    risk_score = Column(Float, default=0.0)
    biometric_session_id = Column(String, index=True, nullable=True)
    biometric_status = Column(String, default="NONE")  # NONE, PENDING, COMPLETED, FAILED

class FraudAlert(Base):
    __tablename__ = "antifraud_transactionrisk"

    id = Column(Integer, primary_key=True)
    transaction_id = Column(Integer, ForeignKey("transactions_transaction.id"), index=True)
    user_id = Column(Integer, index=True)
    risk_level = Column(String, nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    reasons = Column(JSON)
    is_verified = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class CountryHistory(Base):
    __tablename__ = "antifraud_userlocation"

    id = Column(Integer, primary_key=True)
    user_id = Column(String, index=True, nullable=False)
    country_code = Column(String(2), nullable=False)
    last_seen = Column(DateTime, default=datetime.utcnow)

class UserDevice(Base):
    __tablename__ = "user_devices"

    id = Column(Integer, primary_key=True)
    user_id = Column(String, index=True, nullable=False)
    device_id = Column(String, index=True, nullable=False)
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)

class FraudRule(Base):
    __tablename__ = "fraud_rules"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    weight = Column(Float, nullable=False)
    is_active = Column(Integer, default=1)  # 0 or 1
    config = Column(JSON)  # Thresholds, etc.

from sqlalchemy import LargeBinary

class FaceProfile(Base):
    __tablename__ = "antifraud_faceprofile"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, index=True)
    face_encoding = Column(LargeBinary)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
