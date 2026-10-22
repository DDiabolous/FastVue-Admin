"""Add the personal profile cover image.

Revision ID: 0003
Revises: 0002
"""

from alembic import op
import sqlalchemy as sa

revision = '0003'
down_revision = '0002'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('coverImage', sa.Text(), nullable=True))


def downgrade():
    op.drop_column('users', 'coverImage')
