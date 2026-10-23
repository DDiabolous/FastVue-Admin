from sqlalchemy import select

from app.models.admin.accounts import AdminAccount

from app.repositories.base import Repository


class AdminAccountRepository(Repository):
    model = AdminAccount
    search_fields = ('username', 'realName', 'email', 'role')

    async def by_username(self, db, username):
        return await db.scalar(select(AdminAccount).where(AdminAccount.username == username))

    async def role_is_bound(self, db, key):
        return (
            await db.scalar(select(AdminAccount.id).where(AdminAccount.role == key).limit(1))
            is not None
        )
