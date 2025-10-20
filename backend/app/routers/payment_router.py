from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.checkout_service import process_checkout
from app.services.cart_service import clear_cart, get_cart_total
from app.core.config import MOCK_PAYMENT_URL

router = APIRouter(prefix="/payments", tags=["Payments"])

class CheckoutRequest(BaseModel):
    description: str

@router.post("/checkout")
def checkout(payload: CheckoutRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.user_uuid:
        raise HTTPException(status_code=400, detail="Usuario no tiene cuenta vinculada")

    total_cart = get_cart_total(user_uuid=current_user.user_uuid, db=db)
    if total_cart <= 0:
        raise HTTPException(status_code=400, detail="El carrito está vacío")

    payment_result = process_checkout(
        account_uuid=current_user.user_uuid,
        total_cart=total_cart,
        description=payload.description,
        MOCK_PAYMENT_URL=MOCK_PAYMENT_URL
    )

    # 🔹 Registrar intento de pago (opcional)
    # create_payment_attempt(user_uuid=current_user.user_uuid, amount=total_cart, success=(payment_result.get("status")=="aprobado"), db=db)

    if payment_result.get("status") == "aprobado":
        clear_cart(user_uuid=current_user.user_uuid, db=db)

    return {"message": "Pago realizado con éxito", "payment": payment_result}
