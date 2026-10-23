import { watchEffect } from 'vue'
import { useAdminStore } from '@/stores/admin'
const stops = new WeakMap()
export const authDirective = {
  mounted(el, binding) {
    const user = useAdminStore()
    stops.set(
      el,
      watchEffect(() => {
        el.hidden = !user.can(binding.value)
      }),
    )
  },
  updated(el, binding) {
    el.hidden = !useAdminStore().can(binding.value)
  },
  unmounted(el) {
    stops.get(el)?.()
    stops.delete(el)
  },
}
