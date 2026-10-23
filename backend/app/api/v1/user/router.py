from fastapi import APIRouter

from . import auth, profile

router = APIRouter(prefix='/user')
router.include_router(auth.router)
router.include_router(profile.router)
