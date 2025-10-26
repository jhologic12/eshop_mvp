from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.checkout_service import process_checkout

router = APIRouter(prefix="/payments", tags=["Payments"])

class CheckoutRequest(BaseModel):
    card_number: str
    holder_name: str
    expiration_date: str
    cvv: str

@router.post("/checkout")
def checkout(payload: CheckoutRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    if not current_user.user_uuid:
        raise HTTPException(status_code=400, detail="Usuario no tiene cuenta vinculada")

    # ✅ Armar card_data esperado por process_checkout
    card_data = {
        "card_number": payload.card_number,
        "holder_name": payload.holder_name,
        "expiration_date": payload.expiration_date,
        "cvv": payload.cvv
    }

    # ✅ Enviar todo al servicio centralizado
    result = process_checkout(
        user=current_user,
        card_data=card_data,
        db=db
    )

    return result
