import { computed, watch, unref, onUnmounted } from 'vue'
import { useTablePreferences } from './useTablePreferences'
import { useAdminStore } from '@/stores/admin'
import { readPreference, writePreference } from '@/utils/preferences'

// Keep rich business cell slots in the page while sharing table and filter preferences.
export function useBusinessTable(name, columns, options) {
  const table = useTablePreferences(`business-${name}`, columns)
  table.visible.value = [
    ...new Set([
      ...table.visible.value,
      ...columns.filter((column) => column.locked).map((column) => column.prop),
    ]),
  ]
  const user = useAdminStore()
  const key = `business:${user.userInfo?.id || 'default'}:${name}`
  const saved = readPreference(key, {})
  for (const [field, initial] of Object.entries(options.query)) {
    const value = saved.query?.[field]
    if (
      Array.isArray(initial)
        ? Array.isArray(value)
        : typeof value === typeof initial || (initial === '' && typeof value === 'number')
    )
      options.query[field] = value
  }
  if (options.pagination) {
    if (Number.isInteger(saved.page) && saved.page > 0) options.pagination.currentPage = saved.page
    if ((options.pageSizes || [10, 20, 50, 100]).includes(saved.pageSize))
      options.pagination.pageSize = saved.pageSize
  }
  if (options.viewMode && ['table', 'card'].includes(saved.viewMode))
    options.viewMode.value = saved.viewMode
  if (options.viewMode) {
    // 切换视图模式（如网格卡片切回表格）时，由于表格组件多阶段渲染可能造成容器高度短暂塌陷，
    // 导致浏览器原生将滚动条截断强制归零（跳回顶部）。此处在 DOM 更新前锁定页面最小高度并记录位置，
    // 渲染完成后释放锁并保持滚动位置连续，避免跳顶。
    let switchToken = 0
    let activePageEl = null
    watch(
      () => unref(options.viewMode),
      (newMode, oldMode) => {
        if (!oldMode || newMode === oldMode) return
        if (typeof document === 'undefined') return
        const scrollEl = document.querySelector('.content-container')
        if (!scrollEl) return
        const prevScrollTop = scrollEl.scrollTop
        const pageEl = scrollEl.firstElementChild
        if (pageEl && prevScrollTop > 0) {
          activePageEl = pageEl
          const currentToken = ++switchToken
          const prevHeight = pageEl.offsetHeight
          pageEl.style.minHeight = `${prevHeight}px`
          const restore = () => {
            if (switchToken === currentToken) {
              if (pageEl) pageEl.style.minHeight = ''
              activePageEl = null
            }
            if (scrollEl && scrollEl.scrollTop !== prevScrollTop) {
              scrollEl.scrollTop = prevScrollTop
            }
          }
          if (typeof requestAnimationFrame !== 'undefined') {
            requestAnimationFrame(() => {
              requestAnimationFrame(restore)
            })
          } else {
            setTimeout(restore, 50)
          }
        }
      },
      { flush: 'pre' },
    )
    onUnmounted(() => {
      if (activePageEl) activePageEl.style.minHeight = ''
    })
  }
  for (const key of ['showStats', 'showMoreFilter'])
    if (options[key] && typeof saved[key] === 'boolean') options[key].value = saved[key]
  watch(
    () => ({
      query: { ...options.query },
      page: options.pagination?.currentPage,
      pageSize: options.pagination?.pageSize,
      viewMode: unref(options.viewMode),
      showStats: unref(options.showStats),
      showMoreFilter: unref(options.showMoreFilter),
    }),
    (value) => writePreference(key, value),
    { deep: true },
  )
  if (options.pagination) {
    watch(
      [options.total, () => options.pagination.pageSize, () => unref(options.loading)],
      ([total, size, loading]) => {
        if (!loading)
          options.pagination.currentPage = Math.min(
            options.pagination.currentPage,
            Math.max(1, Math.ceil(total / size)),
          )
      },
    )
  }
  if (options.clearSelection)
    watch(
      () => [
        JSON.stringify(options.query),
        options.pagination?.currentPage,
        options.pagination?.pageSize,
        unref(options.viewMode),
      ],
      options.clearSelection,
    )
  const isFiltered = computed(() =>
    Object.values(options.query).some((value) =>
      Array.isArray(value)
        ? value.length > 0
        : value !== '' && value !== null && value !== undefined,
    ),
  )
  return {
    ...table,
    columns,
    isFiltered,
    isColumnVisible: (prop) =>
      columns.some((column) => column.prop === prop && column.locked) ||
      table.visible.value.includes(prop),
    columnWidth: (prop, fallback) =>
      table.visibleColumns.value.find((column) => column.prop === prop)?.width || fallback,
  }
}
