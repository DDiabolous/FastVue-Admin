import { ref, watch, onMounted, onUnmounted, unref, nextTick } from 'vue'
import * as echarts from 'echarts'
import { useAppStore } from '@/stores/app'

export function useChart(elRef, optionsGetter, config = {}) {
  const chartInstance = ref(null)
  const appStore = useAppStore()
  let resizeObserver = null
  let themeObserver = null

  const getThemePalette = () => {
    const isDark =
      appStore.isDark ||
      (typeof document !== 'undefined' && document.documentElement.classList.contains('dark'))
    const primary = appStore.accent || '#2563eb'
    return {
      isDark,
      primary,
      textColor: isDark ? '#94a3b8' : '#64748b',
      titleColor: isDark ? '#f8fafc' : '#1e293b',
      splitLineColor: isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.06)',
      axisLineColor: isDark ? '#334155' : '#e2e8f0',
      tooltipBg: isDark ? 'rgba(15, 23, 42, 0.92)' : 'rgba(255, 255, 255, 0.96)',
      tooltipBorder: isDark ? '#334155' : '#e2e8f0',
      tooltipText: isDark ? '#f8fafc' : '#0f172a',
      colors: [
        primary,
        '#10b981', // emerald
        '#f59e0b', // amber
        '#8b5cf6', // purple
        '#06b6d4', // cyan
        '#ec4899', // pink
        '#f43f5e', // rose
      ],
    }
  }

  const initChart = () => {
    if (!elRef.value) return
    if (chartInstance.value) {
      chartInstance.value.dispose()
    }
    chartInstance.value = echarts.init(elRef.value, null, {
      renderer: config.renderer || 'canvas',
    })
    updateChart()
  }

  const updateChart = () => {
    if (!chartInstance.value) return
    const palette = getThemePalette()
    let rawOption =
      typeof optionsGetter === 'function' ? optionsGetter(palette) : unref(optionsGetter)
    if (typeof rawOption === 'function') {
      rawOption = rawOption(palette)
    }
    if (!rawOption || typeof rawOption !== 'object') return
    chartInstance.value.setOption(rawOption, true)
  }

  const resize = () => {
    if (chartInstance.value) {
      chartInstance.value.resize({ animation: { duration: 250 } })
    }
  }

  onMounted(() => {
    nextTick(() => {
      initChart()
      if (typeof ResizeObserver !== 'undefined' && elRef.value) {
        resizeObserver = new ResizeObserver(() => {
          resize()
        })
        resizeObserver.observe(elRef.value)
      }
      if (typeof MutationObserver !== 'undefined' && typeof document !== 'undefined') {
        themeObserver = new MutationObserver(() => {
          updateChart()
        })
        themeObserver.observe(document.documentElement, {
          attributes: true,
          attributeFilter: ['class', 'data-theme'],
        })
      }
    })
  })

  // Re-render when theme, accent color or sidebar changes
  watch(
    () => [appStore.isDark, appStore.accent, appStore.sidebarCollapsed],
    () => {
      nextTick(() => {
        updateChart()
        resize()
      })
    },
  )

  // Watch options changes when a ref is passed
  if (typeof optionsGetter !== 'function') {
    watch(
      () => unref(optionsGetter),
      () => {
        updateChart()
      },
      { deep: true },
    )
  }

  onUnmounted(() => {
    if (resizeObserver) {
      resizeObserver.disconnect()
      resizeObserver = null
    }
    if (themeObserver) {
      themeObserver.disconnect()
      themeObserver = null
    }
    if (chartInstance.value) {
      chartInstance.value.dispose()
      chartInstance.value = null
    }
  })

  return {
    chartInstance,
    resize,
    updateChart,
    getThemePalette,
    echarts,
  }
}
