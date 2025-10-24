from pydantic import BaseModel, Field
from typing import List, Annotated
from typing import Optional  # ✅ Asegúrate de importar Optional
class PurchasedProduct(BaseModel):
    product_id: str
    product_name: str
    quantity: int
    price: float
    subtotal: float
    image_url: Optional[str] = None

# 🔹 Petición del usuario para procesar un pago con tarjeta
class PaymentRequest(BaseModel):
     card_number: Annotated[str, Field(min_length=13, max_length=19)]
     holder_name: str
     expiration_date: str
     cvv: Annotated[str, Field(min_length=3, max_length=4)]

class PaymentResponse(BaseModel):
    message: str
    total: float
    items: List[PurchasedProduct]  # usar el modelo correcto

    class Config:
        from_attributes = True
