import { test } from 'node:test'
import assert from 'node:assert/strict'
import { normalizeAppearance, readPreference, writePreference } from '../src/utils/preferences.js'
import { storageKey } from '../src/config/app.js'

test('corrupted appearance settings fall back to safe supported values', () => {
  const defaults = { theme: 'light', accent: '#2563eb', density: 'comfortable', showPageTitle: true }
  assert.deepEqual(normalizeAppearance(null), defaults)
  assert.deepEqual(
    normalizeAppearance({ theme: 'invalid', accent: 'red; color:black', density: 'other' }),
    defaults,
  )
  assert.deepEqual(
    normalizeAppearance({ theme: 'system', accent: '#0d9488', density: 'compact' }),
    { theme: 'system', accent: '#0d9488', density: 'compact', showPageTitle: true },
  )
})

test('page titles default to visible and only a boolean false hides them', () => {
  assert.equal(normalizeAppearance({}).showPageTitle, true)
  assert.equal(normalizeAppearance({ showPageTitle: false }).showPageTitle, false)
  assert.equal(normalizeAppearance({ showPageTitle: 'false' }).showPageTitle, true)
})

test('preferences use app namespace and recover from invalid JSON or unavailable storage', () => {
  const values = new Map()
  globalThis.localStorage = {
    getItem: (key) => values.get(key) ?? null,
    setItem: (key, value) => values.set(key, value),
  }
  writePreference('appearance', { theme: 'dark' })
  assert.deepEqual(readPreference('appearance', {}), { theme: 'dark' })
  assert.ok(values.has(storageKey('appearance')))
  values.set(storageKey('appearance'), '{invalid')
  assert.deepEqual(readPreference('appearance', { theme: 'light' }), { theme: 'light' })
  globalThis.localStorage = {
    getItem() {
      throw new Error('blocked')
    },
    setItem() {
      throw new Error('full')
    },
  }
  assert.deepEqual(readPreference('appearance', {}), {})
  assert.doesNotThrow(() => writePreference('appearance', {}))
})
