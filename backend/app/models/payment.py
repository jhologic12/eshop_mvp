from sqlalchemy import Column, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base, UUIDMixin

class Payment(Base, UUIDMixin):
    __tablename__ = "payments"

    amount = Column(Float, nullable=False)
    description = Column(String(255), nullable=True)

    # 🔹 Relación correcta con usuario
    user_uuid = Column(String(36), ForeignKey("users.user_uuid"), nullable=False)

    # 🔹 Relaciones ORM
    user = relationship("User", back_populates="payments")
