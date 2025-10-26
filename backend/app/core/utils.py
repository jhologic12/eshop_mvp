# backend/app/core/utils.py
from passlib.context import CryptContext
from cloudinary.uploader import upload

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)



def upload_image_to_cloudinary(file):
    """
    file: archivo recibido de FastAPI UploadFile
    Retorna: URL pública de la imagen
    """
    result = upload(file.file, folder="products")  # sube a carpeta 'products'
    return result["secure_url"]