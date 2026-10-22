"""add user avatar and session metadata

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-22 10:27:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('avatar', sa.Text(), nullable=True))
    op.add_column('sessions', sa.Column('created_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column(
        'sessions',
        sa.Column('ip', sa.String(length=64), server_default='127.0.0.1', nullable=False),
    )
    op.add_column(
        'sessions',
        sa.Column('user_agent', sa.String(length=255), server_default='', nullable=False),
    )


def downgrade():
    op.drop_column('sessions', 'user_agent')
    op.drop_column('sessions', 'ip')
    op.drop_column('sessions', 'created_at')
    op.drop_column('users', 'avatar')
