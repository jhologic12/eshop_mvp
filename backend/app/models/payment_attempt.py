from sqlalchemy import Column, String, Float, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class PaymentAttempt(Base):
    __tablename__ = "payment_attempts"

    attempt_uuid = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, index=True)  # UUID del usuario
    amount = Column(Float)
    success = Column(Boolean, default=False)
    reason = Column(String, nullable=True)  # Por qué falló
    created_at = Column(DateTime, default=datetime.utcnow)
