from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class CartItem(Base):
    __tablename__ = "cart_items"

    cart_item_uuid = Column(String(36), primary_key=True, index=True, default=generate_uuid)

    # ✅ Apunta al UUID real de tu modelo User
    user_uuid = Column(String(36), ForeignKey("users.user_uuid"), nullable=False)  

    # ✅ Apunta al UUID del producto
    product_uuid = Column(String(36), ForeignKey("products.uuid"), nullable=False)  

    quantity = Column(Integer, nullable=False)

    # Relaciones
    user = relationship("User", back_populates="cart_items")
    product = relationship("Product", back_populates="cart_items")

    