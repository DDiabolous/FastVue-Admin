"""Name product accounts and administrator authentication tables explicitly."""

from alembic import op

revision = '0007'
down_revision = '0006'
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table('user_accounts', 'app_accounts')
    op.rename_table('sessions', 'admin_sessions')
    op.rename_table('login_buckets', 'admin_login_buckets')
    op.execute('ALTER INDEX ix_sessions_user_id RENAME TO ix_admin_sessions_user_id')
    op.execute('ALTER INDEX ix_sessions_expires_at RENAME TO ix_admin_sessions_expires_at')


def downgrade():
    op.execute('ALTER INDEX ix_admin_sessions_expires_at RENAME TO ix_sessions_expires_at')
    op.execute('ALTER INDEX ix_admin_sessions_user_id RENAME TO ix_sessions_user_id')
    op.rename_table('admin_login_buckets', 'login_buckets')
    op.rename_table('admin_sessions', 'sessions')
    op.rename_table('app_accounts', 'user_accounts')
