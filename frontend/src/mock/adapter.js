import { readDatabase, writeDatabase, appendLog } from './database.js'
import { hasPermission, permissionOptions } from '../config/permissions.js'

const fail = (code, message) => {
  throw Object.assign(new Error(message), { code })
}
const publicUser = (db, user) => {
  const role = db.roles.find((r) => r.roleKey === user.role && r.status === 1)
  const { password, ...info } = user
  return { ...info, roleName: role?.roleName || '未分配角色', permissions: role?.permissions || [] }
}
let pendingRequest = Promise.resolve()

export function mockRequest(path, options = {}) {
  // Keep each read/modify/write sequence together while storage is asynchronous.
  const result = pendingRequest.then(() => handleMockRequest(path, options))
  pendingRequest = result.then(() => undefined, () => undefined)
  return result
}

async function handleMockRequest(path, { method = 'GET', body, token } = {}) {
  if (!path.startsWith('/admin/')) fail(404, '接口不存在')
  path = path.slice('/admin'.length)
  path = path.replace(/^\/accounts(?=[/?]|$)/, '/users')
  const db = await readDatabase()
  const url = new URL(path, 'http://demo.local')
  const parts = url.pathname.split('/').filter(Boolean)
  if (path === '/auth/login' && method === 'POST') {
    const user = db.users.find(
      (u) => u.username === body.username && u.password === body.password && u.status === 1,
    )
    if (!user) fail(401, '账号或密码错误，或账号已停用')
    const sessionToken = crypto.randomUUID()
    db.sessions[sessionToken] = {
      userId: user.id,
      expiresAt: Date.now() + 8 * 3600_000,
      createdAt: Date.now(),
      ip: '127.0.0.1',
      device: 'Desktop / Chrome (Web)',
    }
    appendLog(db, user.username, '登录成功', '登录', 'login')
    await writeDatabase(db)
    return { token: sessionToken, user: publicUser(db, user) }
  }
  const session = db.sessions[token]
  const user = db.users.find((u) => u.id === session?.userId && u.status === 1)
  if (!user || session.expiresAt < Date.now()) fail(401, '登录已失效，请重新登录')
  const permissions = publicUser(db, user).permissions
  const canManage = (role) =>
    permissions.includes('*') || role.permissions.every((key) => hasPermission(permissions, key))
  const canAssign = (role) => role.status === 1 && canManage(role)
  if (path === '/auth/roles') {
    if (
      !hasPermission(publicUser(db, user).permissions, 'system:users:create') &&
      !hasPermission(publicUser(db, user).permissions, 'system:users:update')
    )
      fail(403, '没有操作权限')
    return db.roles.filter(canAssign).map(({ roleKey, roleName }) => ({ roleKey, roleName }))
  }
  if (path === '/me' && method === 'GET') return publicUser(db, user)
  if (path === '/auth/sessions' && method === 'GET') {
    return Object.entries(db.sessions)
      .filter(([_, s]) => s.userId === user.id && s.expiresAt > Date.now())
      .map(([k, s]) => ({
        tokenHash: k,
        device: s.device || 'Chrome / Web Browser',
        ip: s.ip || '127.0.0.1',
        createdAt: s.createdAt ? new Date(s.createdAt).toLocaleString() : '最近登录',
        expiresAt: new Date(s.expiresAt).toLocaleString(),
        isCurrent: k === token,
      }))
  }
  if (path.startsWith('/auth/sessions/') && method === 'DELETE') {
    const targetHash = decodeURIComponent(parts[2] || '')
    if (db.sessions[targetHash]?.userId === user.id) {
      delete db.sessions[targetHash]
      await writeDatabase(db)
    }
    return null
  }
  if (path === '/auth/logout' && method === 'POST') {
    delete db.sessions[token]
    appendLog(db, user.username, '退出登录', '登录', 'login')
    await writeDatabase(db)
    return null
  }
  if (path === '/me' && method === 'PATCH') {
    if (body.realName !== undefined) user.realName = String(body.realName || user.username)
    if (body.email !== undefined) user.email = String(body.email || '')
    for (const field of ['gender', 'phone', 'location', 'bio']) {
      if (body[field] !== undefined) user[field] = String(body[field])
    }
    if (body.avatar !== undefined) user.avatar = String(body.avatar)
    if (body.coverImage !== undefined) user.coverImage = String(body.coverImage || '')
    appendLog(db, user.username, '更新个人资料', user.username)
    await writeDatabase(db)
    return publicUser(db, user)
  }
  if (path === '/auth/password' && method === 'POST') {
    if (body.oldPassword !== user.password) fail(400, '当前密码不正确')
    if (!body.newPassword || body.newPassword.length < 8) fail(400, '新密码至少 8 位')
    user.password = body.newPassword
    for (const [key, value] of Object.entries(db.sessions))
      if (value.userId === user.id) delete db.sessions[key]
    appendLog(db, user.username, '修改密码', user.username)
    await writeDatabase(db)
    return null
  }
  const [resource, id] = parts
  if (!['users', 'roles', 'dictionary', 'settings', 'logs'].includes(resource))
    fail(404, '接口不存在')
  const action = { GET: 'read', POST: 'create', PATCH: 'update', DELETE: 'delete' }[method]
  if (!action || !hasPermission(publicUser(db, user).permissions, `system:${resource}:${action}`))
    fail(403, '没有操作权限')
  if (resource === 'settings') {
    if (method === 'GET') return db.settings
    if (method !== 'PATCH') fail(405, '不支持的操作')
    db.settings = {
      siteName: String(body.siteName || ''),
      description: String(body.description || ''),
      contactEmail: String(body.contactEmail || ''),
      registration: String(body.registration || ''),
    }
    appendLog(db, user.username, '更新系统配置', '系统配置')
    await writeDatabase(db)
    return db.settings
  }
  if (method === 'GET') {
    const keyword = (url.searchParams.get('keyword') || '').toLowerCase()
    const category = url.searchParams.get('category')
    const list = db[resource].filter(
      (row) =>
        (!category || row.category === category) &&
        Object.entries(row).some(
          ([key, value]) => key !== 'password' && String(value).toLowerCase().includes(keyword),
        ),
    )
    const page = Math.max(1, Number(url.searchParams.get('page')) || 1)
    const pageSize = Math.min(200, Math.max(1, Number(url.searchParams.get('pageSize')) || 10))
    return {
      list: list
        .slice((page - 1) * pageSize, page * pageSize)
        .map((row) => (resource === 'users' ? publicUser(db, row) : row)),
      total: list.length,
    }
  }
  if (resource === 'logs') fail(405, '日志只读')
  const index = db[resource].findIndex((row) => row.id === id)
  if (method !== 'POST' && index < 0) fail(404, '记录不存在')
  const current = db[resource][index]
  if (resource === 'users' && current?.username === 'admin')
    fail(400, '内置管理员请通过个人中心修改资料')
  if (resource === 'roles' && current?.roleKey === 'admin')
    fail(400, '内置管理员角色不可修改或删除')
  if (method === 'DELETE') {
    if (resource === 'users' && id === user.id) fail(400, '不能删除当前账号')
    if (resource === 'users' && !db.roles.some((r) => r.roleKey === current.role && canManage(r)))
      fail(403, '不能删除超出自身权限的账号')
    if (resource === 'roles' && db.users.some((u) => u.role === current.roleKey))
      fail(400, '角色已被用户使用，请先调整用户角色')
    db[resource].splice(index, 1)
  } else {
    const fields = {
      users: ['username', 'realName', 'email', 'role', 'status'],
      roles: ['roleKey', 'roleName', 'description', 'permissions', 'status'],
      dictionary: ['type', 'label', 'value', 'sort', 'status'],
    }[resource]
    const data = Object.fromEntries(
      fields.filter((key) => body[key] !== undefined).map((key) => [key, body[key]]),
    )
    const key = { users: 'username', roles: 'roleKey', dictionary: 'value' }[resource]
    const merged = { ...current, ...data }
    const required = {
      users: ['username', 'realName', 'role'],
      roles: ['roleKey', 'roleName'],
      dictionary: ['type', 'label', 'value'],
    }[resource]
    if (required.some((field) => !String(merged[field] ?? '').trim())) fail(400, '请填写必填字段')
    if (
      db[resource].some(
        (row) =>
          row.id !== id &&
          row[key] === merged[key] &&
          (resource !== 'dictionary' || row.type === merged.type),
      )
    )
      fail(400, '标识已存在')
    if (resource === 'users') {
      if (!db.roles.some((r) => r.roleKey === merged.role && canAssign(r)))
        fail(403, '不能分配超出自身权限的角色')
      if (current && !db.roles.some((r) => r.roleKey === current.role && canManage(r)))
        fail(403, '不能修改超出自身权限的账号')
      if (method === 'POST' || body.password) {
        if (!body.password || body.password.length < 8) fail(400, '密码至少 8 位')
        data.password = body.password
      }
    }
    if (resource === 'roles') {
      if (
        current &&
        merged.roleKey !== current.roleKey &&
        db.users.some((u) => u.role === current.roleKey)
      )
        fail(400, '已使用的角色不能修改标识')
      if (
        data.permissions &&
        data.permissions.some((p) => p !== '*' && !permissionOptions.some((o) => o.value === p))
      )
        fail(400, '权限码无效')
    }
    if (method === 'POST')
      db[resource].unshift({
        ...data,
        id: crypto.randomUUID(),
        createdAt: new Date().toLocaleString('zh-CN'),
      })
    else {
      Object.assign(current, data)
      if (resource === 'users' && (data.password || data.status === 0)) {
        for (const [key, value] of Object.entries(db.sessions))
          if (value.userId === id) delete db.sessions[key]
      }
    }
  }
  appendLog(
    db,
    user.username,
    `${{ POST: '新增', PATCH: '编辑', DELETE: '删除' }[method]}${resource}`,
    id || body.username || body.roleKey || body.label,
  )
  await writeDatabase(db)
  return null
}
