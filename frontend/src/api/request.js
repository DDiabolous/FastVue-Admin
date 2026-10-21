import { appConfig, storageKey } from '../config/app.js'

export async function request(path, { method = 'GET', body } = {}) {
  const token = localStorage.getItem(storageKey('token')) || ''
  try {
    if (appConfig.useMock) {
      const { mockRequest } = await import('../mock/adapter.js')
      return await mockRequest(path, { method, body, token })
    }
    const response = await fetch(`${appConfig.apiBaseUrl.replace(/\/$/, '')}${path}`, {
      method,
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      ...(body === undefined ? {} : { body: JSON.stringify(body) }),
    })
    const result = await response.json().catch(() => ({}))
    if (!response.ok || result.code !== 200) {
      throw Object.assign(new Error(result.message || `请求失败 (${response.status})`), {
        code: response.ok ? result.code : response.status,
      })
    }
    return result.data
  } catch (error) {
    if (error.code === 401 && token) {
      localStorage.removeItem(storageKey('token'))
      window.dispatchEvent(new Event('auth-expired'))
    }
    throw error
  }
}
