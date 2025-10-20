from sqlalchemy import Column, String, Float, Text, Boolean, Integer
from app.core.database import Base, UUIDMixin
from sqlalchemy.orm import relationship
from uuid import uuid4



class Product(Base, UUIDMixin):
    __tablename__ = "products"
    name = Column(String(120), nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, default=True)
    image_small = Column(String(255), nullable=True)
    image_medium = Column(String(255), nullable=True)
    image_thumbnail = Column(String(255), nullable=True)
    cart_items = relationship("CartItem", back_populates="product")