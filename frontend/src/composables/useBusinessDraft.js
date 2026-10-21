import { computed, ref, watch } from 'vue'
import { useUnsavedChanges } from './useUnsavedChanges'

export function useBusinessDraft(visible, form, saving) {
  const baseline = ref('')
  watch(
    visible,
    (open) => {
      if (open) baseline.value = JSON.stringify(form)
    },
    { flush: 'post' },
  )
  const dirty = computed(() => visible.value && baseline.value !== JSON.stringify(form))
  const { confirmDiscard } = useUnsavedChanges(dirty)
  return {
    async close() {
      if (!saving.value && (await confirmDiscard())) visible.value = false
    },
    async beforeClose(done) {
      if (!saving.value && (await confirmDiscard())) done()
    },
  }
}
