import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException

from alembic.config import Config
from alembic.script import ScriptDirectory

from .api.router import router
from .core.config import get_settings
from .core.errors import register_exception_handlers
from .core.readiness import DatabaseNotReady, check_database
from .db.session import create_database


def create_app(config=None):
    config = config or get_settings()
    engine, sessions = create_database(config.database_url)
    migrations = Config(str(Path(__file__).resolve().parents[1] / 'alembic.ini'))
    expected_revision = ScriptDirectory.from_config(migrations).get_current_head()

    @asynccontextmanager
    async def lifespan(app):
        try:
            await check_database(app, expected_revision)
            logging.getLogger('fastvue').info(
                'Database connection, migrations and initialization verified'
            )
            yield
        finally:
            await app.state.engine.dispose()

    app = FastAPI(title='FastVue-Admin API', version='1.0.0', lifespan=lifespan)
    app.state.config, app.state.engine, app.state.sessions = config, engine, sessions
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origins,
        allow_credentials=False,
        allow_methods=['GET', 'POST', 'PATCH', 'DELETE', 'OPTIONS'],
        allow_headers=['Authorization', 'Content-Type'],
    )

    register_exception_handlers(app)

    @app.get('/api/health', tags=['health'])
    async def health(request: Request):
        try:
            await check_database(request.app, expected_revision)
        except DatabaseNotReady:
            raise HTTPException(503, '数据库不可用或需要迁移、初始化') from None
        return {'code': 200, 'message': 'ok', 'data': {'database': 'postgresql'}}

    app.include_router(router)
    return app


app = create_app()
