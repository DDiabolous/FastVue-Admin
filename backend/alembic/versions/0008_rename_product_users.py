"""Rename product accounts to users without modifying administrator accounts."""

from alembic import op

revision = '0008'
down_revision = '0007'
branch_labels = None
depends_on = None


def upgrade():
    # The original administrator users table was renamed in revision 0006.
    op.rename_table('app_accounts', 'users')


def downgrade():
    op.rename_table('users', 'app_accounts')
