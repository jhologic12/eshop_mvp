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
    product = db.query(Product).filter(Product.id == item.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    # Buscar item existente en carrito
    cart_item = db.query(CartItem).filter(
        CartItem.user_uuid == current_user.user_uuid,
        CartItem.product_id == product.id
    ).first()
    
    if cart_item:
        cart_item.quantity += item.quantity
    else:
        cart_item = CartItem(
            user_uuid=current_user.user_uuid,
            product_id=product.id,
            quantity=item.quantity
        )
        db.add(cart_item)
    
    db.commit()
    db.refresh(cart_item)
    
    return CartItemDetail(
        id=str(cart_item.cart_item_uuid),                  # ✅ Convertido
        product_id=str(product.id),                        # ✅ Nombre correcto
        product_name=product.name,
        quantity=cart_item.quantity,
        price=product.price,
        total_price=product.price * cart_item.quantity,
        image_url=getattr(product, "image_thumbnail", None)  # ✅ Se incluye
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
            "product_id": str(item.product_id),
            "name": item.product.name,
            "price": item.product.price,
            "quantity": item.quantity,
            "subtotal": item.product.price * item.quantity,
            "image_url": getattr(item.product, "image_thumbnail", None),
        }
        for item in items
    ]

# -------------------------------------
# 🔹 Actualizar cantidad
# -------------------------------------
@router.put("/update/{product_id}", response_model=dict)
def update_cart_item_quantity_endpoint(
    product_id: str,
    quantity: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = db.query(CartItem).filter(
        CartItem.user_uuid == current_user.user_uuid,
        CartItem.product_id == product_id
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="El producto no está en el carrito")

    product = db.query(Product).filter(Product.id == product_id).first()
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
@router.delete("/remove/{product_id}", response_model=dict)
def remove_cart_item_endpoint(
    product_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = db.query(CartItem).filter(
        CartItem.user_uuid == current_user.user_uuid,
        CartItem.product_id == product_id
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="El producto no está en el carrito")
    
    db.delete(item)
    db.commit()
    
    return {"message": "Producto eliminado del carrito"}



# -------------------------------------
# 🔹 Vaciar el carrito completo
# -------------------------------------
@router.delete("/clear", response_model=dict)
def clear_cart_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    deleted = db.query(CartItem).filter(
        CartItem.user_uuid == current_user.user_uuid
    ).delete()

    db.commit()
    return {"message": f"Se eliminaron {deleted} productos del carrito."}


# -------------------------------------
# 🔹 Calcular total del carrito
# -------------------------------------
@router.get("/total", response_model=dict)
def cart_total_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items = db.query(CartItem).filter(
        CartItem.user_uuid == current_user.user_uuid
    ).all()

    total = sum(item.product.price * item.quantity for item in items)

    return {
        "total": total,
        "cantidad_items": len(items)
    }