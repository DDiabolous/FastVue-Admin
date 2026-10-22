import asyncio
from unittest.mock import AsyncMock
from types import SimpleNamespace

import pytest
from sqlalchemy import delete, text, update

from app.core.config import Settings
from app.main import create_app
from app.models import SystemSettings, User
from app.core.readiness import DatabaseNotReady


async def test_startup_checks_database_before_serving_and_disposes_on_shutdown(app, monkeypatch):
    dispose = AsyncMock(wraps=app.state.engine.dispose)
    monkeypatch.setattr(app.state, 'engine', SimpleNamespace(dispose=dispose))
    async with app.router.lifespan_context(app):
        dispose.assert_not_called()
    dispose.assert_awaited_once()


@pytest.mark.parametrize('state', ['old_revision', 'missing_settings', 'disabled_admin'])
async def test_startup_refuses_unready_database(app, client, state, monkeypatch):
    async with app.state.sessions() as db, db.begin():
        if state == 'old_revision':
            await db.execute(text("UPDATE alembic_version SET version_num = 'old'"))
        elif state == 'missing_settings':
            await db.execute(delete(SystemSettings))
        else:
            await db.execute(update(User).where(User.builtin.is_(True)).values(status=0))
    assert (await client.get('/api/health')).status_code == 503
    dispose = AsyncMock(wraps=app.state.engine.dispose)
    monkeypatch.setattr(app.state, 'engine', SimpleNamespace(dispose=dispose))
    with pytest.raises(DatabaseNotReady, match='迁移|初始化'):
        async with app.router.lifespan_context(app):
            pytest.fail('An unready application must not start serving requests')
    dispose.assert_awaited_once()


async def test_connection_failure_aborts_startup_without_exposing_credentials():
    app = create_app(
        Settings(
            database_url='postgresql+asyncpg://private-user:private-password@127.0.0.1:1/private-db'
        )
    )
    with pytest.raises(DatabaseNotReady, match='数据库连接失败') as raised:
        async with app.router.lifespan_context(app):
            pytest.fail('Database connection failure must abort startup')
    assert 'private-' not in str(raised.value)
    assert raised.value.__suppress_context__


async def test_startup_timeout_is_bounded_and_disposes_engine(app, monkeypatch):
    from app.core import readiness

    real_timeout = asyncio.timeout
    monkeypatch.setattr(readiness.asyncio, 'timeout', lambda _: real_timeout(0.01))

    class SlowSession:
        async def __aenter__(self):
            await asyncio.sleep(60)

        async def __aexit__(self, *args):
            pass

    monkeypatch.setattr(app.state, 'sessions', SlowSession)
    dispose = AsyncMock(wraps=app.state.engine.dispose)
    monkeypatch.setattr(app.state, 'engine', SimpleNamespace(dispose=dispose))
    with pytest.raises(DatabaseNotReady, match='超时'):
        async with app.router.lifespan_context(app):
            pytest.fail('A timed-out database check must abort startup')
    dispose.assert_awaited_once()
