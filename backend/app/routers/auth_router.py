from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.user_schema import UserCreate, UserOut, UserLogin , TokenResponse
from app.models.user import User
from app.core.database import get_db
from app.core.security import get_password_hash, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta
from pydantic import BaseModel 

router = APIRouter(prefix="/auth", tags=["Auth"])

# -------------------------------
# Register
# -------------------------------
@router.post("/register", response_model=UserOut)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    # Verifica si el usuario ya existe
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email ya registrado")

    # Crear usuario con contraseña hasheada
    new_user = User(
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=get_password_hash(payload.password),
        is_admin=payload.is_admin
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# -------------------------------
# Login
# -------------------------------
@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    # Buscar usuario
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Credenciales incorrectas"
        )

    # Generar token JWT con email y rol
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.email,       # 👈 email como identificador
            "is_admin": user.is_admin  # 👈 incluir rol admin
        },
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}