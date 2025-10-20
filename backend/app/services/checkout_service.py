from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.services.cart_service import get_cart_total, clear_cart, list_cart_items
from app.models.user import User
from app.models.product import Product
import requests
from app.schemas.payment_schema import PurchasedProduct
from app.models.cart import CartItem

MOCK_PAYMENT_URL = "http://127.0.0.1:8001"


def process_checkout(user: User, card_data: dict, db: Session):
    """
    Procesa el flujo completo del pago:
    1️⃣ Valida la tarjeta.
    2️⃣ Calcula el total del carrito.
    3️⃣ Llama al mock de pago.
    4️⃣ Devuelve los productos comprados.
    5️⃣ Limpia el carrito si fue exitoso.
    """

    # 1️⃣ Validar tarjeta
    validate_response = requests.post(f"{MOCK_PAYMENT_URL}/cards/validate", json=card_data)
    if validate_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Error al validar la tarjeta")

    card_info = validate_response.json()
    account_uuid = card_info.get("account_uuid")
    if not account_uuid:
        raise HTTPException(status_code=400, detail="No se recibió account_uuid del servicio de tarjeta")

    # 2️⃣ Obtener total del carrito
    total = get_cart_total(user_uuid=user.user_uuid, db=db)
    if total <= 0:
        raise HTTPException(status_code=400, detail="El carrito está vacío o el total es inválido")

    # 3️⃣ Preparar payload para /payments
    payload = {
        "account_uuid": account_uuid,
        "amount": total,
        "description": "Compra en eShop"
    }

    print("Payload que se enviará a /payments:", payload)  # 🔹 depuración

    payment_response = requests.post(f"{MOCK_PAYMENT_URL}/payments/", json=payload)
    if payment_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Error procesando el pago")

    data = payment_response.json()
    if data.get("status") != "aprobado":
        raise HTTPException(status_code=400, detail="Pago rechazado")

   # 4️⃣ Limpiar carrito tras pago exitoso
    cart_items = db.query(CartItem).filter(CartItem.user_uuid == user.user_uuid).all()
    purchased_items = []
    
    for item in cart_items:
        product = db.query(Product).filter(Product.uuid == item.product_uuid).first()
        if product:
            purchased_items.append(
                PurchasedProduct(
                    product_id=product.uuid,
                    product_name=product.name,
                    quantity=item.quantity,
                    price=product.price,
                    subtotal=round(product.price * item.quantity, 2)
                )
            )

    clear_cart(user_uuid=user.user_uuid, db=db)

    return {
        "message": "Pago procesado exitosamente",
        "total": total,
        "items": purchased_items
    }