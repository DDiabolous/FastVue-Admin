from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect, text

from app.core.readiness import check_database
from conftest import sign_in


async def test_admin_table_rename_preserves_records_and_sessions(app, client):
    headers = await sign_in(client)
    config = Config(str(Path(__file__).resolve().parents[1] / 'alembic.ini'))

    def verify(connection):
        config.attributes['connection'] = connection

        def snapshot(table):
            return (
                connection.execute(text(f'SELECT row_to_json(t)::text FROM {table} t ORDER BY id'))
                .scalars()
                .all()
            )

        accounts = snapshot('admin_accounts')
        roles = snapshot('admin_roles')
        command.downgrade(config, '0005')
        assert snapshot('users') == accounts
        assert snapshot('roles') == roles
        assert not inspect(connection).has_table('admin_accounts')
        command.upgrade(config, 'head')
        assert snapshot('admin_accounts') == accounts
        assert snapshot('admin_roles') == roles
        inspector = inspect(connection)
        assert not inspector.has_table('users')
        assert not inspector.has_table('roles')
        assert inspector.get_foreign_keys('admin_sessions')[0]['referred_table'] == 'admin_accounts'
        assert inspector.get_foreign_keys('admin_accounts')[0]['referred_table'] == 'admin_roles'
        assert 'ix_admin_accounts_role' in {
            index['name'] for index in inspector.get_indexes('admin_accounts')
        }

    async with app.state.engine.begin() as db:
        await db.run_sync(verify)
    await check_database(app, '0007')
    assert (await client.get('/api/v1/admin/me', headers=headers)).status_code == 200
