from pydantic import BaseModel
from typing import Optional, Dict


# 🔹 Esquema base para productos
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int
    is_active: Optional[bool] = True


# 🔹 Esquema para creación
class ProductCreate(ProductBase):
    image_base64: Optional[str] = None
    image_url: Optional[str] = None


# 🔹 Esquema para actualización
class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    is_active: Optional[bool] = None
    image_base64: Optional[str] = None
    image_url: Optional[str] = None


# 🔹 Esquema de respuesta
class ProductResponse(ProductBase):
    uuid: str
    image_small: Optional[str] = None
    image_thumbnail: Optional[str] = None
    image_medium: Optional[str] = None
    #images: Optional[Dict[str, str]] = {}

    class Config:
        from_attributes = True  # Pydantic v2 reemplaza orm_mode
