import { test, beforeEach } from 'node:test'
import assert from 'node:assert/strict'
import { createPinia, setActivePinia } from 'pinia'
import { useExampleProjects } from '../src/stores/exampleProjects.js'

beforeEach(() => setActivePinia(createPinia()))
test('projects share creates, edits and deletes without changing other records', () => {
  const store = useExampleProjects()
  const initial = store.projects.length
  const input = {
    name: '新项目',
    code: 'PRJ-013',
    category: '产品研发',
    owner: '林晓',
    dates: ['2026-11-01', '2026-12-01'],
    budget: 1000,
    status: 'planned',
    progress: 0,
    description: '',
  }
  const created = store.save(input)
  input.dates[0] = '2027-01-01'
  assert.equal(created.dates[0], '2026-11-01')
  assert.equal(store.projects.length, initial + 1)
  const updated = store.save({ ...created, name: '更新项目' })
  assert.equal(updated.name, '更新项目')
  assert.equal(updated.events.length, 2)
  assert.equal(store.projects.length, initial + 1)
  store.remove([created.id])
  assert.equal(store.projects.length, initial)
})
test('duplicate project codes are rejected without overwriting data', () => {
  const store = useExampleProjects()
  const before = JSON.stringify(store.projects)
  assert.throws(() => store.save({ code: store.projects[0].code, dates: [] }), /编号已存在/)
  assert.equal(JSON.stringify(store.projects), before)
})
