from fastapi import APIRouter

from .admin.router import router as admin_router
from .user.router import router as user_router

router = APIRouter(prefix='/v1')
router.include_router(admin_router)
router.include_router(user_router)
