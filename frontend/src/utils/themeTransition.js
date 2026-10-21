// Animate the dark layer: reveal it from the trigger, or retract it back into the trigger.
export async function transitionTheme({ dark, trigger, update }) {
  if (
    !document.startViewTransition ||
    window.matchMedia('(prefers-reduced-motion: reduce)').matches
  ) {
    update()
    return
  }

  const rect = trigger?.getBoundingClientRect()
  const x = rect ? rect.left + rect.width / 2 : window.innerWidth / 2
  const y = rect ? rect.top + rect.height / 2 : window.innerHeight / 2
  const radius = Math.hypot(Math.max(x, window.innerWidth - x), Math.max(y, window.innerHeight - y))
  const circle = [`circle(0px at ${x}px ${y}px)`, `circle(${radius}px at ${x}px ${y}px)`]
  const root = document.documentElement
  root.style.setProperty('--theme-reveal-origin', `${x}px ${y}px`)
  root.style.setProperty('--theme-reveal-radius', `${radius}px`)
  root.dataset.themeTransition = dark ? 'expand' : 'retract'
  let updated = false
  let animation
  const apply = async () => {
    updated = true
    await update()
  }

  try {
    const transition = document.startViewTransition(apply)
    await transition.ready
    animation = root.animate(
      { clipPath: dark ? circle : [...circle].reverse() },
      {
        duration: dark ? 500 : 420,
        easing: 'cubic-bezier(0.4, 0, 0.2, 1)',
        fill: 'both',
        pseudoElement: dark ? '::view-transition-new(root)' : '::view-transition-old(root)',
      },
    )
    await animation.finished
    await transition.finished
  } catch {
    // A skipped or unsupported snapshot must never prevent the theme from changing.
    if (!updated) await apply()
  } finally {
    // fill: both is needed while the snapshots exist, but retaining it would apply
    // the previous circle to the next transition's pseudo-element of the same name.
    animation?.cancel()
    delete root.dataset.themeTransition
    root.style.removeProperty('--theme-reveal-origin')
    root.style.removeProperty('--theme-reveal-radius')
  }
}
