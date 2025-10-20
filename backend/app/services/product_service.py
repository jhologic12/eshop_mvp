import base64
from io import BytesIO
from pathlib import Path
from PIL import Image
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from uuid import uuid4
from fastapi import HTTPException
import logging

from app.models.product import Product
from app.models.cart import CartItem
from app.schemas.product_schema import ProductCreate, ProductUpdate
from app.core.logger import logger

# Evita redefinir logger
logger = logging.getLogger("eshop_logger")

# -------------------------
# Manejo de imágenes
# -------------------------
IMAGE_SIZES = {
    "small": (100, 100),
    "thumbnail": (200, 200),
    "medium": (800, 800)
}


def save_product_images(base64_image: str, product_uuid: str) -> Dict[str, str]:
    """Genera todas las versiones de la imagen y devuelve sus URLs."""
    base_path = Path("static/products")
    base_path.mkdir(parents=True, exist_ok=True)

    image_data = base64.b64decode(base64_image)
    image = Image.open(BytesIO(image_data)).convert("RGB")

    image_paths = {}
    for size_name, size in IMAGE_SIZES.items():
        img_copy = image.copy()
        img_copy.thumbnail(size)
        path = base_path / f"{product_uuid}_{size_name}.webp"
        img_copy.save(path, format="WEBP", quality=80, optimize=True)
        image_paths[size_name] = f"/static/products/{product_uuid}_{size_name}.webp"

    return image_paths


def _process_product_image(db: Session, product: Product, base64_image: str):
    """Procesa y guarda las versiones de imagen para un producto."""
    image_paths = save_product_images(base64_image, product.uuid)
    product.image_small = image_paths["small"]
    product.image_thumbnail = image_paths["thumbnail"]
    product.image_medium = image_paths["medium"]
    product.images = image_paths

    db.commit()
    db.refresh(product)


# -------------------------
# CRUD Productos
# -------------------------
def create_product(db: Session, product_in: ProductCreate) -> Product:
    product = Product(
        uuid=str(uuid4()),
        name=product_in.name,
        description=product_in.description,
        price=product_in.price,
        stock=product_in.stock,
        is_active=product_in.is_active if product_in.is_active is not None else True,
        image_small=None,
        image_thumbnail=None,
        image_medium=None
    )
    db.add(product)
    db.commit()
    db.refresh(product)

    # Guardar imagen base64 o asignar URL
    if getattr(product_in, "image_base64", None):
        _process_product_image(db, product, product_in.image_base64)
    elif getattr(product_in, "image_url", None):
        product.image_small = product_in.image_url
        product.image_thumbnail = product_in.image_url
        product.image_medium = product_in.image_url
        db.commit()
        db.refresh(product)

    return product


def get_all_products(db: Session) -> List[Product]:
    return db.query(Product).filter(Product.is_active == True).all()


def get_product_by_id(db: Session, product_uuid: str) -> Optional[Product]:
    return db.query(Product).filter(Product.uuid == product_uuid).first()


def update_product(db: Session, product_uuid: str, product_in: ProductUpdate) -> Product:
    product = get_product_by_id(db, product_uuid)
    if not product:
        raise ValueError(f"Producto con UUID {product_uuid} no encontrado")

    for field, value in product_in.dict(exclude_unset=True).items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, product_uuid: str):
    product = get_product_by_id(db, product_uuid)
    if not product:
        raise ValueError(f"Producto con UUID {product_uuid} no encontrado")

    product.is_active = False
    db.commit()
    db.refresh(product)
    return {"message": f"Producto {product_uuid} eliminado correctamente"}


# -------------------------
# Actualizar stock tras compra
# -------------------------
def update_stock_after_purchase(db: Session, user_id: str):
    """
    Reduce el stock de los productos comprados en el carrito del usuario.
    Verifica que haya suficiente stock antes de descontar.
    """
    cart_items = db.query(CartItem).filter(CartItem.user_id == user_id).all()
    if not cart_items:
        logger.warning(f"No hay items en el carrito del usuario {user_id} para actualizar stock")
        return

    for item in cart_items:
        product = db.query(Product).filter(Product.uuid == item.product_id).first()
        if not product:
            logger.error(f"Producto con UUID {item.product_id} no encontrado")
            raise HTTPException(status_code=404, detail=f"Producto {item.product_id} no encontrado")

        if product.stock < item.quantity:
            logger.warning(
                f"Stock insuficiente para {product.name} "
                f"(Disponible: {product.stock}, solicitado: {item.quantity})"
            )
            raise HTTPException(
                status_code=400,
                detail=f"Stock insuficiente para {product.name}. Disponible: {product.stock}"
            )

        product.stock -= item.quantity
        logger.info(f"Stock actualizado para {product.name}: ahora {product.stock} unidades")

    db.commit()
    logger.info(f"Stock actualizado correctamente para usuario {user_id}")
