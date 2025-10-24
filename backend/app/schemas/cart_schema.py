from pydantic import BaseModel
from typing import Optional, List

# Entrada al agregar un item al carrito
class CartItemCreate(BaseModel):
    product_uuid: str
    quantity: int

# Detalle de un item en el carrito
class CartItemDetail(BaseModel):
    id: str
    product_uuid: str
    product_name: Optional[str] = None
    quantity: int
    price: float
    total_price: float
    image_url: Optional[str] = None  # <-- nueva propiedad
    class Config:
        from_attributes = True  # Pydantic v2

# Carrito completo de un usuario
class CartItemOut(BaseModel):
    user_id: str
    items: List[CartItemDetail]


class CartItemResponse(BaseModel):
    product_id: str
    name: str
    price: float
    quantity: int
    subtotal: float
    image_url: Optional[str] = None  # <-- nueva propiedad
    class Config:
        from_attributes = True  # Reemplaza 'orm_mode' en Pydantic v2