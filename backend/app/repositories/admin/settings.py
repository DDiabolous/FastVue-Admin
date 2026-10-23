from app.models.admin.settings import SystemSettings

from app.repositories.base import Repository


class SettingsRepository(Repository):
    model = SystemSettings

    async def current(self, db):
        return await self.get(db, 1)
