<template>
  <div class="charts-row">
    <!-- Left: Traffic & Requests Trend Chart -->
    <el-card shadow="never" class="chart-card trend-card">
      <template #header>
        <div class="card-header-flex">
          <div>
            <h3 class="chart-title">服务调用与业务流量趋势</h3>
            <p class="chart-subtitle">接口实时吞吐峰值与活跃访问用户数时序分析</p>
          </div>
          <div class="header-actions">
            <div class="time-range-tabs" role="tablist">
              <button
                type="button"
                role="tab"
                :aria-selected="timeRange === '7d'"
                class="range-tab"
                :class="{ 'is-active': timeRange === '7d' }"
                @click="timeRange = '7d'"
              >
                近 7 天
              </button>
              <button
                type="button"
                role="tab"
                :aria-selected="timeRange === '30d'"
                class="range-tab"
                :class="{ 'is-active': timeRange === '30d' }"
                @click="timeRange = '30d'"
              >
                近 30 天
              </button>
            </div>
          </div>
        </div>
      </template>

      <div class="chart-wrapper">
        <BaseChart :key="timeRange" :options="trendOptions" height="310px" />
      </div>
    </el-card>

    <!-- Right: Asset & Device Category Distribution Ring Chart -->
    <el-card shadow="never" class="chart-card category-card">
      <template #header>
        <div class="card-header-flex">
          <div>
            <h3 class="chart-title">终端资产结构分布</h3>
            <p class="chart-subtitle">各类边缘硬件终端与传感设备纳管占比</p>
          </div>
          <span class="total-tag">共 1,420 台</span>
        </div>
      </template>

      <div class="chart-wrapper">
        <BaseChart :options="categoryOptions" height="310px" />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import * as echarts from 'echarts'
import BaseChart from '@/components/charts/BaseChart.vue'

const timeRange = ref('7d')

// Mock datasets for 7d and 30d
const datasets = {
  '7d': {
    dates: ['10-16', '10-17', '10-18', '10-19', '10-20', '10-21', '10-22'],
    uv: [2480, 2890, 3120, 2950, 3480, 3890, 4210],
    requests: [520, 610, 680, 640, 780, 810, 842],
  },
  '30d': {
    dates: [
      '09-23', '09-26', '09-29', '10-02', '10-05', '10-08', '10-11', '10-14', '10-17', '10-20', '10-22',
    ],
    uv: [1890, 2150, 2300, 2580, 2410, 2890, 3100, 3350, 3620, 3950, 4210],
    requests: [380, 420, 470, 530, 490, 620, 690, 730, 770, 810, 842],
  },
}

const trendOptions = computed(() => (palette) => {
  const data = datasets[timeRange.value]
  const isDark = palette.isDark
  const primary = palette.primary

  return {
    tooltip: {
      trigger: 'axis',
      backgroundColor: palette.tooltipBg,
      borderColor: palette.tooltipBorder,
      borderWidth: 1,
      textStyle: {
        color: palette.tooltipText,
        fontSize: 12,
      },
      padding: [10, 14],
      extraCssText:
        'box-shadow: 0 12px 28px -4px rgba(0,0,0,0.22); border-radius: 8px; backdrop-filter: blur(8px);',
    },
    legend: {
      left: 'center',
      top: 0,
      icon: 'circle',
      itemWidth: 8,
      itemHeight: 8,
      itemGap: 24,
      textStyle: {
        color: palette.textColor,
        fontSize: 12,
      },
      data: ['活跃访问用户 (UV)', '接口调用量 (k)'],
    },
    grid: {
      left: 12,
      right: 20,
      top: 48,
      bottom: 10,
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: data.dates,
      axisLine: {
        lineStyle: {
          color: palette.axisLineColor,
        },
      },
      axisLabel: {
        color: palette.textColor,
        fontSize: 11,
      },
      axisTick: {
        show: false,
      },
    },
    yAxis: [
      {
        type: 'value',
        name: '用户数 (UV)',
        nameTextStyle: {
          color: palette.textColor,
          fontSize: 11,
          padding: [0, 0, 6, 0],
        },
        splitLine: {
          lineStyle: {
            color: palette.splitLineColor,
            type: 'dashed',
          },
        },
        axisLabel: {
          color: palette.textColor,
          fontSize: 11,
        },
      },
      {
        type: 'value',
        name: '吞吐量 (k)',
        nameTextStyle: {
          color: palette.textColor,
          fontSize: 11,
          padding: [0, 0, 6, 0],
        },
        splitLine: {
          show: false,
        },
        axisLabel: {
          color: palette.textColor,
          fontSize: 11,
        },
      },
    ],
    series: [
      {
        name: '活跃访问用户 (UV)',
        type: 'line',
        smooth: true,
        showSymbol: false,
        symbolSize: 6,
        itemStyle: {
          color: primary,
        },
        lineStyle: {
          width: 2.8,
          color: primary,
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: isDark ? 'rgba(59, 130, 246, 0.4)' : 'rgba(37, 99, 235, 0.28)' },
            { offset: 1, color: isDark ? 'rgba(59, 130, 246, 0.01)' : 'rgba(37, 99, 235, 0.01)' },
          ]),
        },
        data: data.uv,
      },
      {
        name: '接口调用量 (k)',
        type: 'line',
        yAxisIndex: 1,
        smooth: true,
        showSymbol: false,
        symbolSize: 6,
        itemStyle: {
          color: '#10b981',
        },
        lineStyle: {
          width: 2.8,
          color: '#10b981',
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(16, 185, 129, 0.26)' },
            { offset: 1, color: 'rgba(16, 185, 129, 0.01)' },
          ]),
        },
        data: data.requests,
      },
    ],
  }
})

const categoryOptions = computed(() => (palette) => {
  const isDark = palette.isDark

  return {
    tooltip: {
      trigger: 'item',
      backgroundColor: palette.tooltipBg,
      borderColor: palette.tooltipBorder,
      borderWidth: 1,
      textStyle: {
        color: palette.tooltipText,
        fontSize: 12,
      },
      padding: [8, 12],
      formatter: '{b}<br/><b>{c} 台</b> ({d}%)',
      extraCssText:
        'box-shadow: 0 10px 24px -4px rgba(0,0,0,0.22); border-radius: 8px; backdrop-filter: blur(8px);',
    },
    legend: {
      bottom: 2,
      left: 'center',
      icon: 'circle',
      itemWidth: 8,
      itemHeight: 8,
      itemGap: 14,
      textStyle: {
        color: palette.textColor,
        fontSize: 11,
      },
    },
    series: [
      {
        name: '终端设备类别',
        type: 'pie',
        radius: ['48%', '74%'],
        center: ['50%', '44%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 6,
          borderColor: isDark ? '#1e293b' : '#ffffff',
          borderWidth: 2,
        },
        label: {
          show: false,
          position: 'center',
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 14,
            fontWeight: '600',
            color: palette.titleColor,
            formatter: '{b}\n{d}%',
          },
          itemStyle: {
            shadowBlur: 12,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.25)',
          },
        },
        data: [
          { value: 454, name: '边缘网关', itemStyle: { color: palette.primary } },
          { value: 398, name: '传感采集', itemStyle: { color: '#10b981' } },
          { value: 312, name: '高精视觉', itemStyle: { color: '#8b5cf6' } },
          { value: 256, name: '巡检终端', itemStyle: { color: '#f59e0b' } },
        ],
      },
    ],
  }
})
</script>

<style scoped>
.charts-row {
  display: grid;
  grid-template-columns: minmax(0, 1.8fr) minmax(0, 1.2fr);
  gap: 20px;
  margin-bottom: 24px;
}

@media (max-width: 1080px) {
  .charts-row {
    grid-template-columns: 1fr;
  }
}

.chart-card {
  border-radius: var(--radius-lg, 10px);
  border: 1px solid var(--border-light, #f1f5f9);
  background-color: var(--card-bg, #ffffff);
  transition:
    transform var(--motion-duration-base, 220ms) var(--ease-out-natural, cubic-bezier(0.16, 1, 0.3, 1)),
    box-shadow var(--motion-duration-base, 220ms) var(--ease-out-natural, cubic-bezier(0.16, 1, 0.3, 1)),
    border-color var(--motion-duration-base, 220ms) var(--ease-out-natural, cubic-bezier(0.16, 1, 0.3, 1));
  will-change: transform, box-shadow;
}

.chart-card:hover {
  transform: translateY(-2px);
  border-color: var(--border-color, #e5e7eb);
  box-shadow: 0 8px 18px -6px rgba(0, 0, 0, 0.06);
}

:global(html.dark) .chart-card:hover {
  box-shadow: 0 8px 18px -6px rgba(0, 0, 0, 0.35);
}

.card-header-flex {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.chart-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-main, #1e293b);
  margin: 0;
  line-height: 1.3;
}

.chart-subtitle {
  font-size: 12px;
  color: var(--text-muted, #94a3b8);
  margin: 4px 0 0 0;
}

.total-tag {
  font-size: 12px;
  font-weight: 600;
  color: var(--primary-color, #2563eb);
  background: var(--primary-light, rgba(37, 99, 235, 0.1));
  padding: 3px 8px;
  border-radius: 4px;
}

.time-range-tabs {
  display: inline-flex;
  align-items: center;
  background-color: var(--border-light, #f1f5f9);
  padding: 3px;
  border-radius: var(--radius-sm, 6px);
  gap: 2px;
}

:global(html.dark) .time-range-tabs {
  background-color: rgba(255, 255, 255, 0.08);
}

.range-tab {
  border: none;
  background: transparent;
  padding: 4px 10px;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-muted, #94a3b8);
  border-radius: 4px;
  cursor: pointer;
  transition:
    color var(--motion-duration-fast, 150ms) var(--ease-out-natural, cubic-bezier(0.16, 1, 0.3, 1)),
    background-color var(--motion-duration-fast, 150ms) var(--ease-out-natural, cubic-bezier(0.16, 1, 0.3, 1)),
    box-shadow var(--motion-duration-fast, 150ms) var(--ease-out-natural, cubic-bezier(0.16, 1, 0.3, 1));
  line-height: 1.2;
}

.range-tab:hover {
  color: var(--text-main, #1e293b);
}

.range-tab.is-active {
  background-color: var(--card-bg, #ffffff);
  color: var(--primary-color, #2563eb);
  font-weight: 600;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

:global(html.dark) .range-tab.is-active {
  background-color: #334155;
  color: #60a5fa;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

.chart-wrapper {
  padding-top: 4px;
  min-height: 310px;
}
</style>
