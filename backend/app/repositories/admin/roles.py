from sqlalchemy import select

from app.models.admin.roles import AdminRole

from app.repositories.base import Repository


class AdminRoleRepository(Repository):
    model = AdminRole
    search_fields = ('roleKey', 'roleName', 'description')

    async def by_key(self, db, key):
        return await db.scalar(select(AdminRole).where(AdminRole.roleKey == key))

    async def by_keys(self, db, keys):
        return (await db.scalars(select(AdminRole).where(AdminRole.roleKey.in_(keys)))).all()

    async def enabled(self, db):
        return (
            await db.scalars(
                select(AdminRole).where(AdminRole.status == 1).order_by(AdminRole.roleKey)
            )
        ).all()
