<template>
  <div class="kpi-grid">
    <el-card v-for="item in kpis" :key="item.id" shadow="never" class="kpi-card stagger-item">
      <div class="kpi-body">
        <div class="kpi-meta">
          <span class="kpi-label">{{ item.label }}</span>
          <div class="kpi-value-row">
            <span class="kpi-number">{{ item.value }}</span>
            <span class="kpi-unit">{{ item.unit }}</span>
          </div>
          <div class="kpi-badge-row">
            <span
              class="kpi-badge"
              :class="item.trend >= 0 ? 'badge-up' : 'badge-down'"
            >
              <el-icon :size="12">
                <TopRight v-if="item.trend >= 0" />
                <BottomRight v-else />
              </el-icon>
              {{ item.trendText }}
            </span>
            <span class="kpi-subtext">{{ item.subtext }}</span>
          </div>
        </div>

        <div class="kpi-sparkline">
          <svg
            viewBox="0 0 120 48"
            preserveAspectRatio="none"
            class="spark-svg"
            :style="{ '--spark-color': item.color, '--spark-glow': item.glowColor }"
          >
            <defs>
              <linearGradient :id="`grad-${item.id}`" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" :stop-color="item.color" stop-opacity="0.32" />
                <stop offset="100%" :stop-color="item.color" stop-opacity="0.0" />
              </linearGradient>
            </defs>
            <path :d="item.areaPath" :fill="`url(#grad-${item.id})`" />
            <path
              :d="item.linePath"
              fill="none"
              :stroke="item.color"
              stroke-width="2.2"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAppStore } from '@/stores/app'

const appStore = useAppStore()

const primaryColor = computed(() => appStore.accent || '#2563eb')

const kpis = computed(() => [
  {
    id: 'users',
    label: '全平台用户总量',
    value: '12,846',
    unit: '人',
    trend: 12.8,
    trendText: '+12.8%',
    subtext: '较上周活跃增量',
    color: primaryColor.value,
    glowColor: 'rgba(37, 99, 235, 0.25)',
    linePath: 'M 0 38 Q 20 25, 40 30 T 80 18 T 120 8',
    areaPath: 'M 0 38 Q 20 25, 40 30 T 80 18 T 120 8 L 120 48 L 0 48 Z',
  },
  {
    id: 'devices',
    label: '在运物联网硬件',
    value: '1,420',
    unit: '台',
    trend: 98.2,
    trendText: '98.2%',
    subtext: '在线率稳定运行',
    color: '#10b981',
    glowColor: 'rgba(16, 185, 129, 0.25)',
    linePath: 'M 0 32 Q 30 38, 55 20 T 90 22 T 120 12',
    areaPath: 'M 0 32 Q 30 38, 55 20 T 90 22 T 120 12 L 120 48 L 0 48 Z',
  },
  {
    id: 'requests',
    label: '今日业务调用量',
    value: '842.6',
    unit: 'k 次',
    trend: 23.4,
    trendText: '+23.4%',
    subtext: '环比昨日请求峰值',
    color: '#8b5cf6',
    glowColor: 'rgba(139, 92, 246, 0.25)',
    linePath: 'M 0 42 Q 25 35, 50 22 T 85 14 T 120 6',
    areaPath: 'M 0 42 Q 25 35, 50 22 T 85 14 T 120 6 L 120 48 L 0 48 Z',
  },
  {
    id: 'sla',
    label: '服务可用性 (SLA)',
    value: '99.98',
    unit: '%',
    trend: 0.1,
    trendText: '优秀',
    subtext: '核心集群无异常',
    color: '#06b6d4',
    glowColor: 'rgba(6, 182, 212, 0.25)',
    linePath: 'M 0 20 Q 25 18, 50 22 T 85 16 T 120 14',
    areaPath: 'M 0 20 Q 25 18, 50 22 T 85 16 T 120 14 L 120 48 L 0 48 Z',
  },
])
</script>

<style scoped>
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

@media (max-width: 1200px) {
  .kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .kpi-grid {
    grid-template-columns: 1fr;
  }
}

.kpi-card {
  border-radius: var(--radius-lg, 10px);
  border: 1px solid var(--border-light, #f1f5f9);
  background-color: var(--card-bg, #ffffff);
  transition:
    transform var(--motion-duration-base, 220ms) var(--ease-out-natural, cubic-bezier(0.16, 1, 0.3, 1)),
    box-shadow var(--motion-duration-base, 220ms) var(--ease-out-natural, cubic-bezier(0.16, 1, 0.3, 1)),
    border-color var(--motion-duration-base, 220ms) var(--ease-out-natural, cubic-bezier(0.16, 1, 0.3, 1));
  overflow: hidden;
  will-change: transform, box-shadow;
}

.kpi-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px -8px rgba(0, 0, 0, 0.08);
  border-color: var(--border-color, #e5e7eb);
}

:global(html.dark) .kpi-card:hover {
  box-shadow: 0 10px 20px -8px rgba(0, 0, 0, 0.4);
}

.kpi-body {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 4px 2px;
}

.kpi-meta {
  flex: 1;
  min-width: 0;
}

.kpi-label {
  font-size: 13px;
  color: var(--text-muted, #94a3b8);
  font-weight: 500;
  display: block;
  white-space: nowrap;
}

.kpi-value-row {
  display: flex;
  align-items: baseline;
  gap: 4px;
  margin-top: 6px;
  margin-bottom: 8px;
}

.kpi-number {
  font-size: 26px;
  font-weight: 700;
  color: var(--text-main, #1e293b);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  letter-spacing: -0.02em;
  line-height: 1.1;
}

.kpi-unit {
  font-size: 12px;
  color: var(--text-muted, #94a3b8);
  font-weight: 500;
}

.kpi-badge-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.kpi-badge {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  font-size: 11px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 4px;
  line-height: 1.3;
}

.badge-up {
  color: #10b981;
  background-color: rgba(16, 185, 129, 0.12);
}

.badge-down {
  color: #ef4444;
  background-color: rgba(239, 68, 68, 0.12);
}

.kpi-subtext {
  font-size: 11px;
  color: var(--text-muted, #94a3b8);
  white-space: nowrap;
}

.kpi-sparkline {
  width: 90px;
  height: 48px;
  flex-shrink: 0;
}

.spark-svg {
  width: 100%;
  height: 100%;
  overflow: visible;
  filter: drop-shadow(0 2px 4px var(--spark-glow));
}
</style>
