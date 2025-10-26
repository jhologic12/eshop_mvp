# app/models/payment_attempt.py
from sqlalchemy import Column, Float, Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from app.core.database import Base
from datetime import datetime
import uuid

class PaymentAttempt(Base):
    __tablename__ = "payment_attempts"

    attempt_uuid = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_uuid = Column(PG_UUID(as_uuid=True), ForeignKey("users.user_uuid"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    success = Column(Boolean, default=False)
    reason = Column(String, nullable=True)  # Por qué falló
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relación con el usuario
    user = relationship("User", back_populates="payment_attempts")
