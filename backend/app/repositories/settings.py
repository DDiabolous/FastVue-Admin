from app.models.settings import SystemSettings

from .base import Repository


class SettingsRepository(Repository):
    model = SystemSettings

    async def current(self, db):
        return await self.get(db, 1)
