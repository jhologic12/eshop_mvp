from sqlalchemy import Column, String, Float, Text, Boolean, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from app.core.database import Base
import uuid

class Product(Base):
    __tablename__ = "products"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String(120), nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, default=True)
    image_small = Column(String(255), nullable=True)
    image_medium = Column(String(255), nullable=True)
    image_thumbnail = Column(String(255), nullable=True)

    # Relaciones
    cart_items = relationship("CartItem", back_populates="product", cascade="all, delete-orphan")
