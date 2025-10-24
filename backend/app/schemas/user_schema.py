from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from uuid import UUID
import re

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=100)

class UserCreate(UserBase):
    password: str 
    is_admin: bool = False

    @field_validator("password")
    def password_complexity(cls, v: str) -> str:
        """
        Valida que la contraseña cumpla:
        - Mínimo 8 caracteres
        - Al menos 1 letra mayúscula
        - Al menos 1 letra minúscula
        - Al menos 1 número
        - Al menos 1 símbolo especial
        """
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        if not re.search(r"[A-Z]", v):
            raise ValueError("La contraseña debe contener al menos una letra mayúscula")
        if not re.search(r"[a-z]", v):
            raise ValueError("La contraseña debe contener al menos una letra minúscula")
        if not re.search(r"\d", v):
            raise ValueError("La contraseña debe contener al menos un número")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("La contraseña debe contener al menos un símbolo especial")
        return v

class UserOut(UserBase):
    user_uuid: UUID
    is_admin: bool

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    user_uuid: str
    full_name: str
    email: str

    class Config:
        from_attributes = True
