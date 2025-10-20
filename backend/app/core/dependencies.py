# backend/app/core/dependencies.py
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer
from app.models.user import User
from app.core.database import get_db
from app.services.auth_service import get_user_by_email

security = HTTPBearer()  # Para extraer token JWT de la cabecera Authorization


def get_current_user(db: Session = Depends(get_db), token: str = Depends(security)) -> User:
    """
    Devuelve el usuario autenticado a partir del token JWT.
    Levanta 401 si el token es inválido o el usuario no existe.
    """
    from app.core.security import decode_access_token

    payload = decode_access_token(token.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    email = payload.get("sub")
    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user


def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Devuelve el usuario si es admin.
    Levanta 403 si el usuario no es administrador.
    """
    if not getattr(current_user, "is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    return current_user


def get_user_or_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Devuelve cualquier usuario autenticado (normal o admin).
    Útil para endpoints donde ambos tipos de usuario pueden operar.
    """
    return current_user
