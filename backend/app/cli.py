import argparse
import asyncio
import getpass
import os
from datetime import timedelta
from pathlib import Path

from alembic import command
from alembic.config import Config
from pydantic import ValidationError
from sqlalchemy import delete, select, text

from .core.config import get_settings
from .core.security import hash_password
from .db.session import create_database
from .models import Dictionary, LoginBucket, Role, Session, SystemSettings, User, utcnow

BACKEND_DIR = Path(__file__).resolve().parents[1]


def migrate_database():
    command.upgrade(Config(str(BACKEND_DIR / 'alembic.ini')), 'head')


def valid_port(value):
    try:
        port = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError('端口必须为整数') from None
    if not 1 <= port <= 65535:
        raise argparse.ArgumentTypeError('端口范围为 1–65535')
    return port


async def initialize(sessions, password, demo=False):
    if not 8 <= len(password) <= 128:
        raise ValueError('管理员密码需为 8–128 位')
    async with sessions() as db, db.begin():
        await db.execute(text('SELECT pg_advisory_xact_lock(74192851)'))
        if await db.scalar(select(User.id).where(User.builtin.is_(True))):
            return False  # Repeat initialization never resets credentials or app data.
        if await db.scalar(select(Role.id).limit(1)) or await db.scalar(select(User.id).limit(1)):
            raise ValueError('数据库中已有账号或角色，请勿重复导入初始数据')
        editor = [
            f'system:{resource}:{action}'
            for resource in ['users', 'dictionary']
            for action in ['read', 'create', 'update', 'delete']
        ]
        db.add_all(
            [
                Role(roleKey='admin', roleName='管理员', permissions=['*'], builtin=True),
                Role(roleKey='editor', roleName='编辑', permissions=editor),
                Role(
                    roleKey='viewer',
                    roleName='只读用户',
                    permissions=['system:users:read', 'system:dictionary:read'],
                ),
            ]
        )
        await db.flush()
        db.add(
            User(
                username='admin',
                realName='管理员',
                role='admin',
                builtin=True,
                password_hash=hash_password(password),
            )
        )
        if demo:
            db.add_all(
                [
                    User(
                        username='editor',
                        realName='编辑用户',
                        role='editor',
                        password_hash=hash_password('editor123'),
                    ),
                    User(
                        username='viewer',
                        realName='只读用户',
                        role='viewer',
                        password_hash=hash_password('viewer123'),
                    ),
                ]
            )
        db.add(SystemSettings(id=1))
        db.add_all(
            [
                Dictionary(type='common_status', label='启用', value='1', sort=1),
                Dictionary(type='common_status', label='停用', value='0', sort=2),
            ]
        )
    return True


async def run(args):
    config = get_settings()
    engine, sessions = create_database(config.database_url)
    try:
        if args.command in {'init', 'setup'}:
            async with sessions() as db:
                initialized = await db.scalar(select(User.id).where(User.builtin.is_(True)))
            if initialized:
                print('已初始化，未修改现有数据或密码')
                return
            password = os.environ.get('ADMIN_PASSWORD') or getpass.getpass(
                '首次管理员密码（至少 8 位）: '
            )
            created = await initialize(sessions, password, args.demo)
            print('初始化完成，管理员账号：admin' if created else '已初始化，未修改现有数据或密码')
            if created and args.demo:
                print('仅限开发：已创建 editor/editor123 和 viewer/viewer123')
        else:
            async with sessions() as db, db.begin():
                await db.execute(text('SELECT pg_advisory_xact_lock(74192851)'))
                await db.execute(delete(Session).where(Session.expires_at <= utcnow()))
                await db.execute(
                    delete(LoginBucket).where(
                        LoginBucket.started_at
                        < utcnow() - timedelta(seconds=config.login_window_seconds)
                    )
                )
            print('已清理过期会话与登录限流窗口，审计日志保留')
    finally:
        await engine.dispose()


def main():
    parser = argparse.ArgumentParser(description='FastVue-Admin 启动与数据库管理')
    sub = parser.add_subparsers(dest='command', required=True)
    setup = sub.add_parser('setup', help='首次准备或升级：执行迁移，按需初始化管理员')
    setup.add_argument('--demo', action='store_true', help='仅首次开发初始化：额外创建演示账号')
    init = sub.add_parser('init', help='迁移后显式初始化数据库')
    init.add_argument('--demo', action='store_true', help='仅开发环境：额外创建固定密码演示账号')
    sub.add_parser('cleanup', help='清理过期会话和限流记录')
    for name, help_text in [('dev', '启动开发服务，自动重载'), ('serve', '启动生产服务，不重载')]:
        server = sub.add_parser(name, help=help_text)
        server.add_argument('--host', default='127.0.0.1')
        server.add_argument('--port', type=valid_port, default=8000, metavar='PORT')
    args = parser.parse_args()
    try:
        if args.command in {'dev', 'serve'}:
            import uvicorn

            uvicorn.run(
                'app.main:app',
                host=args.host,
                port=args.port,
                reload=args.command == 'dev',
                reload_dirs=[str(BACKEND_DIR)] if args.command == 'dev' else None,
                proxy_headers=False,
            )
            return
        if args.command == 'setup':
            migrate_database()
        asyncio.run(run(args))
    except ValidationError:
        parser.exit(1, '配置无效，请检查 backend/.env 或进程环境变量\n')
    except ValueError as exc:
        parser.exit(1, f'{exc}\n')
    except Exception:
        parser.exit(1, '执行失败，请检查数据库连接、权限及迁移状态；未输出连接凭据\n')


if __name__ == '__main__':
    main()
