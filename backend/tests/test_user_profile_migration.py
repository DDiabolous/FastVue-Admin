from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect, text

from test_user_accounts_migration import record


async def test_profile_migration_preserves_accounts_and_backfills_defaults(app):
    config = Config(str(Path(__file__).resolve().parents[1] / 'alembic.ini'))
    original = record('5' * 32, '+8613900000005')

    def verify(connection):
        config.attributes['connection'] = connection
        command.downgrade(config, '0008')
        old = {**original, 'membership_level': 'premium', 'membership_expires_at': None}
        names = ', '.join(f'"{name}"' for name in old)
        values = ', '.join(f':{name}' for name in old)
        connection.execute(text(f'INSERT INTO users ({names}) VALUES ({values})'), old)
        command.upgrade(config, 'head')
        columns = {column['name'] for column in inspect(connection).get_columns('users')}
        assert not {'membership_level', 'membership_expires_at'} & columns
        stored = (
            connection.execute(text('SELECT * FROM users WHERE id = :id'), original)
            .mappings()
            .one()
        )
        assert all(stored[name] == value for name, value in original.items())
        assert stored['gender'] == 'unspecified'
        assert all(stored[name] is None for name in ('birthday', 'city', 'email', 'bio'))

    async with app.state.engine.begin() as db:
        await db.run_sync(verify)
