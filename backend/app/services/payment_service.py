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
async def checkout_payment(
    payment_in: PaymentRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # 1️⃣ Obtener items del carrito
    cart_items = db.query(CartItem).filter(CartItem.user_id == current_user.id).all()
    if not cart_items:
        raise HTTPException(status_code=400, detail="Carrito vacío")

    # 2️⃣ Filtrar y ajustar cantidades según stock
    items_to_purchase = []
    adjusted_items = []
    for item in cart_items:
        available_stock = item.product.stock
        if available_stock <= 0:
            adjusted_items.append(f"{item.product.name} (sin stock)")
            continue
        purchase_qty = min(item.quantity, available_stock)
        if purchase_qty < item.quantity:
            adjusted_items.append(f"{item.product.name} (ajustado a {purchase_qty})")
        items_to_purchase.append((item, purchase_qty))

    if not items_to_purchase:
        raise HTTPException(status_code=400, detail="No hay productos disponibles para comprar")

    # 3️⃣ Calcular total según cantidades ajustadas
    total_cart = sum(item.product.price * qty for item, qty in items_to_purchase)
    logger.info(f"Usuario {current_user.id} inicia checkout con monto {total_cart}")

    # 4️⃣ Validar tarjeta en mock externo
    card_payload = {
        "card_number": payment_in.card_number,
        "holder_name": payment_in.holder_name,
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

    # 5️⃣ Ejecutar pago y actualizar stock de forma segura
    try:
        payment_payload = {
            "account_uuid": account_uuid,
            "amount": total_cart,
            "description": "Compra de productos en eShop"
        }

        async with httpx.AsyncClient() as client:
            payment_resp = await client.post(payment_url, json=payment_payload)
            if payment_resp.status_code != 200:
                raise HTTPException(status_code=502, detail="Error en servicio de pagos")
            payment_data = payment_resp.json()

        # 6️⃣ Actualizar stock y limpiar solo los productos comprados
        for item, qty in items_to_purchase:
            product = item.product
            # Validar stock suficiente
            if product.stock < qty:
                raise HTTPException(
                    status_code=400,
                    detail=f"Stock insuficiente para {product.name}. Disponible: {product.stock}, solicitado: {qty}"
        )   
            # Actualizar stock
            product.stock -= qty
            db.add(product)  # Marca el producto como modificado
            db.delete(item)

        db.commit()
        logger.info(f"Carrito actualizado y stock ajustado para usuario {current_user.id}")

    except Exception as e:
        db.rollback()
        logger.error(f"Error procesando checkout: {str(e)}")
        raise HTTPException(status_code=500, detail="Error procesando pago y actualización de stock")

    # 7️⃣ Preparar mensaje final al usuario
    message = "Pago realizado exitosamente."
    if adjusted_items:
        message += " Algunos productos fueron ajustados o no disponibles: " + ", ".join(adjusted_items)

    return {
        "message": message,
        "total": total_cart,
        "payment_response": payment_data
    }
