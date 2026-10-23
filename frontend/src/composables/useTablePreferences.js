import { computed, ref, watch } from 'vue'
import { useAdminStore } from '@/stores/admin'
import { readPreference, writePreference } from '@/utils/preferences'

export function useTablePreferences(name, columns) {
  const user = useAdminStore()
  const key = `table:${user.userInfo?.id || 'default'}:${name}`
  const saved = readPreference(key, {})
  const allowed = columns.map((column) => column.prop)
  const valid = Array.isArray(saved.visible)
    ? saved.visible.filter((prop) => allowed.includes(prop))
    : allowed
  const visible = ref(valid.length ? valid : allowed)
  const widths = ref(saved.widths && typeof saved.widths === 'object' ? saved.widths : {})
  const keyword = ref(typeof saved.keyword === 'string' ? saved.keyword : '')
  const appliedKeyword = ref(keyword.value)
  const page = ref(Number.isInteger(saved.page) && saved.page > 0 ? saved.page : 1)
  const visibleColumns = computed(() =>
    columns
      .filter((column) => visible.value.includes(column.prop))
      .map((column) => ({
        ...column,
        width:
          Number(widths.value[column.prop]) >= 80
            ? Math.min(800, Number(widths.value[column.prop]))
            : undefined,
      })),
  )
  watch(
    [visible, widths, appliedKeyword, page],
    () =>
      writePreference(key, {
        visible: visible.value,
        widths: widths.value,
        keyword: appliedKeyword.value,
        page: page.value,
      }),
    { deep: true },
  )
  function resize(newWidth, _, column) {
    if (allowed.includes(column.property))
      widths.value[column.property] = Math.max(80, Math.min(newWidth, 800))
  }
  function resetColumns() {
    visible.value = [...allowed]
    widths.value = {}
  }
  return { keyword, appliedKeyword, page, visible, visibleColumns, resize, resetColumns }
}
