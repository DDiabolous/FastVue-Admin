import { test, beforeEach } from 'node:test'
import assert from 'node:assert/strict'
import { mockRequest } from '../src/mock/adapter.js'
import { readDatabase, writeDatabase } from '../src/mock/database.js'
import { hasPermission } from '../src/config/permissions.js'
const storage = new Map()
globalThis.localStorage = {
  getItem: (key) => storage.get(key) ?? null,
  setItem: (key, value) => storage.set(key, value),
  removeItem: (key) => storage.delete(key),
}
beforeEach(() => storage.clear())
const login = async (username = 'admin', password = `${username}123`) =>
  (await mockRequest('/auth/login', { method: 'POST', body: { username, password } })).token

test('image-only profile updates preserve name, email and the other image', async () => {
  const token = await login()
  const before = await mockRequest('/auth/me', { token })
  const patch = (body) => mockRequest('/auth/profile', { token, method: 'PATCH', body })
  const details = { gender: 'female', phone: '+86 13800138000', location: '上海', bio: '开源开发者' }
  await patch(details)
  await patch({ avatar: 'avatar-image' })
  const covered = await patch({ coverImage: 'cover-image' })
  assert.equal(covered.realName, before.realName)
  assert.equal(covered.email, before.email)
  assert.equal(covered.avatar, 'avatar-image')
  assert.equal(covered.coverImage, 'cover-image')
  await patch({ realName: 'Updated', email: 'updated@example.org' })
  const reset = await patch({ coverImage: '' })
  assert.equal(reset.realName, 'Updated')
  assert.equal(reset.email, 'updated@example.org')
  assert.equal(reset.avatar, 'avatar-image')
  assert.equal(reset.coverImage, '')
  for (const [key, value] of Object.entries(details)) assert.equal(reset[key], value)
  const cleared = await patch({ gender: 'unspecified', phone: '', location: '', bio: '' })
  assert.equal(cleared.gender, 'unspecified')
  assert.equal(cleared.bio, '')
})

test('concurrent profile changes preserve both writes', async () => {
  const token = await login()
  await Promise.all([
    mockRequest('/auth/profile', { token, method: 'PATCH', body: { phone: '123456' } }),
    mockRequest('/auth/profile', { token, method: 'PATCH', body: { bio: '并发保存的介绍' } }),
  ])
  const me = await mockRequest('/auth/me', { token })
  assert.equal(me.phone, '123456')
  assert.equal(me.bio, '并发保存的介绍')
})

test('credentials, account state and session expiry are enforced', async () => {
  await assert.rejects(login('admin', 'incorrect'), { code: 401 })
  const token = await login()
  const me = await mockRequest('/auth/me', { token })
  assert.equal(me.password, undefined)
  assert.deepEqual(me.permissions, ['*'])
  const db = await readDatabase()
  db.sessions[token].expiresAt = 0
  await writeDatabase(db)
  await assert.rejects(mockRequest('/users', { token }), { code: 401 })
})
test('viewer can read but cannot write; editor cannot access role management or assign admin', async () => {
  const token = await login('viewer')
  assert.equal((await mockRequest('/users', { token })).total, 3)
  await assert.rejects(mockRequest('/users', { token, method: 'POST', body: {} }), { code: 403 })
  await assert.rejects(mockRequest('/roles', { token }), { code: 403 })
  const editor = await login('editor')
  const roles = await mockRequest('/auth/roles', { token: editor })
  assert.equal(
    roles.some((r) => r.roleKey === 'admin'),
    false,
  )
  await assert.rejects(
    mockRequest('/users', {
      token: editor,
      method: 'POST',
      body: {
        username: 'elevated',
        realName: 'Test',
        password: 'test12345',
        role: 'admin',
        status: 1,
      },
    }),
    { code: 403 },
  )
})
test('CRUD persists, hides passwords, rejects duplicate keys and records audit events', async () => {
  const token = await login()
  const body = {
    username: 'test',
    realName: 'Test',
    role: 'viewer',
    password: 'test12345',
    status: 1,
  }
  await mockRequest('/users', { token, method: 'POST', body })
  await assert.rejects(mockRequest('/users', { token, method: 'POST', body }), { code: 400 })
  const result = await mockRequest('/users?keyword=test&page=1&pageSize=1', { token })
  assert.equal(result.total, 1)
  assert.equal(result.list[0].password, undefined)
  const id = result.list[0].id
  await mockRequest(`/users/${id}`, { token, method: 'PATCH', body: { realName: 'Changed' } })
  assert.equal((await mockRequest('/users?keyword=Changed', { token })).total, 1)
  await mockRequest(`/users/${id}`, { token, method: 'DELETE' })
  assert.equal((await mockRequest('/users?keyword=Changed', { token })).total, 0)
  assert.equal((await mockRequest('/logs?category=operation', { token })).total, 3)
})
test('built-in administrator and assigned roles are protected', async () => {
  const token = await login()
  await assert.rejects(mockRequest('/users/u-admin', { token, method: 'DELETE' }), { code: 400 })
  await assert.rejects(
    mockRequest('/roles/r-admin', { token, method: 'PATCH', body: { status: 0 } }),
    { code: 400 },
  )
  await assert.rejects(mockRequest('/roles/r-viewer', { token, method: 'DELETE' }), { code: 400 })
})
test('password change checks old password and revokes existing sessions', async () => {
  const token = await login('viewer')
  await assert.rejects(
    mockRequest('/auth/password', {
      token,
      method: 'POST',
      body: { oldPassword: 'wrong', newPassword: 'newpassword123' },
    }),
    { code: 400 },
  )
  await mockRequest('/auth/password', {
    token,
    method: 'POST',
    body: { oldPassword: 'viewer123', newPassword: 'newpassword123' },
  })
  await assert.rejects(mockRequest('/auth/me', { token }), { code: 401 })
  await assert.rejects(login('viewer'), { code: 401 })
  assert.ok(await login('viewer', 'newpassword123'))
})
test('role changes affect active sessions and settings persist', async () => {
  const token = await login(),
    viewer = await login('viewer')
  await mockRequest('/roles/r-viewer', {
    token,
    method: 'PATCH',
    body: { permissions: [], status: 1 },
  })
  await assert.rejects(mockRequest('/users', { token: viewer }), { code: 403 })
  await mockRequest('/settings', { token, method: 'PATCH', body: { siteName: 'Example' } })
  assert.equal((await mockRequest('/settings', { token })).siteName, 'Example')
})
test('permissions deny absent grants and allow explicit or wildcard access', () => {
  assert.equal(hasPermission([], 'system:users:read'), false)
  assert.equal(hasPermission(['*'], 'system:users:create'), true)
  assert.equal(
    hasPermission(['system:users:read'], ['system:users:read', 'system:roles:read']),
    true,
  )
})
