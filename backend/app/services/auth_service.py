# backend/app/services/auth_service.py
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user_schema import UserCreate
from app.core.security import get_password_hash, verify_password
from datetime import timedelta
from app.core.security import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

def create_user(db: Session, user_in: UserCreate) -> User:
    user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=get_password_hash(user_in.password),
        is_admin=getattr(user_in, "is_admin", False)  # guardar permisos de admin
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if user and verify_password(password, user.hashed_password):
        return user
    return None

def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()



def login_user(db: Session, email: str, password: str):
    """
    Autentica un usuario y genera un token JWT.
    """
    user = authenticate_user(db, email, password)
    if not user:
        return None

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    token_data = {
        "sub": user.email,
        "is_admin": user.is_admin  # 👈 Incluir el rol en el token
    }

    access_token = create_access_token(
        data=token_data,
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }