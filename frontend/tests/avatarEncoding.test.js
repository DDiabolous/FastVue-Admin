import test from 'node:test'
import assert from 'node:assert/strict'
import { encodeAvatar, MAX_AVATAR_DATA_URL_LENGTH } from '../src/utils/avatarEncoding.js'

test('small avatars retain their lossless PNG encoding', () => {
  assert.equal(encodeAvatar({ toDataURL: () => 'data:image/png;base64,small' }), 'data:image/png;base64,small')
})

test('large PNGs fall back to a compressed image within the request budget', () => {
  const formats = []
  const result = encodeAvatar({
    toDataURL(type) {
      formats.push(type)
      return type === 'image/png' ? 'x'.repeat(MAX_AVATAR_DATA_URL_LENGTH + 1) : 'data:image/webp;base64,small'
    },
  })
  assert.deepEqual(formats, ['image/png', 'image/webp'])
  assert.equal(result, 'data:image/webp;base64,small')
})

test('encodings that cannot fit the request budget are rejected', () => {
  assert.equal(encodeAvatar({ toDataURL: () => 'x'.repeat(MAX_AVATAR_DATA_URL_LENGTH + 1) }), '')
})
