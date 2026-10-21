import { watchEffect } from 'vue'
import { useUserStore } from '@/stores/user'
const stops = new WeakMap()
export const authDirective = {
  mounted(el, binding) {
    const user = useUserStore()
    stops.set(
      el,
      watchEffect(() => {
        el.hidden = !user.can(binding.value)
      }),
    )
  },
  updated(el, binding) {
    el.hidden = !useUserStore().can(binding.value)
  },
  unmounted(el) {
    stops.get(el)?.()
    stops.delete(el)
  },
}
