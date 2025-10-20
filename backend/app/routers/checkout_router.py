from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.payment_schema import PaymentRequest, PaymentResponse
from app.services.checkout_service import process_checkout
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(
    prefix="/checkout",
    tags=["checkout"]
)

@router.post("/payment", response_model=PaymentResponse)
def checkout_payment(
    payment_data: PaymentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Endpoint para procesar el pago del carrito usando Mock Payment.
    """
    result = process_checkout(current_user, payment_data.model_dump(), db)
    return result
