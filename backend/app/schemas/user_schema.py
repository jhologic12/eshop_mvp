# backend/app/schemas/user_schema.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=100)

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    is_admin: bool = False

class UserOut(UserBase):
    user_uuid: UUID  # en lugar de id
    is_admin: bool

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str



    # --- Esquema de respuesta para login/token ---
class TokenResponse(BaseModel):
    access_token: str
    token_type: str



class UserResponse(BaseModel):
    user_uuid: str  #  coincide con tu modelo User
    full_name: str
    email: str

    class Config:
        from_attributes = True