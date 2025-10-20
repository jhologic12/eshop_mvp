from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.cart import CartItem
from app.models.product import Product
from fastapi import HTTPException

def add_to_cart(user_uuid: str, product_uuid: str, quantity: int, price: float, db: Session):
    """Agrega o actualiza un producto en el carrito."""
    item = db.query(CartItem).filter(
        CartItem.user_uuid == user_uuid,
        CartItem.product_uuid == product_uuid
    ).first()
    
    if item:
        item.quantity += quantity
    else:
        item = CartItem(
            user_uuid=user_uuid,
            product_uuid=product_uuid,
            quantity=quantity,
            price=price
        )
        db.add(item)
    
    db.commit()

def list_cart_items(user_uuid: str, db: Session):
    return db.query(CartItem).filter(CartItem.user_uuid == user_uuid).all()

def update_cart_item_quantity(user_uuid: str, product_uuid: str, quantity: int, db: Session):
    item = db.query(CartItem).filter(
        CartItem.user_uuid == user_uuid,
        CartItem.product_uuid == product_uuid
    ).first()
    if item:
        item.quantity = quantity
        db.commit()

def remove_cart_item(user_uuid: str, product_uuid: str, db: Session):
    db.query(CartItem).filter(
        CartItem.user_uuid == user_uuid,
        CartItem.product_uuid == product_uuid
    ).delete()
    db.commit()

def get_cart_total(user_uuid: str, db: Session) -> float:
    """
    Calcula el total del carrito del usuario sumando (precio * cantidad) de cada producto.
    """
    items = db.query(CartItem).filter(CartItem.user_uuid == user_uuid).all()
    if not items:
        return 0.0

    total = 0.0
    for item in items:
        product = db.query(Product).filter(Product.uuid == item.product_uuid).first()
        if product:
            total += product.price * item.quantity
        else:
            raise HTTPException(
                status_code=404, 
                detail=f"Producto con UUID {item.product_uuid} no encontrado"
            )

    return round(total, 2)

def clear_cart(user_uuid: str, db: Session) -> None:
    """
    Elimina todos los items del carrito del usuario una vez realizado el pago.
    """
    items = db.query(CartItem).filter(CartItem.user_uuid == user_uuid).all()
    for item in items:
        db.delete(item)
    db.commit()



def get_cart_items(user_uuid: str, db: Session):
    """
    Devuelve los items del carrito listos para PaymentResponse.items.
    """
    items = db.query(CartItem).filter(CartItem.user_uuid == user_uuid).all()
    result = []
    for item in items:
        product = db.query(Product).filter(Product.uuid == item.product_uuid).first()
        if product:
            result.append({
                "product_id": product.id,
                "name": product.name,
                "quantity": item.quantity,
                "unit_price": product.price
            })
    return result