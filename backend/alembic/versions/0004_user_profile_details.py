"""Add optional personal profile details.

Revision ID: 0004
Revises: 0003
"""

from alembic import op
import sqlalchemy as sa

revision = '0004'
down_revision = '0003'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'users', sa.Column('gender', sa.String(16), nullable=False, server_default='unspecified')
    )
    for name, length in [('phone', 32), ('location', 100), ('bio', 500)]:
        op.add_column(
            'users', sa.Column(name, sa.String(length), nullable=False, server_default='')
        )
    op.create_check_constraint(
        'user_gender', 'users', "gender IN ('unspecified', 'male', 'female', 'other')"
    )


def downgrade():
    op.drop_constraint('user_gender', 'users', type_='check')
    for name in ['bio', 'location', 'phone', 'gender']:
        op.drop_column('users', name)
