from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.payment_attempt import PaymentAttempt
from app.core.dependencies import get_current_user, get_current_admin_user

router = APIRouter(prefix="/payment-attempts", tags=["Payment Attempts"])

@router.get("/", response_model=List[dict])
def list_payment_attempts(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),  # Usuario autenticado
    user_id: Optional[str] = Query(None, description="Filtrar por user_id"),
    success: Optional[bool] = Query(None, description="Filtrar por éxito/fallo")
):
    # 🔹 Si el usuario no es admin, solo puede ver sus propios intentos
    if not getattr(current_user, "is_admin", False):
        user_id = current_user.id

    query = db.query(PaymentAttempt)

    if user_id:
        query = query.filter(PaymentAttempt.user_id == user_id)
    if success is not None:
        query = query.filter(PaymentAttempt.success == success)

    results = query.order_by(PaymentAttempt.created_at.desc()).all()

    # Transformamos los resultados en diccionario evitando datos sensibles
    return [
        {
            "attempt_uuid": r.attempt_uuid,
            "user_id": r.user_id,
            "amount": r.amount,
            "success": r.success,
            "reason": r.reason,
            "created_at": r.created_at
        }
        for r in results
    ]
