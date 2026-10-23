"""Rename administrator tables while preserving records and foreign keys."""

from alembic import op

revision = '0006'
down_revision = '0005'
branch_labels = None
depends_on = None


def upgrade():
    # PostgreSQL preserves constraints and referencing foreign keys on table rename.
    op.rename_table('roles', 'admin_roles')
    op.rename_table('users', 'admin_accounts')
    op.execute('ALTER INDEX ix_users_role RENAME TO ix_admin_accounts_role')


def downgrade():
    op.execute('ALTER INDEX ix_admin_accounts_role RENAME TO ix_users_role')
    op.rename_table('admin_accounts', 'users')
    op.rename_table('admin_roles', 'roles')
