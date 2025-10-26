# backend/migrate_images_to_cloudinary.py
import os
from pathlib import Path
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

# Importar modelos y DB desde app
from app.core.database import SessionLocal
from app.models import Product  # ajusta según tu modelo real

# Cargar variables de entorno
load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)

# Subiendo un nivel desde __file__ para llegar a backend/
IMAGES_PATH = Path(__file__).parent.parent / "static" / "products"


def migrate_images():
    print(f"Buscando imágenes en {IMAGES_PATH}...")

    image_files = list(IMAGES_PATH.glob("*.webp"))
    print(f"Archivos encontrados: {image_files}")

    db = SessionLocal()

    for file_path in image_files:
        filename = file_path.stem  # elimina extensión
        product_uuid = filename.split("_")[0]  # si tu archivo tiene formato uuid_size

        product = db.query(Product).filter(Product.uuid == product_uuid).first()
        if not product:
            print(f"Producto con UUID {product_uuid} no encontrado en DB, saltando...")
            continue

        size = "original"
        if "_small" in filename:
            size = "small"
        elif "_medium" in filename:
            size = "medium"
        elif "_thumbnail" in filename:
            size = "thumbnail"

        try:
            upload_result = cloudinary.uploader.upload(str(file_path), folder="products")
            url = upload_result.get("secure_url")
            setattr(product, f"url_{size}", url)
            db.commit()
            print(f"Producto {product_uuid} actualizado con URL de Cloudinary ({size}) ✅")
        except Exception as e:
            print(f"Error subiendo {file_path.name}: {e}")

    db.close()
    print("Migración completada ✅")

if __name__ == "__main__":
    migrate_images()
