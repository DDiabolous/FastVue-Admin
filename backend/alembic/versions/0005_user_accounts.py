"""Add registered users, separate from administrator users."""

from alembic import op
import sqlalchemy as sa

revision = '0005'
down_revision = '0004'
branch_labels = None
depends_on = None


def upgrade():
    if not op.get_context().as_sql and sa.inspect(op.get_bind()).has_table('user_accounts'):
        # 兼容已由启动 create_all 创建的新结构，拒绝误用旧后台 users 表。
        columns = {c['name'] for c in sa.inspect(op.get_bind()).get_columns('user_accounts')}
        if not {'phone', 'auth_version', 'membership_level', 'deleted_at'}.issubset(columns):
            raise RuntimeError('user_accounts 表结构不匹配，请检查已有数据')
        return
    op.create_table(
        'user_accounts',
        sa.Column('id', sa.String(32), primary_key=True),
        sa.Column('phone', sa.String(16), nullable=True, unique=True),
        sa.Column('password_hash', sa.String(256), nullable=True),
        sa.Column('nickname', sa.String(64), nullable=False),
        sa.Column('avatar_url', sa.String(2048), nullable=False),
        sa.Column('status', sa.String(16), nullable=False),
        sa.Column('auth_version', sa.Integer(), nullable=False),
        sa.Column('membership_level', sa.String(32), nullable=False),
        sa.Column('membership_expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "status IN ('active', 'disabled', 'deleted')", name='ck_user_account_status'
        ),
    )


def downgrade():
    op.drop_table('user_accounts')
