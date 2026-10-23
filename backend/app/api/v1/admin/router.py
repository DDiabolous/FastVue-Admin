from fastapi import APIRouter

from . import auth, accounts, roles, dictionary, settings, logs, profile

router = APIRouter(prefix='/admin')
for module in (auth, accounts, roles, dictionary, settings, logs, profile):
    router.include_router(module.router)
