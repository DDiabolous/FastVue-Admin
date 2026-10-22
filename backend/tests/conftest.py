import os
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text

from app.cli import initialize
from app.core.config import Settings
from app.main import create_app


@pytest.fixture
async def app():
    url = os.environ.get('TEST_DATABASE_URL')
    if not url:
        pytest.skip('Set TEST_DATABASE_URL to a dedicated PostgreSQL test database')
    # Test isolation uses a random schema and never truncates shared/public tables.
    import uuid
    from sqlalchemy.ext.asyncio import create_async_engine

    schema = 'test_' + uuid.uuid4().hex
    admin_engine = create_async_engine(url)
    async with admin_engine.begin() as connection:
        await connection.execute(text(f'CREATE SCHEMA "{schema}"'))
    config = Settings(database_url=url, login_limit=100)
    instance = create_app(config)
    await instance.state.engine.dispose()
    engine = create_async_engine(url, connect_args={'server_settings': {'search_path': schema}})
    from sqlalchemy.ext.asyncio import async_sessionmaker

    instance.state.engine = engine
    instance.state.sessions = async_sessionmaker(engine, expire_on_commit=False)
    alembic = Config(str(Path(__file__).resolve().parents[1] / 'alembic.ini'))

    # Run real migrations on the same isolated schema without starting another event loop.
    def migrate(connection):
        alembic.attributes['connection'] = connection
        command.upgrade(alembic, 'head')

    async with engine.begin() as connection:
        await connection.run_sync(migrate)
    await initialize(instance.state.sessions, 'AdminPass123!', demo=True)
    try:
        yield instance
    finally:
        await engine.dispose()
        async with admin_engine.begin() as connection:
            await connection.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
        await admin_engine.dispose()


@pytest.fixture
async def client(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        yield client


async def sign_in(client, username='admin', password='AdminPass123!'):
    response = await client.post(
        '/api/v1/auth/login', json={'username': username, 'password': password}
    )
    assert response.status_code == 200, response.text
    return {'Authorization': 'Bearer ' + response.json()['data']['token']}


@pytest.fixture
async def admin(client):
    return await sign_in(client)
