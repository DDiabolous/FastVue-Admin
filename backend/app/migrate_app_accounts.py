"""只读源库，将独立注册用户导入目标库；不迁移后台账号或 Redis 会话。"""

import argparse
import asyncio
import os
from pathlib import Path

from dotenv import dotenv_values
from sqlalchemy import insert, select, text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import get_settings
from app.db.session import create_database
from app.models.app.accounts import AppAccount

COLUMNS = tuple(column.name for column in AppAccount.__table__.columns)


async def import_records(sessions, records):
    """全量事务；相同记录幂等跳过，任何不同的同 ID/手机号均拒绝。"""
    imported = skipped = 0
    async with sessions() as db, db.begin():
        await db.execute(text('SELECT pg_advisory_xact_lock(74192852)'))
        for record in records:
            if record['password_hash'] and not record['password_hash'].startswith('$argon2id$'):
                raise ValueError('源数据包含非 Argon2id 密码，未导入')
            current = await db.get(AppAccount, record['id'])
            if current is not None:
                if any(getattr(current, key) != record[key] for key in COLUMNS):
                    raise ValueError('用户 ID 对应的数据不一致，整批导入已回滚')
                skipped += 1
                continue
            if record['phone'] is not None and await db.scalar(
                select(AppAccount.id).where(AppAccount.phone == record['phone'])
            ):
                raise ValueError('目标已存在相同手机号，整批导入已回滚')
            # Core insert preserves all timestamps and nullable values exactly.
            await db.execute(insert(AppAccount.__table__).values(**record))
            imported += 1
    return imported, skipped


async def migrate(source_url, dry_run=False):
    if not source_url or not source_url.startswith('postgresql+asyncpg://'):
        raise ValueError('源 DATABASE_URL 必须使用 postgresql+asyncpg://')
    source = create_async_engine(source_url, hide_parameters=True)
    try:
        async with source.connect() as connection, connection.begin():
            await connection.execute(
                text('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY')
            )
            rows = (
                (
                    await connection.execute(
                        text('SELECT ' + ', '.join(COLUMNS) + ' FROM users ORDER BY id')
                    )
                )
                .mappings()
                .all()
            )
            records = [dict(row) for row in rows]
    finally:
        await source.dispose()
    if dry_run:
        print(f'源用户记录：{len(records)}；只读检查完成，未写入目标库')
        return
    engine, sessions = create_database(get_settings().database_url)
    try:
        imported, skipped = await import_records(sessions, records)
        print(f'已导入：{imported}；相同记录跳过：{skipped}；源数据未修改；用户需重新登录')
    finally:
        await engine.dispose()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-env', type=Path, help='源中台 .env（只读取 DATABASE_URL）')
    parser.add_argument('--dry-run', action='store_true', help='只读检查源数据，不连接目标库')
    args = parser.parse_args()
    if args.source_env and not args.source_env.is_file():
        parser.error('源 .env 文件不存在')
    source_url = (
        dotenv_values(args.source_env).get('DATABASE_URL')
        if args.source_env
        else os.getenv('SOURCE_DATABASE_URL')
    )
    try:
        asyncio.run(migrate(source_url, args.dry_run))
    except Exception as error:
        # Driver errors may contain URLs, hashes or personal data; do not echo them.
        message = (
            str(error)
            if isinstance(error, ValueError)
            else '数据库操作失败，请检查连接、迁移版本和源表结构'
        )
        parser.exit(1, message + '\n')


if __name__ == '__main__':
    main()
