from datetime import datetime, timezone
from pathlib import Path

import json

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import inspect, select, text

from app.core.passwords import hash_password
from app.migrate_user_accounts import import_records, PROFILE_DEFAULTS
from app.models import AdminAccount
from app.models.user.accounts import UserAccount


def record(uid, phone):
    now = datetime.now(timezone.utc)
    return dict(
        id=uid,
        phone=phone,
        password_hash=hash_password('Password123!'),
        nickname='迁移用户',
        avatar_url='',
        status='active',
        auth_version=3,
        created_at=now,
        updated_at=now,
        deleted_at=None,
    )


async def test_import_preserves_hashes_profiles_and_is_idempotent(app):
    row = record('1' * 32, '+8613900000001')
    assert await import_records(app.state.sessions, [row]) == (1, 0)
    assert await import_records(app.state.sessions, [row]) == (0, 1)
    async with app.state.sessions() as db:
        stored = await db.get(UserAccount, row['id'])
        assert all(getattr(stored, key) == value for key, value in row.items())
        assert await db.scalar(select(AdminAccount.id).where(AdminAccount.builtin.is_(True)))
    with pytest.raises(ValueError, match='不一致'):
        await import_records(app.state.sessions, [{**row, 'nickname': 'different'}])


async def test_import_phone_conflict_rolls_back_whole_batch(app):
    row = record('1' * 32, '+8613900000001')
    await import_records(app.state.sessions, [row])
    other = record('2' * 32, '+8613900000002')
    conflict = record('3' * 32, row['phone'])
    with pytest.raises(ValueError, match='相同手机号'):
        await import_records(app.state.sessions, [other, conflict])
    async with app.state.sessions() as db:
        assert await db.get(UserAccount, other['id']) is None


async def test_user_table_rename_preserves_product_records(app):
    row = record('4' * 32, '+8613900000004')
    await import_records(app.state.sessions, [row])
    config = Config(str(Path(__file__).resolve().parents[1] / 'alembic.ini'))

    def verify(connection):
        config.attributes['connection'] = connection
        before = connection.execute(text('SELECT row_to_json(a)::text FROM users a')).scalar_one()
        command.downgrade(config, '0007')
        assert not inspect(connection).has_table('users')
        assert {
            **PROFILE_DEFAULTS,
            **json.loads(
                connection.execute(
                    text(
                        "SELECT (to_jsonb(a) - 'membership_level' - 'membership_expires_at')::text FROM app_accounts a"
                    )
                ).scalar_one()
            ),
        } == json.loads(before)
        command.upgrade(config, 'head')
        assert not inspect(connection).has_table('app_accounts')
        assert (
            connection.execute(text('SELECT row_to_json(a)::text FROM users a')).scalar_one()
            == before
        )

    async with app.state.engine.begin() as db:
        await db.run_sync(verify)
    async with app.state.sessions() as db:
        stored = await db.get(UserAccount, row['id'])
        assert all(getattr(stored, key) == value for key, value in row.items())


async def test_user_table_migration_preserves_administrator_records(app):
    config = Config(str(Path(__file__).resolve().parents[1] / 'alembic.ini'))
    async with app.state.engine.begin() as db:
        before = (
            (
                await db.execute(
                    text('SELECT row_to_json(u)::text FROM admin_accounts u ORDER BY id')
                )
            )
            .scalars()
            .all()
        )

        def verify(connection):
            config.attributes['connection'] = connection
            command.downgrade(config, '0004')
            assert not inspect(connection).has_table('user_accounts')
            command.upgrade(config, 'head')
            assert inspect(connection).has_table('users')

        await db.run_sync(verify)
        after = (
            (
                await db.execute(
                    text('SELECT row_to_json(u)::text FROM admin_accounts u ORDER BY id')
                )
            )
            .scalars()
            .all()
        )
        assert before == after
