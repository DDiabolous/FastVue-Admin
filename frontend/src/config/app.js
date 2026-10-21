const env = import.meta.env || {}

export const appConfig = Object.freeze({
  name: env.VITE_APP_TITLE || 'FastVue-Admin',
  description: '面向各类业务的后台开发底座',
  storagePrefix: env.VITE_STORAGE_PREFIX || 'fastvue',
  apiBaseUrl: env.VITE_API_BASE_URL || '/api',
  useMock: env.VITE_USE_MOCK !== 'false',
  fullDemo: env.VITE_APP_PRESET === 'full',
  organization: env.VITE_ENABLE_ORGANIZATION === 'true',
})

export const storageKey = (name) => `${appConfig.storagePrefix}:${name}`
