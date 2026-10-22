from datetime import timedelta

import pytest
from sqlalchemy import select, update

from app.cli import initialize
from app.models import AuditLog, LoginBucket, Session, User, utcnow
from conftest import sign_in


async def rows(client, headers, resource):
    response = await client.get('/api/v1/' + resource, headers=headers)
    assert response.status_code == 200, response.text
    return response.json()['data']['list']


async def test_auth_logout_expiry_and_password_hash(client, app):
    assert (await client.get('/api/v1/auth/me')).status_code == 401
    for username in ['missing', 'admin']:
        response = await client.post(
            '/api/v1/auth/login', json={'username': username, 'password': 'wrong'}
        )
        assert response.status_code == 401
        assert 'wrong' not in response.text
    headers = await sign_in(client)
    me = (await client.get('/api/v1/auth/me', headers=headers)).json()['data']
    assert me['permissions'] == ['*']
    assert 'password' not in str(me) and 'hash' not in str(me)
    async with app.state.sessions() as db:
        user = await db.scalar(select(User).where(User.username == 'admin'))
        assert user.password_hash.startswith('$argon2id$')
        stored = await db.scalar(select(Session))
        assert headers['Authorization'].split()[1] not in stored.token_hash
    assert (await client.post('/api/v1/auth/logout', headers=headers)).status_code == 200
    assert (await client.get('/api/v1/auth/me', headers=headers)).status_code == 401
    headers = await sign_in(client)
    async with app.state.sessions() as db, db.begin():
        await db.execute(update(Session).values(expires_at=utcnow() - timedelta(seconds=1)))
    assert (await client.get('/api/v1/auth/me', headers=headers)).status_code == 401


async def test_password_profile_and_all_sessions_revoked(client, admin):
    second = await sign_in(client)
    response = await client.patch(
        '/api/v1/auth/profile',
        headers=admin,
        json={'realName': '维护者', 'email': 'owner@example.org'},
    )
    assert response.json()['data']['realName'] == '维护者'
    assert (
        await client.post(
            '/api/v1/auth/password',
            headers=admin,
            json={'oldPassword': 'incorrect', 'newPassword': 'ChangedPass123!'},
        )
    ).status_code == 400
    assert (
        await client.post(
            '/api/v1/auth/password',
            headers=admin,
            json={'oldPassword': 'AdminPass123!', 'newPassword': 'ChangedPass123!'},
        )
    ).status_code == 200
    for headers in [admin, second]:
        assert (await client.get('/api/v1/auth/me', headers=headers)).status_code == 401


async def test_personal_profile_details(client, admin):
    me = (await client.get('/api/v1/auth/me', headers=admin)).json()['data']
    assert me['gender'] == 'unspecified'
    assert me['bio'] == ''
    details = {
        'gender': 'female',
        'phone': '+86 13800138000',
        'location': '上海',
        'bio': '后端开发者\n喜欢摄影与开源。',
    }
    response = await client.patch('/api/v1/auth/profile', headers=admin, json=details)
    assert response.status_code == 200
    assert all(response.json()['data'][key] == value for key, value in details.items())
    # Image auto-save must not reset any optional profile details.
    await client.patch('/api/v1/auth/profile', headers=admin, json={'avatar': ''})
    me = (await client.get('/api/v1/auth/me', headers=admin)).json()['data']
    assert all(me[key] == value for key, value in details.items())
    for invalid in [{'gender': 'invalid'}, {'bio': 'x' * 501}, {'phone': 'x' * 33}]:
        response = await client.patch('/api/v1/auth/profile', headers=admin, json=invalid)
        assert response.status_code == 422
    reset = {'gender': 'unspecified', 'phone': '', 'location': '', 'bio': ''}
    response = await client.patch('/api/v1/auth/profile', headers=admin, json=reset)
    assert response.status_code == 200
    assert all(response.json()['data'][key] == value for key, value in reset.items())


async def test_profile_cover_persistence_and_reset(client, admin):
    cover = 'data:image/webp;base64,dGVzdA=='
    original = (await client.get('/api/v1/auth/me', headers=admin)).json()['data']
    response = await client.patch('/api/v1/auth/profile', headers=admin, json={'coverImage': cover})
    assert response.status_code == 200
    assert response.json()['data']['realName'] == original['realName']
    assert response.json()['data']['email'] == original['email']
    avatar = 'data:image/png;base64,dGVzdA=='
    response = await client.patch('/api/v1/auth/profile', headers=admin, json={'avatar': avatar})
    assert response.status_code == 200
    assert response.json()['data']['avatar'] == avatar
    assert response.json()['data']['coverImage'] == cover
    assert response.json()['data']['realName'] == original['realName']
    assert response.json()['data']['email'] == original['email']
    assert (
        await client.patch('/api/v1/auth/profile', headers=admin, json={'realName': None})
    ).status_code == 422
    profile = {'realName': '管理员', 'email': 'admin@example.org', 'coverImage': cover}
    response = await client.patch('/api/v1/auth/profile', headers=admin, json=profile)
    assert response.status_code == 200
    assert response.json()['data']['coverImage'] == cover
    me = await client.get('/api/v1/auth/me', headers=admin)
    assert me.json()['data']['coverImage'] == cover

    # Older clients that omit the cover must preserve the saved image.
    del profile['coverImage']
    response = await client.patch('/api/v1/auth/profile', headers=admin, json=profile)
    assert response.json()['data']['coverImage'] == cover

    profile['coverImage'] = ''
    response = await client.patch('/api/v1/auth/profile', headers=admin, json=profile)
    assert response.json()['data']['coverImage'] == ''
    me = await client.get('/api/v1/auth/me', headers=admin)
    assert me.json()['data']['coverImage'] == ''


async def test_session_management_and_avatar_persistence(client, admin):
    # 1. Verify avatar persistence
    avatar_data = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=='
    update_res = await client.patch(
        '/api/v1/auth/profile',
        headers=admin,
        json={'realName': '管理员测试', 'email': 'admin@test.local', 'avatar': avatar_data},
    )
    assert update_res.status_code == 200
    assert update_res.json()['data']['avatar'] == avatar_data

    # Re-fetch profile to ensure database persistence
    me_res = await client.get('/api/v1/auth/me', headers=admin)
    assert me_res.status_code == 200
    assert me_res.json()['data']['avatar'] == avatar_data

    # 2. Simulate another device login with iOS User-Agent
    login_res = await client.post(
        '/api/v1/auth/login',
        json={'username': 'admin', 'password': 'AdminPass123!'},
        headers={
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Mobile Safari/604.1'
        },
    )
    assert login_res.status_code == 200
    second_token = login_res.json()['data']['token']
    second_headers = {'Authorization': f'Bearer {second_token}'}

    # Query active sessions
    sessions_res = await client.get('/api/v1/auth/sessions', headers=admin)
    assert sessions_res.status_code == 200
    session_list = sessions_res.json()['data']
    assert len(session_list) >= 2
    second_session = next(s for s in session_list if not s['isCurrent'])
    assert 'Safari on iOS' in second_session['device']
    assert second_session['createdAt'] is not None

    # Revoke the second session
    revoke_res = await client.delete(
        f'/api/v1/auth/sessions/{second_session["tokenHash"]}', headers=admin
    )
    assert revoke_res.status_code == 200

    # Verify second session is revoked while current session remains active
    assert (await client.get('/api/v1/auth/me', headers=second_headers)).status_code == 401
    assert (await client.get('/api/v1/auth/me', headers=admin)).status_code == 200
    await sign_in(client, password='ChangedPass123!')


async def test_viewer_and_editor_cannot_bypass_permissions(client, admin):
    viewer = await sign_in(client, 'viewer', 'viewer123')
    editor = await sign_in(client, 'editor', 'editor123')
    for resource in ['users', 'dictionary']:
        assert (await client.get('/api/v1/' + resource, headers=viewer)).status_code == 200
        assert (
            await client.post('/api/v1/' + resource, headers=viewer, json={})
        ).status_code == 403
    for path in ['/roles', '/settings', '/logs', '/auth/roles']:
        assert (await client.get('/api/v1' + path, headers=viewer)).status_code == 403
    assert (await client.get('/api/v1/roles', headers=editor)).status_code == 403
    assignable = (await client.get('/api/v1/auth/roles', headers=editor)).json()['data']
    assert 'admin' not in [row['roleKey'] for row in assignable]
    payload = {'username': 'elevate', 'realName': 'x', 'role': 'admin', 'password': 'Testing123!'}
    assert (await client.post('/api/v1/users', headers=editor, json=payload)).status_code == 403
    payload['role'] = 'viewer'
    assert (await client.post('/api/v1/users', headers=editor, json=payload)).status_code == 200
    users = await rows(client, admin, 'users')
    root = next(row for row in users if row['username'] == 'admin')
    assert (
        await client.patch(
            '/api/v1/users/' + root['id'], headers=editor, json={'realName': 'hacked'}
        )
    ).status_code == 400


async def test_role_escalation_is_denied_even_with_role_write_permission(client, admin):
    # A delegated role administrator must not grant '*', or modify/delete higher roles.
    grants = [f'system:roles:{a}' for a in ['read', 'create', 'update', 'delete']]
    role = {'roleKey': 'delegate', 'roleName': '委派管理员', 'permissions': grants}
    assert (await client.post('/api/v1/roles', headers=admin, json=role)).status_code == 200
    assert (
        await client.post(
            '/api/v1/users',
            headers=admin,
            json={
                'username': 'delegate',
                'realName': 'x',
                'role': 'delegate',
                'password': 'Testing123!',
            },
        )
    ).status_code == 200
    delegated = await sign_in(client, 'delegate', 'Testing123!')
    for perms in [['*'], ['system:users:delete']]:
        assert (
            await client.post(
                '/api/v1/roles',
                headers=delegated,
                json={'roleKey': 'hacked', 'roleName': 'x', 'permissions': perms},
            )
        ).status_code == 403
    editor_role = next(
        row for row in await rows(client, admin, 'roles') if row['roleKey'] == 'editor'
    )
    for method, body in [('PATCH', {'permissions': []}), ('DELETE', None)]:
        response = await client.request(
            method,
            '/api/v1/roles/' + editor_role['id'],
            headers=delegated,
            **({'json': body} if body else {}),
        )
        assert response.status_code == 403


async def test_crud_unique_constraints_validation_and_rollback(client, admin):
    payload = {'type': 'test', 'label': '标签', 'value': 'value', 'sort': 0, 'status': 1}
    assert (await client.post('/api/v1/dictionary', headers=admin, json=payload)).status_code == 200
    assert (await client.post('/api/v1/dictionary', headers=admin, json=payload)).status_code == 409
    records = await rows(client, admin, 'dictionary')
    target = next(row for row in records if row['type'] == 'test')
    assert (
        await client.patch(
            '/api/v1/dictionary/' + target['id'], headers=admin, json={'label': '修改'}
        )
    ).status_code == 200
    assert (
        await client.patch(
            '/api/v1/dictionary/' + target['id'], headers=admin, json={'label': None}
        )
    ).status_code == 422
    assert (await client.get('/api/v1/dictionary?page=0', headers=admin)).status_code == 422
    assert (await client.get('/api/v1/users?pageSize=201', headers=admin)).status_code == 422
    assert (
        await client.post(
            '/api/v1/roles',
            headers=admin,
            json={'roleKey': 'bad', 'roleName': 'x', 'permissions': ['bad:permission']},
        )
    ).status_code == 422
    assert (
        await client.post(
            '/api/v1/users',
            headers=admin,
            json={'username': 'test', 'realName': 'x', 'role': 'viewer', 'password': 'short'},
        )
    ).status_code == 422
    # Failed write never corrupts subsequent requests or creates an audit success.
    assert (
        len([row for row in await rows(client, admin, 'dictionary') if row['type'] == 'test']) == 1
    )
    assert (
        await client.delete('/api/v1/dictionary/' + target['id'], headers=admin)
    ).status_code == 200
    assert (
        await client.delete('/api/v1/dictionary/' + target['id'], headers=admin)
    ).status_code == 404


async def test_builtin_and_bound_roles_are_protected(client, admin):
    root = next(row for row in await rows(client, admin, 'users') if row['username'] == 'admin')
    roles = await rows(client, admin, 'roles')
    builtin = next(row for row in roles if row['roleKey'] == 'admin')
    viewer = next(row for row in roles if row['roleKey'] == 'viewer')
    for resource, row in [('users', root), ('roles', builtin)]:
        assert (
            await client.delete('/api/v1/' + resource + '/' + row['id'], headers=admin)
        ).status_code == 400
    assert (
        await client.patch(
            '/api/v1/roles/' + builtin['id'], headers=admin, json={'permissions': []}
        )
    ).status_code == 400
    assert (
        await client.patch(
            '/api/v1/roles/' + viewer['id'], headers=admin, json={'roleKey': 'renamed'}
        )
    ).status_code == 400
    assert (await client.delete('/api/v1/roles/' + viewer['id'], headers=admin)).status_code == 400


@pytest.mark.parametrize(
    'mutation', ['disable_user', 'reset_password', 'disable_role', 'role_change']
)
async def test_account_changes_revoke_sessions(client, admin, mutation):
    headers = await sign_in(client, 'viewer', 'viewer123')
    user = next(row for row in await rows(client, admin, 'users') if row['username'] == 'viewer')
    if mutation == 'disable_role':
        role = next(row for row in await rows(client, admin, 'roles') if row['roleKey'] == 'viewer')
        url, body = '/api/v1/roles/' + role['id'], {'status': 0}
    else:
        url = '/api/v1/users/' + user['id']
        body = {
            'disable_user': {'status': 0},
            'reset_password': {'password': 'ResetPass123!'},
            'role_change': {'role': 'editor'},
        }[mutation]
    assert (await client.patch(url, headers=admin, json=body)).status_code == 200
    assert (await client.get('/api/v1/auth/me', headers=headers)).status_code == 401
    if mutation in ['disable_user', 'disable_role']:
        assert (
            await client.post(
                '/api/v1/auth/login', json={'username': 'viewer', 'password': 'viewer123'}
            )
        ).status_code == 401
        await client.patch(url, headers=admin, json={'status': 1})
        assert (await client.get('/api/v1/auth/me', headers=headers)).status_code == 401


async def test_role_permission_changes_apply_to_next_request(client, admin):
    headers = await sign_in(client, 'viewer', 'viewer123')
    role = next(row for row in await rows(client, admin, 'roles') if row['roleKey'] == 'viewer')
    assert (
        await client.patch('/api/v1/roles/' + role['id'], headers=admin, json={'permissions': []})
    ).status_code == 200
    assert (await client.get('/api/v1/users', headers=headers)).status_code == 403
    assert (await client.get('/api/v1/auth/me', headers=headers)).json()['data'][
        'permissions'
    ] == []


async def test_login_rate_limit_persists_and_recovers(client, app):
    app.state.config.login_limit = 2
    for _ in range(2):
        assert (
            await client.post('/api/v1/auth/login', json={'username': 'admin', 'password': 'wrong'})
        ).status_code == 401
    response = await client.post(
        '/api/v1/auth/login', json={'username': 'admin', 'password': 'AdminPass123!'}
    )
    assert response.status_code == 429 and 'Retry-After' in response.headers
    async with app.state.sessions() as db, db.begin():
        await db.execute(update(LoginBucket).values(started_at=utcnow() - timedelta(hours=1)))
    await sign_in(client)


async def test_settings_public_whitelist_logs_and_idempotent_initialization(client, admin, app):
    payload = {
        'siteName': '测试后台',
        'description': '说明',
        'contactEmail': 'admin@example.org',
        'registration': '测试备案',
    }
    assert (await client.patch('/api/v1/settings', headers=admin, json=payload)).status_code == 200
    assert (await client.get('/api/v1/settings', headers=admin)).json()['data'] == payload
    assert (await client.get('/api/v1/settings/public')).json()['data'] == {
        'siteName': '测试后台',
        'description': '说明',
    }
    assert not await initialize(app.state.sessions, 'DoNotReset123!')
    await sign_in(client)
    logs = await rows(client, admin, 'logs')
    assert any(row['action'] == '更新系统配置' for row in logs)
    assert (await client.post('/api/v1/logs', headers=admin, json={})).status_code == 405
    assert (await client.get('/api/v1/logs?category=invalid', headers=admin)).status_code == 422
    async with app.state.sessions() as db:
        content = str(
            [(row.action, row.target, row.ip) for row in (await db.scalars(select(AuditLog))).all()]
        )
        assert 'AdminPass123!' not in content and 'Bearer' not in content
        assert '127.0.0.1' in content
    assert (await client.get('/api/v1/missing')).status_code == 404
    assert (await client.get('/api/health')).status_code == 200


async def test_cors_and_validation_do_not_expose_credentials(client):
    response = await client.options(
        '/api/v1/auth/login',
        headers={'Origin': 'https://untrusted.example', 'Access-Control-Request-Method': 'POST'},
    )
    assert 'access-control-allow-origin' not in response.headers
    response = await client.options(
        '/api/v1/auth/login',
        headers={'Origin': 'http://localhost:5173', 'Access-Control-Request-Method': 'POST'},
    )
    assert response.headers['access-control-allow-origin'] == 'http://localhost:5173'
    response = await client.post(
        '/api/v1/auth/login', json={'username': 'x', 'password': 'sensitive' * 100}
    )
    assert response.status_code == 422 and 'sensitive' not in response.text


async def test_nonbuiltin_privileged_users_are_outside_editor_scope(client, admin):
    assert (
        await client.post(
            '/api/v1/users',
            headers=admin,
            json={
                'username': 'privileged',
                'realName': '高级账号',
                'role': 'admin',
                'password': 'Testing123!',
            },
        )
    ).status_code == 200
    editor = await sign_in(client, 'editor', 'editor123')
    target = next(
        row for row in await rows(client, admin, 'users') if row['username'] == 'privileged'
    )
    assert (
        await client.patch('/api/v1/users/' + target['id'], headers=editor, json={'role': 'viewer'})
    ).status_code == 403
    assert (await client.delete('/api/v1/users/' + target['id'], headers=editor)).status_code == 403
    me = next(row for row in await rows(client, admin, 'users') if row['username'] == 'editor')
    assert (await client.delete('/api/v1/users/' + me['id'], headers=editor)).status_code == 400


async def test_concurrent_duplicate_writes_and_failed_update_are_atomic(client, admin):
    import asyncio

    payload = {'type': 'concurrent', 'label': '标签', 'value': 'same'}
    responses = await asyncio.gather(
        *[client.post('/api/v1/dictionary', headers=admin, json=payload) for _ in range(2)]
    )
    assert sorted(response.status_code for response in responses) == [200, 409]
    assert (
        await client.post(
            '/api/v1/dictionary', headers=admin, json={**payload, 'value': 'different'}
        )
    ).status_code == 200
    records = [
        row for row in await rows(client, admin, 'dictionary') if row['type'] == 'concurrent'
    ]
    target = next(row for row in records if row['value'] == 'different')
    before = (await client.get('/api/v1/logs?keyword=编辑dictionary', headers=admin)).json()[
        'data'
    ]['total']
    assert (
        await client.patch(
            '/api/v1/dictionary/' + target['id'],
            headers=admin,
            json={'label': '不应保存', 'value': 'same'},
        )
    ).status_code == 409
    restored = next(
        row for row in await rows(client, admin, 'dictionary') if row['id'] == target['id']
    )
    assert restored['label'] == '标签' and restored['value'] == 'different'
    after = (await client.get('/api/v1/logs?keyword=编辑dictionary', headers=admin)).json()['data'][
        'total'
    ]
    assert before == after


async def test_account_and_role_unique_keys_and_input_whitelists(client, admin):
    payload = {'username': 'viewer', 'realName': 'x', 'role': 'viewer', 'password': 'Testing123!'}
    assert (await client.post('/api/v1/users', headers=admin, json=payload)).status_code == 409
    assert (
        await client.post(
            '/api/v1/roles', headers=admin, json={'roleKey': 'viewer', 'roleName': 'x'}
        )
    ).status_code == 409
    for field in ['builtin', 'password_hash', 'createdAt', 'id']:
        response = await client.post(
            '/api/v1/users', headers=admin, json={**payload, 'username': 'new', field: 'untrusted'}
        )
        assert response.status_code == 422 and 'untrusted' not in response.text
    assert (
        await client.patch('/api/v1/settings', headers=admin, json={'siteName': None})
    ).status_code == 422
    for status in [2, '1', True, None]:
        assert (
            await client.post(
                '/api/v1/roles',
                headers=admin,
                json={'roleKey': 'bad', 'roleName': 'x', 'status': status},
            )
        ).status_code == 422


async def test_pagination_literal_keyword_and_public_data_boundaries(client, admin):
    first = (await client.get('/api/v1/users?pageSize=1', headers=admin)).json()['data']
    second = (await client.get('/api/v1/users?page=2&pageSize=1', headers=admin)).json()['data']
    assert first['total'] == second['total'] == 3
    assert first['list'][0]['id'] != second['list'][0]['id']
    assert (await client.get('/api/v1/users?keyword=%25', headers=admin)).json()['data'][
        'total'
    ] == 0
    assert (await client.get('/api/v1/users?keyword=viewer', headers=admin)).json()['data'][
        'total'
    ] == 1
    for path in ['/users', '/roles', '/dictionary', '/settings', '/logs']:
        response = await client.get('/api/v1' + path, headers=admin)
        assert 'password_hash' not in response.text and 'token_hash' not in response.text
    assert (await client.get('/api/v1/logs?category=login', headers=admin)).json()['data'][
        'total'
    ] > 0
    assert (await client.get('/api/v1/logs?category=operation', headers=admin)).json()['data'][
        'total'
    ] == 0


async def test_health_requires_initialization_and_initializer_rejects_weak_password(client, app):
    from sqlalchemy import delete
    from app.models import SystemSettings

    with pytest.raises(ValueError):
        await initialize(app.state.sessions, 'short')
    async with app.state.sessions() as db, db.begin():
        await db.execute(delete(SystemSettings))
    assert (await client.get('/api/health')).status_code == 503
