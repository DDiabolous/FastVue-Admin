"""注册用户业务：SQL 行锁串行化登录、刷新、重置和注销。"""

import secrets
import uuid
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from starlette.concurrency import run_in_threadpool
from app.core.user_security import user_unauthorized, make_tokens, parse_refresh
from app.core.passwords import hash_password, verify_password
from app.db.base import utcnow
from app.models.user.accounts import UserAccount

DUMMY_HASH = hash_password(secrets.token_urlsafe(32))


def profile(user: UserAccount):
    return {
        'id': user.id,
        'phone': user.phone,
        'nickname': user.nickname,
        'avatar_url': user.avatar_url,
        'gender': user.gender,
        'birthday': user.birthday,
        'city': user.city,
        'email': user.email,
        'bio': user.bio,
    }


async def by_phone(db, phone):
    return (
        await db.execute(
            select(UserAccount)
            .where(UserAccount.phone == phone)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
    ).scalar_one_or_none()


async def locked_user(db, uid):
    return (
        await db.execute(
            select(UserAccount)
            .where(UserAccount.id == uid)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
    ).scalar_one_or_none()


async def issue_tokens(user, device, store):
    sid = uuid.uuid4().hex
    tokens, jti = make_tokens(user, sid, store.config)
    await store.issue(user.id, sid, tokens['refresh_token'], jti, user.auth_version, device)
    tokens['user'] = profile(user)
    return tokens


async def register(db, store, payload):
    if not await store.consume_code(payload.phone, 'register', payload.code):
        raise HTTPException(400, '验证码无效或已过期')
    if await by_phone(db, payload.phone):
        raise HTTPException(409, '该手机号已注册')
    user = UserAccount(
        phone=payload.phone,
        nickname='用户' + payload.phone[-4:],
        password_hash=await run_in_threadpool(hash_password, payload.password),
    )
    db.add(user)
    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(409, '该手机号已注册') from None
    tokens = await issue_tokens(user, payload.device_id, store)
    try:
        await db.commit()
    except Exception:
        await store.revoke_all(user.id)
        raise
    return tokens


async def login(db, store, payload, ip):
    await store.login_budget(ip)
    await store.check_login_lock(payload.phone)
    user = await by_phone(db, payload.phone)
    await store.check_login_lock(payload.phone)
    if payload.login_type == 'password':
        valid = await run_in_threadpool(
            verify_password,
            payload.credential,
            user.password_hash if user and user.password_hash else DUMMY_HASH,
        )
    else:
        valid = await store.consume_code(payload.phone, 'login', payload.credential)
    if not valid or user is None or user.status != 'active':
        await store.login_failure(payload.phone)
        raise HTTPException(401, '手机号或登录凭证错误')
    await store.login_success(payload.phone)
    tokens = await issue_tokens(user, payload.device_id, store)
    await db.commit()
    return tokens


async def refresh(db, store, token):
    uid, sid = parse_refresh(token)
    user = await locked_user(db, uid)
    if user is None or user.status != 'active':
        raise user_unauthorized()
    tokens, jti = make_tokens(user, sid, store.config)
    if not await store.rotate(uid, sid, token, tokens['refresh_token'], jti, user.auth_version):
        raise user_unauthorized()
    await db.commit()
    return tokens


async def reset_password(db, store, payload):
    user = await by_phone(db, payload.phone)
    if not await store.consume_code(payload.phone, 'reset_pwd', payload.code):
        raise HTTPException(400, '验证码无效或已过期')
    if user is None or user.status != 'active':
        raise HTTPException(400, '无法重置该账号密码')
    user.password_hash = await run_in_threadpool(hash_password, payload.new_password)
    user.auth_version += 1
    await store.revoke_all(user.id)
    await db.commit()


async def delete_account(db, store, user, payload):
    await store.check_login_lock(user.phone)
    if payload.password is not None:
        valid = await run_in_threadpool(verify_password, payload.password, user.password_hash)
    else:
        valid = await store.consume_code(user.phone, 'delete_account', payload.code)
    if not valid:
        await store.login_failure(user.phone)
        raise HTTPException(400, '二次身份验证失败')
    await store.revoke_all(user.id)
    user.status = 'deleted'
    user.auth_version += 1
    user.deleted_at = utcnow()
    # 注销后释放手机号，并去除个人资料及密码哈希，保留不可登录的注销记录。
    user.phone = None
    user.password_hash = None
    user.nickname = '已注销用户'
    user.avatar_url = ''
    user.gender = 'unspecified'
    user.birthday = None
    user.city = None
    user.email = None
    user.bio = None
    await db.commit()
