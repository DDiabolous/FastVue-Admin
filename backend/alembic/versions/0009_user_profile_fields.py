"""Add product user profile fields and remove membership attributes."""

from alembic import op
import sqlalchemy as sa

revision = '0009'
down_revision = '0008'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'users', sa.Column('gender', sa.String(16), nullable=False, server_default='unspecified')
    )
    op.add_column('users', sa.Column('birthday', sa.Date(), nullable=True))
    op.add_column('users', sa.Column('city', sa.String(100), nullable=True))
    op.add_column('users', sa.Column('email', sa.String(254), nullable=True))
    op.add_column('users', sa.Column('bio', sa.String(500), nullable=True))
    op.create_check_constraint(
        'ck_users_gender', 'users', "gender IN ('unspecified', 'male', 'female', 'other')"
    )
    op.drop_column('users', 'membership_expires_at')
    op.drop_column('users', 'membership_level')


def downgrade():
    # Dropped membership data cannot be recovered; restore the historical defaults.
    op.add_column(
        'users', sa.Column('membership_level', sa.String(32), nullable=False, server_default='free')
    )
    op.alter_column('users', 'membership_level', server_default=None)
    op.add_column(
        'users', sa.Column('membership_expires_at', sa.DateTime(timezone=True), nullable=True)
    )
    op.drop_constraint('ck_users_gender', 'users', type_='check')
    for name in ('bio', 'email', 'city', 'birthday', 'gender'):
        op.drop_column('users', name)
