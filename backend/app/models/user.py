# app/models/user_model.py
from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from app.core.database import Base
import uuid

class User(Base):
    __tablename__ = "users"

    user_uuid = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)

    cart_items = relationship("CartItem", back_populates="user")
    payments = relationship("Payment", back_populates="user")
    payment_attempts = relationship("PaymentAttempt", back_populates="user")  # agregado
