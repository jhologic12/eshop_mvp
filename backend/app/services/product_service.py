import base64
import io
import os
import logging
from typing import List, Optional, Dict
from uuid import uuid4
from PIL import Image
from sqlalchemy.orm import Session
from fastapi import HTTPException
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

from app.models.product import Product
from app.models.cart import CartItem
from app.schemas.product_schema import ProductCreate, ProductUpdate
from app.core.logger import logger

load_dotenv()  # Cargar variables de entorno desde .env

# Evita redefinir logger
logger = logging.getLogger("eshop_logger")

# Inicializar Cloudinary con variables de entorno
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

# -------------------------
# Tamaños de imagen
# -------------------------
IMAGE_SIZES = {
    "small": (100, 100),
    "thumbnail": (200, 200),
    "medium": (800, 800)
}

# -------------------------
# Guardar imagenes en Cloudinary
# -------------------------
def save_product_images_cloudinary(base64_image: str, product_id: str) -> Dict[str, str]:
    """
    Convierte base64 en imagen, genera los tamaños y sube a Cloudinary.
    Devuelve URLs.
    """
    image_data = base64.b64decode(base64_image)
    image = Image.open(io.BytesIO(image_data)).convert("RGB")

    urls = {}
    for size_name, size in IMAGE_SIZES.items():
        img_copy = image.copy()
        img_copy.thumbnail(size)

        img_bytes = io.BytesIO()
        img_copy.save(img_bytes, format="WEBP", quality=80, optimize=True)
        img_bytes.seek(0)

        result = cloudinary.uploader.upload(
            img_bytes,
            folder="products",
            public_id=f"{product_id}_{size_name}",
            format="webp",
            overwrite=True
        )
        urls[size_name] = result["secure_url"]

    return urls

def _process_product_image(db: Session, product: Product, base64_image: str):
    """Procesa y sube imágenes a Cloudinary para un producto."""
    image_urls = save_product_images_cloudinary(base64_image, str(product.id))
    product.image_small = image_urls["small"]
    product.image_thumbnail = image_urls["thumbnail"]
    product.image_medium = image_urls["medium"]

    db.commit()
    db.refresh(product)

# -------------------------
# CRUD Productos
# -------------------------
def create_product(db: Session, product_in: ProductCreate) -> Product:
    product = Product(
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

def get_product_by_id(db: Session, product_id: str) -> Optional[Product]:
    return db.query(Product).filter(Product.id == product_id).first()

def update_product(db: Session, product_id: str, product_in: ProductUpdate) -> Product:
    product = get_product_by_id(db, product_id)
    if not product:
        raise ValueError(f"Producto con ID {product_id} no encontrado")

    for field, value in product_in.dict(exclude_unset=True).items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return product

def delete_product(db: Session, product_id: str):
    product = get_product_by_id(db, product_id)
    if not product:
        raise ValueError(f"Producto con ID {product_id} no encontrado")

    product.is_active = False
    db.commit()
    db.refresh(product)
    return {"message": f"Producto {product_id} eliminado correctamente"}

# -------------------------
# Actualizar stock tras compra
# -------------------------
def update_stock_after_purchase(db: Session, user_id: str):
    cart_items = db.query(CartItem).filter(CartItem.user_id == user_id).all()
    if not cart_items:
        logger.warning(f"No hay items en el carrito del usuario {user_id} para actualizar stock")
        return

    for item in cart_items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            logger.error(f"Producto con ID {item.product_id} no encontrado")
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
