# app/models/payment_model.py
from sqlalchemy import Column, Float, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from app.core.database import Base
import uuid

class Payment(Base):
    __tablename__ = "payments"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(String(255))
    user_uuid = Column(PG_UUID(as_uuid=True), ForeignKey("users.user_uuid"), nullable=False)

    user = relationship("User", back_populates="payments")