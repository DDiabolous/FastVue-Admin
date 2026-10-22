from fastapi import APIRouter

from .endpoints import auth, dictionary, logs, roles, settings, users

router = APIRouter(prefix='/v1')
for module in (auth, users, roles, dictionary, settings, logs):
    router.include_router(module.router)
