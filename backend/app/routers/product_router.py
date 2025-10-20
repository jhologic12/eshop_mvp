from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.product import Product

from app.schemas.product_schema import ProductCreate, ProductUpdate, ProductResponse

from app.services.product_service import (
    create_product,
    get_all_products,
    get_product_by_id,
    update_product,
    delete_product
)
from app.core.dependencies import get_current_admin_user

router = APIRouter(prefix="/products", tags=["Products"])

# -------------------------
# 🔹 Público: Listar productos
# -------------------------
@router.get("/", response_model=List[ProductResponse])
def list_products(db: Session = Depends(get_db)):
    """
    Retorna todos los productos disponibles (público).
    """
    return get_all_products(db)

# -------------------------
# 🔹 Público: Obtener detalle de un producto
# -------------------------
@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: str, db: Session = Depends(get_db)):
    """
    Retorna un producto específico (público).
    """
    product = get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product

# -------------------------
# 🔒 Solo admin: Crear producto
# -------------------------
@router.post("/", response_model=ProductResponse)
def create_product_endpoint(
    product_in: ProductCreate,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin_user)
):
    """
    Crear un nuevo producto (solo admin).
    Maneja base64 o URL de imagen si se envía.
    """
    try:
        product = create_product(db, product_in)
        return product
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -------------------------
# 🔒 Solo admin: Actualizar producto
# -------------------------
@router.put("/{product_id}", response_model=ProductResponse)
def update_product_endpoint(
    product_id: str,
    product: ProductUpdate,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin_user)
):
    """
    Actualiza un producto existente (solo admin).
    """
    existing = get_product_by_id(db, product_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return update_product(db, product_id, product)

# -------------------------
# 🔒 Solo admin: Eliminar producto
# -------------------------
@router.delete("/{product_id}")
def delete_product_endpoint(
    product_id: str,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin_user)
):
    """
    Elimina un producto (solo admin).
    """
    existing = get_product_by_id(db, product_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return delete_product(db, product_id)
