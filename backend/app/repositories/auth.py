from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert

from app.models.auth import LoginBucket, Session
from app.models.users import User


class SessionRepository:
    async def get(self, db, digest):
        return await db.get(Session, digest)

    def add(self, db, digest, user_id, expires_at, ip='127.0.0.1', user_agent=''):
        from app.db.base import utcnow

        db.add(
            Session(
                token_hash=digest,
                user_id=user_id,
                expires_at=expires_at,
                created_at=utcnow(),
                ip=ip or '127.0.0.1',
                user_agent=user_agent[:255] if user_agent else '',
            )
        )

    async def list_user_sessions(self, db, user_id, now):
        stmt = select(Session).where(Session.user_id == user_id, Session.expires_at > now)
        return (await db.scalars(stmt)).all()

    async def revoke(self, db, digest):
        await db.execute(delete(Session).where(Session.token_hash == digest))

    async def revoke_user(self, db, user_id):
        await db.execute(delete(Session).where(Session.user_id == user_id))

    async def revoke_role(self, db, role_key):
        await db.execute(
            delete(Session).where(Session.user_id.in_(select(User.id).where(User.role == role_key)))
        )


class LoginRepository:
    async def bucket(self, db, key, now):
        await db.execute(
            insert(LoginBucket).values(key=key, started_at=now, attempts=0).on_conflict_do_nothing()
        )
        return await db.get(LoginBucket, key)
