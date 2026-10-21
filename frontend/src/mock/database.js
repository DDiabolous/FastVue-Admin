import { storageKey } from '../config/app.js'
import { permissionOptions } from '../config/permissions.js'

const now = () => new Date().toLocaleString('zh-CN', { hour12: false })
export function createDatabase() {
  return {
    users: [
      {
        id: 'u-admin',
        username: 'admin',
        password: 'admin123',
        realName: '管理员',
        role: 'admin',
        email: 'admin@example.com',
        status: 1,
        createdAt: now(),
      },
      {
        id: 'u-editor',
        username: 'editor',
        password: 'editor123',
        realName: '编辑用户',
        role: 'editor',
        email: 'editor@example.com',
        status: 1,
        createdAt: now(),
      },
      {
        id: 'u-viewer',
        username: 'viewer',
        password: 'viewer123',
        realName: '只读用户',
        role: 'viewer',
        email: 'viewer@example.com',
        status: 1,
        createdAt: now(),
      },
    ],
    roles: [
      {
        id: 'r-admin',
        roleKey: 'admin',
        roleName: '管理员',
        description: '管理全部系统功能',
        permissions: ['*'],
        status: 1,
        createdAt: now(),
      },
      {
        id: 'r-editor',
        roleKey: 'editor',
        roleName: '编辑',
        description: '维护用户和数据字典',
        permissions: permissionOptions
          .filter((p) => ['users', 'dictionary'].includes(p.value.split(':')[1]))
          .map((p) => p.value),
        status: 1,
        createdAt: now(),
      },
      {
        id: 'r-viewer',
        roleKey: 'viewer',
        roleName: '只读用户',
        description: '查看用户和数据字典',
        permissions: ['system:users:read', 'system:dictionary:read'],
        status: 1,
        createdAt: now(),
      },
    ],
    dictionary: [
      {
        id: 'd-1',
        type: 'common_status',
        label: '启用',
        value: '1',
        sort: 1,
        status: 1,
        createdAt: now(),
      },
      {
        id: 'd-2',
        type: 'common_status',
        label: '停用',
        value: '0',
        sort: 2,
        status: 1,
        createdAt: now(),
      },
      {
        id: 'd-3',
        type: 'notice_type',
        label: '系统通知',
        value: 'system',
        sort: 1,
        status: 1,
        createdAt: now(),
      },
    ],
    settings: {
      siteName: 'FastVue-Admin',
      description: '面向各类业务的后台开发底座',
      contactEmail: '',
      registration: '',
    },
    logs: [],
    sessions: {},
  }
}
export function readDatabase() {
  try {
    const value = JSON.parse(localStorage.getItem(storageKey('demo-v1')))
    if (value?.users && value?.roles && value?.sessions) return value
  } catch {
    /* Reset invalid demo data only. */
  }
  const db = createDatabase()
  writeDatabase(db)
  return db
}
export function writeDatabase(db) {
  localStorage.setItem(storageKey('demo-v1'), JSON.stringify(db))
}
export function appendLog(
  db,
  operator,
  action,
  target,
  category = 'operation',
  status = 'success',
) {
  db.logs.unshift({
    id: crypto.randomUUID(),
    time: now(),
    operator,
    action,
    target,
    category,
    status,
    ip: '127.0.0.1',
  })
  db.logs = db.logs.slice(0, 500)
}
