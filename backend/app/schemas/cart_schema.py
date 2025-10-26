from pydantic import BaseModel
from typing import Optional, List


# ✅ Entrada al agregar un item al carrito
class CartItemCreate(BaseModel):
    product_id: str   # UUID como string
    quantity: int


# ✅ Detalle de un item en el carrito (respuesta individual)
class CartItemDetail(BaseModel):
    id: str                      # UUID del cart item
    product_id: str              # UUID del producto
    product_name: Optional[str] = None
    quantity: int
    price: float                 # Precio unitario
    total_price: float           # price * quantity
    image_url: Optional[str] = None

    class Config:
        from_attributes = True   # Para soportar objetos ORM (Pydantic V2)


# ✅ Carrito completo de un usuario
class CartItemOut(BaseModel):
    user_id: str
    items: List[CartItemDetail]


# ✅ Otra versión posible de respuesta (por producto)
class CartItemResponse(BaseModel):
    product_id: str
    name: str
    price: float
    quantity: int
    subtotal: float
    image_url: Optional[str] = None

    class Config:
        from_attributes = True
