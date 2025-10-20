from fastapi import APIRouter
from app.routers import auth_router, product_router, cart_router, payment_router, checkout_router

router = APIRouter()

# ✅ Incluye directamente los routers (sin .router)
router.include_router(auth_router)
router.include_router(product_router)
router.include_router(cart_router)
router.include_router(payment_router)
router.include_router(checkout_router)
