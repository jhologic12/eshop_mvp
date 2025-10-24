# app/routers/cart_router.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.product import Product
from app.models.cart import CartItem
from app.schemas.cart_schema import CartItemCreate, CartItemDetail, CartItemResponse

router = APIRouter(prefix="/cart", tags=["Cart"])

# -------------------------------------
# 🔹 Agregar producto al carrito
# -------------------------------------
@router.post("/add", response_model=CartItemDetail)
def add_to_cart_endpoint(
    item: CartItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Buscar producto
    product = db.query(Product).filter(Product.uuid == item.product_uuid).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    # Buscar item existente en carrito
    cart_item = db.query(CartItem).filter(
        CartItem.user_uuid == current_user.user_uuid,
        CartItem.product_uuid == item.product_uuid
    ).first()
    
    if cart_item:
        cart_item.quantity += item.quantity
    else:
        cart_item = CartItem(
            user_uuid=current_user.user_uuid,
            product_uuid=product.uuid,
            quantity=item.quantity
        )
        db.add(cart_item)
    
    db.commit()
    db.refresh(cart_item)
    
    return CartItemDetail(
        id=cart_item.cart_item_uuid,
        product_uuid=product.uuid,
        product_name=product.name,
        quantity=cart_item.quantity,
        price=product.price,
        total_price=product.price * cart_item.quantity
    )

# -------------------------------------
# 🔹 Listar productos del carrito
# -------------------------------------
@router.get("/list", response_model=list[CartItemResponse])
def list_cart_items_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items = db.query(CartItem).filter(CartItem.user_uuid == current_user.user_uuid).all()
    return [
        {
            "product_id": item.product_uuid,
            "name": item.product.name,
            "price": item.product.price,
            "quantity": item.quantity,
            "subtotal": item.product.price * item.quantity,
           "image_url": item.product.image_thumbnail,  # <--- aquí usamos el campo existente
        }
        for item in items
    ]


# -------------------------------------
# 🔹 Actualizar cantidad
# -------------------------------------
# 🔹 Actualizar cantidad usando product_uuid
# Actualizar cantidad de un item usando product_uuid
@router.put("/update/{product_uuid}", response_model=dict)
def update_cart_item_quantity_endpoint(
    product_uuid: str,  # <-- antes era product_id: int
    quantity: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Buscar item en carrito
    item = (
        db.query(CartItem)
        .filter(CartItem.user_uuid == current_user.user_uuid,
                CartItem.product_uuid == product_uuid)
        .first()
    )

    if not item:
        raise HTTPException(status_code=404, detail="El producto no está en el carrito")

    product = db.query(Product).filter(Product.uuid == product_uuid).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    if product.stock < quantity:
        raise HTTPException(status_code=400, detail="Stock insuficiente")

    item.quantity = quantity
    db.commit()
    return {"message": "Cantidad actualizada correctamente"}


# -------------------------------------
# 🔹 Eliminar producto
# -------------------------------------
@router.delete("/remove/{product_uuid}", response_model=dict)
def remove_cart_item_endpoint(
    product_uuid: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = db.query(CartItem).filter(
        CartItem.user_uuid == current_user.user_uuid,
        CartItem.product_uuid == product_uuid
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="El producto no está en el carrito")
    
    db.delete(item)
    db.commit()
    
    return {"message": "Producto eliminado del carrito"}

# -------------------------------------
# 🔹 Vaciar carrito
# -------------------------------------
@router.delete("/clear", response_model=dict)
def clear_cart_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db.query(CartItem).filter(CartItem.user_uuid == current_user.user_uuid).delete()
    db.commit()
    
    return {"message": "Carrito vaciado correctamente"}

# -------------------------------------
# 🔹 Calcular total del carrito
# -------------------------------------
@router.get("/total", response_model=dict)
def get_cart_total_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items = db.query(CartItem).filter(CartItem.user_uuid == current_user.user_uuid).all()
    total = sum(item.product.price * item.quantity for item in items)
    return {"total": total}
