from fastapi import APIRouter

from .admin.router import router as admin_router
from .app.router import router as app_router

router = APIRouter(prefix='/v1')
router.include_router(admin_router)
router.include_router(app_router)
