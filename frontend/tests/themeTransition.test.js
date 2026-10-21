import { test, beforeEach } from 'node:test'
import assert from 'node:assert/strict'
import { transitionTheme } from '../src/utils/themeTransition.js'

let root, captures, updates, reduced
beforeEach(() => {
  captures = []
  updates = 0
  reduced = false
  root = {
    dataset: {},
    style: { setProperty() {}, removeProperty() {} },
    animate: (frames, options) => {
      captures.push({ frames, options })
      return { finished: Promise.resolve(), cancel() {} }
    },
  }
  globalThis.window = {
    innerWidth: 1200,
    innerHeight: 800,
    matchMedia: () => ({ matches: reduced }),
  }
  globalThis.document = {
    documentElement: root,
    startViewTransition(update) {
      update()
      return { ready: Promise.resolve(), finished: Promise.resolve() }
    },
  }
})
const trigger = { getBoundingClientRect: () => ({ left: 980, top: 20, width: 40, height: 40 }) }
const update = () => {
  updates++
}

test('dark mode expands the new snapshot from the button to the farthest corner', async () => {
  await transitionTheme({ dark: true, trigger, update })
  assert.equal(updates, 1)
  assert.equal(captures[0].options.pseudoElement, '::view-transition-new(root)')
  assert.equal(captures[0].frames.clipPath[0], 'circle(0px at 1000px 40px)')
  assert.equal(captures[0].frames.clipPath[1], `circle(${Math.hypot(1000, 760)}px at 1000px 40px)`)
  assert.equal(root.dataset.themeTransition, undefined)
})
test('light mode retracts the old dark snapshot back into the button', async () => {
  await transitionTheme({ dark: false, trigger, update })
  assert.equal(captures[0].options.pseudoElement, '::view-transition-old(root)')
  assert.equal(captures[0].frames.clipPath[1], 'circle(0px at 1000px 40px)')
  assert.equal(updates, 1)
})
test('reduced motion or unavailable view transitions changes the theme directly', async () => {
  reduced = true
  await transitionTheme({ dark: true, trigger, update })
  reduced = false
  document.startViewTransition = undefined
  await transitionTheme({ dark: false, trigger, update })
  assert.equal(updates, 2)
  assert.equal(captures.length, 0)
})
test('a skipped transition keeps the applied theme and removes temporary state', async () => {
  document.startViewTransition = (apply) => {
    apply()
    return { ready: Promise.reject(new Error('skipped')), finished: Promise.resolve() }
  }
  await transitionTheme({ dark: true, trigger, update })
  assert.equal(updates, 1)
  assert.equal(root.dataset.themeTransition, undefined)
})

test('the snapshot mask is prepared before the theme update starts', async () => {
  const properties = new Map()
  root.style.setProperty = (key, value) => properties.set(key, value)
  root.style.removeProperty = (key) => properties.delete(key)
  document.startViewTransition = (apply) => {
    assert.equal(root.dataset.themeTransition, 'expand')
    assert.equal(properties.get('--theme-reveal-origin'), '1000px 40px')
    assert.ok(properties.get('--theme-reveal-radius').endsWith('px'))
    apply()
    return { ready: Promise.resolve(), finished: Promise.resolve() }
  }
  await transitionTheme({ dark: true, trigger, update })
  assert.equal(properties.size, 0)
})

test('the initial mask remains until the clip animation has finished', async () => {
  let finishAnimation
  root.animate = () => ({
    cancel() {},
    finished: new Promise((resolve) => {
      finishAnimation = resolve
    }),
  })
  const running = transitionTheme({ dark: true, trigger, update })
  await Promise.resolve()
  assert.equal(root.dataset.themeTransition, 'expand')
  finishAnimation()
  await running
  assert.equal(root.dataset.themeTransition, undefined)
})

test('repeated toggles release every filled animation instead of reusing stale masks', async () => {
  const retained = new Set()
  let cancelled = 0
  root.animate = () => {
    const animation = {
      finished: Promise.resolve(),
      cancel() {
        retained.delete(animation)
        cancelled++
      },
    }
    retained.add(animation)
    return animation
  }
  for (let index = 0; index < 10; index++) {
    await transitionTheme({ dark: index % 2 === 0, trigger, update })
    assert.equal(retained.size, 0, `toggle ${index + 1} left a filled snapshot animation`)
  }
  assert.equal(cancelled, 10)
  assert.equal(updates, 10)
})

test('the filled animation is released only after the native snapshots have finished', async () => {
  let finishTransition
  let cancelled = false
  document.startViewTransition = (apply) => {
    apply()
    return {
      ready: Promise.resolve(),
      finished: new Promise((resolve) => {
        finishTransition = resolve
      }),
    }
  }
  root.animate = () => ({
    finished: Promise.resolve(),
    cancel() {
      cancelled = true
    },
  })
  const running = transitionTheme({ dark: true, trigger, update })
  await Promise.resolve()
  await Promise.resolve()
  assert.equal(cancelled, false)
  finishTransition()
  await running
  assert.equal(cancelled, true)
  assert.equal(root.dataset.themeTransition, undefined)
})
