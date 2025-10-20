from sqlalchemy.orm import Session
from typing import List
from app.models.product import Product
from app.schemas.product_schema import ProductCreate

def list_products(db: Session) -> List[Product]:
    return db.query(Product).all()

def create_product(db: Session, product_in: ProductCreate) -> Product:
    product = Product(**product_in.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product
