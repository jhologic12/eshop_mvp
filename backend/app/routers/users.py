from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.schemas.user_schema import UserCreate, UserOut
from app.services import user_service
from app.core.dependencies import get_db, get_current_admin_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/", response_model=List[UserOut])
def list_all_users(db: Session = Depends(get_db), current_user = Depends(get_current_admin_user)):
    return user_service.list_users(db)

@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_new_user(user_in: UserCreate, db: Session = Depends(get_db), current_user = Depends(get_current_admin_user)):
    if user_service.get_user_by_email(db, user_in.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    return user_service.create_user(db, user_in)
