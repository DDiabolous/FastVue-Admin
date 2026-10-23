from app.models.admin.audit import AuditLog

from app.repositories.base import Repository


class AuditRepository(Repository):
    model = AuditLog
    search_fields = ('operator', 'action', 'target', 'ip')

    def ordering(self):
        return [AuditLog.time.desc(), AuditLog.id]

    def append(self, db, data):
        db.add(AuditLog(**data))

    async def list_category(self, db, page, page_size, keyword, category):
        conditions = [AuditLog.category == category] if category else []
        return await self.list(db, page, page_size, keyword, conditions)
