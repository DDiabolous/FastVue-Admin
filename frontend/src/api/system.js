import { request } from './request.js'
export const authApi = {
  login: (username, password) =>
    request('/auth/login', { method: 'POST', body: { username, password } }),
  me: () => request('/auth/me'),
  logout: () => request('/auth/logout', { method: 'POST' }),
  profile: (body) => request('/auth/profile', { method: 'PATCH', body }),
  password: (body) => request('/auth/password', { method: 'POST', body }),
}
export const resourceApi = (resource) => ({
  list: (params) => request(`/${resource}?${new URLSearchParams(params)}`),
  create: (body) => request(`/${resource}`, { method: 'POST', body }),
  update: (id, body) =>
    request(`/${resource}/${encodeURIComponent(id)}`, { method: 'PATCH', body }),
  remove: (id) => request(`/${resource}/${encodeURIComponent(id)}`, { method: 'DELETE' }),
})
export const settingsApi = {
  get: () => request('/settings'),
  save: (body) => request('/settings', { method: 'PATCH', body }),
}
