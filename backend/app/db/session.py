from contextlib import asynccontextmanager

from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


def create_database(url):
    engine = create_async_engine(url, pool_pre_ping=True, hide_parameters=True)
    return engine, async_sessionmaker(engine, expire_on_commit=False)


@asynccontextmanager
async def request_session(sessions, read_only=False):
    async with sessions() as db:
        try:
            # Serialize policy writes against authorization reads; services commit writes.
            lock = 'pg_advisory_xact_lock_shared' if read_only else 'pg_advisory_xact_lock'
            await db.execute(text(f'SELECT {lock}(74192851)'))
            yield db
        except Exception:
            await db.rollback()
            raise
