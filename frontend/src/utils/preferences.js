import { storageKey } from '../config/app.js'

export function readPreference(key, fallback) {
  try {
    return JSON.parse(localStorage.getItem(storageKey(key))) ?? fallback
  } catch {
    return fallback
  }
}
export function writePreference(key, value) {
  try {
    localStorage.setItem(storageKey(key), JSON.stringify(value))
  } catch {
    /* Preferences remain usable in memory when storage is unavailable. */
  }
}
export const accents = [
  { label: '靛蓝', value: '#4f46e5' },
  { label: '蓝色', value: '#2563eb' },
  { label: '青绿', value: '#0d9488' },
  { label: '紫色', value: '#7c3aed' },
  { label: '玫红', value: '#e11d48' },
]
export function normalizeAppearance(value = {}) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) value = {}
  return {
    theme: ['light', 'dark', 'system'].includes(value.theme) ? value.theme : 'light',
    accent: accents.some((item) => item.value === value.accent) ? value.accent : '#2563eb',
    density: value.density === 'compact' ? 'compact' : 'comfortable',
  }
}
