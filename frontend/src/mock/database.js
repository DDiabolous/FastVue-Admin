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
const legacyKey = storageKey('demo-v1')
let databasePromise

function storageError(error) {
  return new Error(
    error?.name === 'QuotaExceededError'
      ? '浏览器存储空间不足，请释放本站存储空间或更换浏览器后重试'
      : '无法读写演示数据，请检查浏览器存储权限后重试',
    { cause: error },
  )
}

function readLegacyDatabase() {
  try {
    const value = JSON.parse(localStorage.getItem(legacyKey))
    if (value?.users && value?.roles && value?.sessions) return value
  } catch {
    /* Ignore malformed legacy data; never delete it before a successful migration. */
  }
  return null
}

function openDatabase() {
  if (!databasePromise) {
    databasePromise = new Promise((resolve, reject) => {
      const request = indexedDB.open(storageKey('demo-v2'), 1)
      request.onupgradeneeded = () => request.result.createObjectStore('database')
      request.onerror = () => reject(request.error)
      request.onsuccess = () => {
        const connection = request.result
        connection.onversionchange = () => {
          connection.close()
          databasePromise = undefined
        }
        resolve(connection)
      }
    }).catch((error) => {
      databasePromise = undefined
      throw error
    })
  }
  return databasePromise
}

async function databaseTransaction(mode, value) {
  const connection = await openDatabase()
  return new Promise((resolve, reject) => {
    const transaction = connection.transaction('database', mode)
    const store = transaction.objectStore('database')
    const request = mode === 'readonly' ? store.get('main') : store.put(value, 'main')
    transaction.oncomplete = () => resolve(request.result)
    transaction.onerror = () => reject(transaction.error)
    transaction.onabort = () => reject(transaction.error)
  })
}

export async function readDatabase() {
  // The Node test environment has no IndexedDB; browsers use the async store.
  if (typeof indexedDB === 'undefined') {
    const value = readLegacyDatabase()
    if (value) return value
    const db = createDatabase()
    await writeDatabase(db)
    return db
  }
  try {
    const stored = await databaseTransaction('readonly')
    if (stored?.users && stored?.roles && stored?.sessions) return stored
  } catch (error) {
    throw storageError(error)
  }
  const db = readLegacyDatabase() || createDatabase()
  await writeDatabase(db)
  return db
}

export async function writeDatabase(db) {
  try {
    if (typeof indexedDB === 'undefined') {
      localStorage.setItem(legacyKey, JSON.stringify(db))
      return
    }
    await databaseTransaction('readwrite', db)
  } catch (error) {
    throw storageError(error)
  }
  // Only remove the legacy copy after the IndexedDB transaction commits.
  try {
    localStorage.removeItem(legacyKey)
  } catch {
    /* The committed database is usable even if legacy cleanup is restricted. */
  }
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
