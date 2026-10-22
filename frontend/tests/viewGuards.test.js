import test from 'node:test'
import assert from 'node:assert/strict'
import { registerViewGuard, confirmViewDiscard } from '../src/utils/viewGuards.js'

test('refresh is cancelled when an active form refuses to discard changes', async () => {
  const unregister = registerViewGuard(async () => false)
  try {
    assert.equal(await confirmViewDiscard(), false)
  } finally {
    unregister()
  }
  assert.equal(await confirmViewDiscard(), true)
})

test('all active forms must allow refresh and disposed forms no longer block it', async () => {
  let confirmations = 0
  const unregister = registerViewGuard(async () => {
    confirmations++
    return true
  })
  const removeBlocker = registerViewGuard(async () => false)
  try {
    assert.equal(await confirmViewDiscard(), false)
    removeBlocker()
    assert.equal(await confirmViewDiscard(), true)
    assert.equal(confirmations, 2)
  } finally {
    unregister()
    removeBlocker()
  }
})
