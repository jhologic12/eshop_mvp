from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"

    user_uuid = Column(String, primary_key=True, index=True, default=generate_uuid)
    full_name = Column(String, nullable=False)  # reemplaza full_name por name
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)  # aquí guardaremos el hash
    is_admin = Column(Boolean, default=False)

    cart_items = relationship("CartItem", back_populates="user")
    payments = relationship("Payment", back_populates="user")
