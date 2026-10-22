from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request

from app.api.dependencies import audit_context, get_db, require
from app.core.responses import ok
from app.schemas.common import Envelope, Page, PageQuery
from app.schemas.roles import RoleCreate, RoleRead, RoleUpdate
from app.services.roles import RoleService

router = APIRouter(prefix='/roles', tags=['v1 · 角色'])
service = RoleService()


@router.get('', response_model=Envelope[Page[RoleRead]])
async def listing(
    query: Annotated[PageQuery, Query()],
    principal=Depends(require('system:roles:read')),
    db=Depends(get_db),
):
    return ok(await service.list(db, query.page, query.pageSize, query.keyword))


@router.post('', response_model=Envelope[None])
async def create(
    body: RoleCreate,
    request: Request,
    principal=Depends(require('system:roles:create')),
    db=Depends(get_db),
):
    await service.create(db, principal, audit_context(request, principal), body.model_dump())
    return ok()


@router.patch('/{id}', response_model=Envelope[None])
async def update(
    id: str,
    body: RoleUpdate,
    request: Request,
    principal=Depends(require('system:roles:update')),
    db=Depends(get_db),
):
    await service.update(
        db, principal, audit_context(request, principal), id, body.model_dump(exclude_unset=True)
    )
    return ok()


@router.delete('/{id}', response_model=Envelope[None])
async def remove(
    id: str, request: Request, principal=Depends(require('system:roles:delete')), db=Depends(get_db)
):
    await service.delete(db, principal, audit_context(request, principal), id)
    return ok()
