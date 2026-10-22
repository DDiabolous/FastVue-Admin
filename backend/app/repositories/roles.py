from sqlalchemy import select

from app.models.roles import Role

from .base import Repository


class RoleRepository(Repository):
    model = Role
    search_fields = ('roleKey', 'roleName', 'description')

    async def by_key(self, db, key):
        return await db.scalar(select(Role).where(Role.roleKey == key))

    async def by_keys(self, db, keys):
        return (await db.scalars(select(Role).where(Role.roleKey.in_(keys)))).all()

    async def enabled(self, db):
        return (await db.scalars(select(Role).where(Role.status == 1).order_by(Role.roleKey))).all()
