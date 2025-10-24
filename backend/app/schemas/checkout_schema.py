from pydantic import BaseModel
from typing import List, Optional

class ProductInCart(BaseModel):
    product_uuid: str
    name: str
    quantity: int
    price: float
    image_url: Optional[str] = None
    
class CheckoutResponse(BaseModel):
    id: str
    message: str
    total: float
    products: List[ProductInCart]
    payment_method: str
