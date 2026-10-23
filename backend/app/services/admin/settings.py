from app.core.errors import AppError
from app.repositories.admin.settings import SettingsRepository

from app.services.admin.audit import audit
from app.services.admin.base import non_null
from app.services.admin.presenters import fields


class SettingsService:
    repository = SettingsRepository()
    public_fields = ['siteName', 'description', 'contactEmail', 'registration']

    async def get(self, db, public=False):
        row = await self.repository.current(db)
        if not row:
            raise AppError(503, '请先初始化数据库')
        return fields(row, ['siteName', 'description'] if public else self.public_fields)

    async def update(self, db, context, data):
        row = await self.repository.current(db)
        if not row:
            raise AppError(503, '请先初始化数据库')
        await self.repository.update(db, row, non_null(data))
        audit(db, context, '更新系统配置', '系统配置')
        result = fields(row, self.public_fields)
        await db.commit()
        return result
