from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert

from app.models.admin.auth import AdminLoginBucket, AdminSession
from app.models.admin.accounts import AdminAccount


class AdminSessionRepository:
    async def get(self, db, digest):
        return await db.get(AdminSession, digest)

    def add(self, db, digest, user_id, expires_at, ip='127.0.0.1', user_agent=''):
        from app.db.base import utcnow

        db.add(
            AdminSession(
                token_hash=digest,
                user_id=user_id,
                expires_at=expires_at,
                created_at=utcnow(),
                ip=ip or '127.0.0.1',
                user_agent=user_agent[:255] if user_agent else '',
            )
        )

    async def list_user_sessions(self, db, user_id, now):
        stmt = select(AdminSession).where(
            AdminSession.user_id == user_id, AdminSession.expires_at > now
        )
        return (await db.scalars(stmt)).all()

    async def revoke(self, db, digest):
        await db.execute(delete(AdminSession).where(AdminSession.token_hash == digest))

    async def revoke_user(self, db, user_id):
        await db.execute(delete(AdminSession).where(AdminSession.user_id == user_id))

    async def revoke_role(self, db, role_key):
        await db.execute(
            delete(AdminSession).where(
                AdminSession.user_id.in_(
                    select(AdminAccount.id).where(AdminAccount.role == role_key)
                )
            )
        )


class AdminLoginRepository:
    async def bucket(self, db, key, now):
        await db.execute(
            insert(AdminLoginBucket)
            .values(key=key, started_at=now, attempts=0)
            .on_conflict_do_nothing()
        )
        return await db.get(AdminLoginBucket, key)
