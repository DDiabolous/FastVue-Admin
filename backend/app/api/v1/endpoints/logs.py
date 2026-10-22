from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_db, require
from app.core.responses import ok
from app.schemas.common import Envelope, Page
from app.schemas.logs import LogQuery, LogRead
from app.services.audit import AuditService

router = APIRouter(prefix='/logs', tags=['v1 · 审计'])


@router.get('', response_model=Envelope[Page[LogRead]])
async def logs(
    query: Annotated[LogQuery, Query()],
    principal=Depends(require('system:logs:read')),
    db=Depends(get_db),
):
    return ok(
        await AuditService().list(db, query.page, query.pageSize, query.keyword, query.category)
    )
