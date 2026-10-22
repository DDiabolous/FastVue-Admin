<template>
  <div class="base-chart-container" :style="{ width, height }">
    <div ref="chartEl" class="base-chart-canvas" />
    <div v-if="loading" class="chart-loading-overlay">
      <el-icon class="is-loading" :size="26"><Loading /></el-icon>
      <span class="loading-text">{{ loadingText }}</span>
    </div>
    <div v-else-if="empty" class="chart-empty-overlay">
      <el-empty :description="emptyText" :image-size="70" />
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useChart } from '@/composables/useChart'

const props = defineProps({
  options: {
    type: [Object, Function],
    required: true,
  },
  width: {
    type: String,
    default: '100%',
  },
  height: {
    type: String,
    default: '320px',
  },
  loading: {
    type: Boolean,
    default: false,
  },
  loadingText: {
    type: String,
    default: '数据载入中...',
  },
  empty: {
    type: Boolean,
    default: false,
  },
  emptyText: {
    type: String,
    default: '暂无图表数据',
  },
  renderer: {
    type: String,
    default: 'canvas',
  },
})

const emit = defineEmits(['chart-click', 'chart-init'])

const chartEl = ref(null)

const { chartInstance, resize, updateChart, getThemePalette, echarts } = useChart(
  chartEl,
  () => props.options,
  { renderer: props.renderer },
)

watch(
  () => props.options,
  () => {
    updateChart()
  },
  { deep: true },
)

watch(chartInstance, (ins) => {
  if (ins) {
    emit('chart-init', ins)
    ins.on('click', (params) => {
      emit('chart-click', params)
    })
  }
})

defineExpose({
  chartInstance,
  resize,
  updateChart,
  getThemePalette,
  echarts,
})
</script>

<style scoped>
.base-chart-container {
  position: relative;
  overflow: hidden;
}

.base-chart-canvas {
  width: 100%;
  height: 100%;
}

.chart-loading-overlay,
.chart-empty-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background-color: var(--card-bg, rgba(255, 255, 255, 0.85));
  backdrop-filter: blur(4px);
  z-index: 5;
}

.loading-text {
  font-size: 13px;
  color: var(--text-muted, #94a3b8);
}
</style>
