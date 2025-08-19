from fastapi import APIRouter

from .products.views import router as products_router
from .demo_auth.demo_jwt_auth import router as demo_jwt_auth_router


router = APIRouter()
router.include_router(router=products_router, prefix="/products")
router.include_router(router=demo_jwt_auth_router, prefix="/demo-auth")
