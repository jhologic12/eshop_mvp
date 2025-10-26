# app/routers/payment_router.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.cart import CartItem
from app.schemas.payment_schema import PaymentRequest
from app.schemas.payment_schema import PurchasedProduct
import httpx
import logging

from app.core.config import settings
MOCK_PAYMENT_URL = settings.mock_payment_url

router = APIRouter(prefix="/payments", tags=["Payments"])
logger = logging.getLogger(__name__)



# Para validar la tarjeta
validate_url = f"{MOCK_PAYMENT_URL}/cards/validate"

# Para procesar el pago
payment_url = f"{MOCK_PAYMENT_URL}/payments"


@router.post("/checkout")
async def checkout_payment(payment_in: PaymentRequest, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    # 1️⃣ Obtener items del carrito
    cart_items = db.query(CartItem).filter(CartItem.user_id == current_user.id).all()
    if not cart_items:
        raise HTTPException(status_code=400, detail="Carrito vacío")

    # 2️⃣ Calcular total del carrito
    total_cart = sum(item.product.price * item.quantity for item in cart_items)
    logger.info(f"Usuario {current_user.id} inicia checkout con monto {total_cart}")

    # 3️⃣ Validar tarjeta en mock externo
    card_payload = {
         "card_number": payment_in.card_number,       # ⚠️ igual
        "holder_name": payment_in.holder_name,       # ⚠️ renombrado de card_holder
        "expiration_date": payment_in.expiration_date,
        "cvv": payment_in.cvv
    }

    async with httpx.AsyncClient() as client:
        validate_resp = await client.post(validate_url, json=card_payload)
        if validate_resp.status_code != 200:
            raise HTTPException(status_code=502, detail="Error en servicio de validación de pagos")
        validate_data = validate_resp.json()

    account_uuid = validate_data.get("account_uuid")
    if not account_uuid:
        raise HTTPException(status_code=502, detail="Validación de tarjeta falló: no se recibió account_uuid")

    # 4️⃣ Preparar payload para pago
    payment_payload = {
        "account_uuid": account_uuid,
        "amount": total_cart,
        "description": "Compra de productos en eShop"
    }
    

    # 5️⃣ Ejecutar pago en mock externo
    async with httpx.AsyncClient() as client:
        payment_resp = await client.post(payment_url, json=payment_payload)
        if payment_resp.status_code != 200:
            raise HTTPException(status_code=502, detail="Error en servicio de pagos")
        payment_data = payment_resp.json()

    # 6️⃣ Limpiar carrito si pago exitoso
    for item in cart_items:
        db.delete(item)
    db.commit()
    logger.info(f"Carrito eliminado para usuario {current_user.id} después de pago exitoso")

    return {
        "message": "Pago realizado exitosamente",
        "total": total_cart,
        "payment_response": payment_data
    }
