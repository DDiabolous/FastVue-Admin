// Leave room for the JSON envelope below nginx's 1 MiB request limit.
export const MAX_AVATAR_DATA_URL_LENGTH = 900 * 1024

export function encodeAvatar(canvas) {
  for (const [type, quality] of [
    ['image/png', undefined],
    ['image/webp', 0.85],
    ['image/jpeg', 0.8],
    ['image/jpeg', 0.6],
  ]) {
    const encoded = canvas.toDataURL(type, quality)
    if (encoded.length <= MAX_AVATAR_DATA_URL_LENGTH) return encoded
  }
  return ''
}
