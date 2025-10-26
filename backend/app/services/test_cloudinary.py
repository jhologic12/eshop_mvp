import os
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv
import os

load_dotenv()  # carga las variables desde .env
# Configura tus credenciales de Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

# Verificación de credenciales
print("cloud_name:", cloudinary.config().cloud_name)
print("api_key:", cloudinary.config().api_key)
print("api_secret:", cloudinary.config().api_secret)

# Ruta de una imagen local para probar
test_image_path = "test_image.jpg"  # asegúrate de tener esta imagen en la misma carpeta

try:
    result = cloudinary.uploader.upload(
        test_image_path,
        folder="products/test"
    )
    print("Subida exitosa ✅")
    print("URL de la imagen:", result["secure_url"])
except Exception as e:
    print("Error al subir la imagen ❌")
    print(e)
