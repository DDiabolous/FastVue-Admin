import { request } from './adminRequest.js'
export const adminAuthApi = {
  login: (username, password) =>
    request('/admin/auth/login', { method: 'POST', body: { username, password } }),
  me: () => request('/admin/me'),
  logout: () => request('/admin/auth/logout', { method: 'POST' }),
  profile: (body) => request('/admin/me', { method: 'PATCH', body }),
  password: (body) => request('/admin/auth/password', { method: 'POST', body }),
  sessions: () => request('/admin/auth/sessions'),
  revokeSession: (id) => request(`/admin/auth/sessions/${encodeURIComponent(id)}`, { method: 'DELETE' }),
}
const resourcePath = (resource) => `/admin/${resource === 'users' ? 'accounts' : resource}`
export const resourceApi = (resource) => ({
  list: (params) => request(`${resourcePath(resource)}?${new URLSearchParams(params)}`),
  create: (body) => request(`${resourcePath(resource)}`, { method: 'POST', body }),
  update: (id, body) =>
    request(`${resourcePath(resource)}/${encodeURIComponent(id)}`, { method: 'PATCH', body }),
  remove: (id) => request(`${resourcePath(resource)}/${encodeURIComponent(id)}`, { method: 'DELETE' }),
})
export const settingsApi = {
  get: () => request('/admin/settings'),
  save: (body) => request('/admin/settings', { method: 'PATCH', body }),
}
