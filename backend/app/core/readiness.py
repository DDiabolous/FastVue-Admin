import asyncio

from sqlalchemy import text


class DatabaseNotReady(RuntimeError):
    pass


async def check_database(app, expected_revision):
    """Use the same bounded readiness check during startup and ongoing probes."""
    try:
        async with asyncio.timeout(10):
            async with app.state.sessions() as db:
                await db.execute(text('SELECT 1'))
                revisions = (
                    await db.scalars(text('SELECT version_num FROM alembic_version'))
                ).all()
                if revisions != [expected_revision]:
                    raise DatabaseNotReady(
                        '数据库迁移版本不匹配，请先执行 uv run --locked alembic upgrade head'
                    )
                settings_ready = await db.scalar(
                    text('SELECT EXISTS (SELECT 1 FROM settings WHERE id = 1)')
                )
                admin_ready = await db.scalar(
                    text("""
                    SELECT EXISTS (
                        SELECT 1 FROM admin_accounts u JOIN admin_roles r ON u.role = r."roleKey"
                        WHERE u.builtin AND r.builtin AND u.status = 1 AND r.status = 1
                    )
                """)
                )
                if not settings_ready or not admin_ready:
                    raise DatabaseNotReady(
                        '数据库尚未完成初始化，请先执行 uv run --locked python -m app.cli init；'
                        '如已初始化，请检查内置管理员和角色状态'
                    )
    except DatabaseNotReady:
        raise
    except TimeoutError:
        raise DatabaseNotReady('数据库检查超时（10 秒），请检查连接配置和数据库状态') from None
    except Exception:
        # Never include driver messages: they may contain credentials or connection URLs.
        raise DatabaseNotReady(
            '数据库连接失败或结构不完整，请检查 DATABASE_URL、数据库状态，'
            '并确认已执行 uv run --locked alembic upgrade head'
        ) from None
