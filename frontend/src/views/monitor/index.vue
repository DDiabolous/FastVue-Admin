<template>
  <div class="page-container monitor-page">
    <!-- Top Hardware Resource Row -->
    <el-row :gutter="16" class="res-row">
      <!-- CPU Usage Card -->
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="never" class="res-card">
          <div class="res-inner">
            <div class="res-header">
              <span class="res-title">CPU 使用率</span>
              <el-tag size="small" type="success" effect="light">运行良好</el-tag>
            </div>
            <div class="res-main">
              <el-progress
                type="dashboard"
                :percentage="metrics.cpu.usage"
                :color="cpuColor"
                :width="120"
              >
                <template #default="{ percentage }">
                  <span class="progress-val">{{ percentage }}%</span>
                  <span class="progress-sub">8 核心并发</span>
                </template>
              </el-progress>
            </div>
            <div class="res-footer">
              <span>架构: {{ metrics.cpu.model }}</span>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- Memory Usage Card -->
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="never" class="res-card">
          <div class="res-inner">
            <div class="res-header">
              <span class="res-title">系统物理内存 (RAM)</span>
              <el-tag size="small" type="primary" effect="light">{{ metrics.memory.usage }}%</el-tag>
            </div>
            <div class="res-main">
              <el-progress
                type="dashboard"
                :percentage="metrics.memory.usage"
                color="#3b82f6"
                :width="120"
              >
                <template #default="{ percentage }">
                  <span class="progress-val">{{ metrics.memory.used }}</span>
                  <span class="progress-sub">总计 {{ metrics.memory.total }}</span>
                </template>
              </el-progress>
            </div>
            <div class="res-footer">
              <span>可用空闲内存: {{ metrics.memory.free }}</span>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- Disk Usage Card -->
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="never" class="res-card">
          <div class="res-inner">
            <div class="res-header">
              <span class="res-title">系统存储盘容量 (SSD)</span>
              <el-tag size="small" type="info" effect="light">健康状态</el-tag>
            </div>
            <div class="res-main">
              <el-progress
                type="dashboard"
                :percentage="metrics.disk.usage"
                color="#10b981"
                :width="120"
              >
                <template #default="{ percentage }">
                  <span class="progress-val">{{ percentage }}%</span>
                  <span class="progress-sub">已用 {{ metrics.disk.used }}</span>
                </template>
              </el-progress>
            </div>
            <div class="res-footer">
              <span>剩余可用容量: {{ metrics.disk.free }}</span>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- Server Runtime Specs Card -->
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="never" class="res-card">
          <div class="res-inner">
            <div class="res-header">
              <span class="res-title">服务器运行环境</span>
              <span class="pulse-badge online"></span>
            </div>
            <div class="server-specs-list">
              <div class="spec-row">
                <span class="spec-k">操作系统:</span>
                <span class="spec-v">{{ metrics.system.os }}</span>
              </div>
              <div class="spec-row">
                <span class="spec-k">Node 运行时:</span>
                <span class="spec-v mono font-bold">{{ metrics.system.nodeVersion }}</span>
              </div>
              <div class="spec-row">
                <span class="spec-k">连续无故障运行:</span>
                <span class="spec-v font-green">{{ metrics.system.uptime }}</span>
              </div>
              <div class="spec-row">
                <span class="spec-k">系统时间:</span>
                <span class="spec-v mono">{{ metrics.system.serverTime }}</span>
              </div>
            </div>
            <div class="res-footer">
              <el-button link type="primary" size="small" :icon="Refresh" @click="refreshHealthMetrics">
                立即刷新检测
              </el-button>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Middle: Microservices Health Grid -->
    <el-card shadow="never" class="service-health-card">
      <template #header>
        <div class="card-header-flex">
          <div class="title-with-icon">
            <el-icon color="#2563eb"><Connection /></el-icon>
            <span>平台核心微服务与数据集群运行状态</span>
          </div>
          <div class="header-tools">
            <el-button size="small" :icon="Cpu" :loading="flushLoading" @click="handleFlushCache">
              释放运行时缓存 (GC)
            </el-button>
            <el-button size="small" type="primary" plain :icon="Download" @click="handleExportReport">
              导出健康诊断报告
            </el-button>
          </div>
        </div>
      </template>

      <div class="services-grid">
        <div
          v-for="svc in metrics.services"
          :key="svc.name"
          class="service-item-box"
        >
          <div class="svc-top">
            <div class="svc-title">
              <span class="pulse-badge online"></span>
              <strong>{{ svc.name }}</strong>
            </div>
            <el-tag size="small" type="success" effect="light">UP 在线</el-tag>
          </div>
          <div class="svc-body">
            <div class="svc-prop">
              <span class="k">监听端口:</span>
              <span class="v mono">:{{ svc.port }}</span>
            </div>
            <div class="svc-prop">
              <span class="k">响应延时:</span>
              <span class="v mono font-green">{{ svc.latency }}</span>
            </div>
            <div class="svc-prop">
              <span class="k">累计请求:</span>
              <span class="v mono">{{ svc.reqCount }}</span>
            </div>
          </div>
        </div>
      </div>
    </el-card>

    <!-- Bottom: Realtime Terminal Output Console -->
    <el-card shadow="never" class="terminal-card">
      <template #header>
        <div class="card-header-flex">
          <div class="title-with-icon">
            <el-icon color="#38bdf8"><DataBoard /></el-icon>
            <span>中台系统内核及服务实时事件流</span>
          </div>
          <el-button link type="primary" size="small" @click="clearLogs">
            清空控制台
          </el-button>
        </div>
      </template>

      <div class="terminal-body" ref="terminalRef">
        <div v-for="(log, idx) in consoleLogs" :key="idx" class="term-row">
          <span class="term-ts">[{{ log.ts }}]</span>
          <span class="term-level" :class="log.level">[{{ log.level }}]</span>
          <span class="term-mod">&lt;{{ log.module }}&gt;</span>
          <span class="term-msg">{{ log.msg }}</span>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Connection,
  Cpu,
  Download,
  DataBoard,
  Refresh
} from '@element-plus/icons-vue'
import { getSystemMonitorMetrics, addAuditLog } from '@/utils/mockData'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

const metrics = reactive(getSystemMonitorMetrics())
const flushLoading = ref(false)

const cpuColor = (percentage) => {
  if (percentage < 60) return '#10b981'
  if (percentage < 85) return '#f59e0b'
  return '#ef4444'
}

const refreshHealthMetrics = () => {
  const latest = getSystemMonitorMetrics()
  Object.assign(metrics, latest)
  ElMessage.success('系统监控指标已刷新')
}

const consoleLogs = ref([
  { ts: '14:35:10', level: 'INFO', module: 'API-Gateway', msg: 'Incoming HTTP GET /api/v1/healthcheck status=200 duration=4ms' },
  { ts: '14:35:12', level: 'INFO', module: 'MQTT-Broker', msg: 'Client [ent_edge_gw_01] pingreq/pingresp ACK verified, keepalive=60s' },
  { ts: '14:35:18', level: 'INFO', module: 'Auth-SSO', msg: 'JWT session renewed for operator admin, role=super_admin' },
  { ts: '14:35:22', level: 'WARN', module: 'Telemetry-Engine', msg: 'Spindle motor CNC-08 vibration spike 4.8mm/s, alert event queued' },
  { ts: '14:35:25', level: 'INFO', module: 'PostgreSQL-Pool', msg: 'Connection pool active=14, idle=36, max=100. Query load nominal.' }
])

const handleFlushCache = () => {
  flushLoading.value = true
  setTimeout(() => {
    flushLoading.value = false
    metrics.memory.usage = 42.1
    metrics.memory.used = '6.7 GB'
    metrics.memory.free = '9.3 GB'
    ElMessage.success('已触发 V8 堆内存碎片整理与 Redis 无效键值淘汰')
    addAuditLog({
      operator: userStore.currentUsername,
      action: '系统垃圾回收与缓存释放',
      target: 'V8/Redis',
      detail: '释放了 1.1GB 无效缓存',
      status: 'success',
      ip: '192.168.1.108'
    })
  }, 600)
}

const handleExportReport = () => {
  const content = `=========================================
企业管理中台系统运行健康度诊断报告
生成时间: ${new Date().toLocaleString()}
=========================================
CPU 使用率: ${metrics.cpu.usage}% (${metrics.cpu.cores}核)
物理内存: 已用 ${metrics.memory.used} / 总计 ${metrics.memory.total} (${metrics.memory.usage}%)
磁盘空间: 已用 ${metrics.disk.used} / 总计 ${metrics.disk.total} (${metrics.disk.usage}%)
Node 版本: ${metrics.system.nodeVersion}
连续运行时间: ${metrics.system.uptime}

核心微服务状态:
${metrics.services.map(s => `- ${s.name}: [${s.status.toUpperCase()}] 端口:${s.port} 延迟:${s.latency}`).join('\n')}
=========================================
`
  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `系统健康诊断报告_${new Date().toISOString().slice(0, 10)}.txt`
  link.click()
  ElMessage.success('系统诊断报告已生成下载')
}

const clearLogs = () => {
  consoleLogs.value = []
  ElMessage.info('终端日志面板已清空')
}
</script>

<style scoped>
.monitor-page {
  gap: 16px;
}

.res-row {
  row-gap: 16px;
}

.res-card {
  border-radius: 12px;
  height: 100%;
}

.res-inner {
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%;
}

.res-header {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.res-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-main);
}

.res-main {
  margin: 8px 0;
}

.progress-val {
  display: block;
  font-size: 18px;
  font-weight: 700;
  color: var(--text-main);
}

.progress-sub {
  display: block;
  font-size: 11px;
  color: #94a3b8;
  margin-top: 2px;
}

.res-footer {
  width: 100%;
  margin-top: auto;
  padding-top: 10px;
  border-top: 1px solid var(--border-light);
  font-size: 11px;
  color: #64748b;
  text-align: center;
}

.server-specs-list {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 6px 0;
  margin-bottom: 6px;
}

.spec-row {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
}

.spec-k {
  color: #64748b;
}

.spec-v {
  color: var(--text-main);
}

.font-bold {
  font-weight: 600;
}

.font-green {
  color: #16a34a;
}

.card-header-flex {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title-with-icon {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  color: var(--text-main);
}

.services-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 14px;
}

.service-item-box {
  background-color: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  padding: 12px 14px;
}

.svc-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.svc-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--text-main);
}

.svc-body {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.svc-prop {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
}

.svc-prop .k {
  color: #64748b;
}

.svc-prop .v {
  color: var(--text-main);
}

.terminal-card {
  border-radius: 12px;
}

.terminal-body {
  background-color: #0f172a;
  border-radius: 8px;
  padding: 14px;
  font-family: monospace;
  font-size: 12px;
  color: #f8fafc;
  min-height: 160px;
  max-height: 220px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.term-row {
  display: flex;
  gap: 8px;
  line-height: 1.4;
  word-break: break-all;
}

.term-ts {
  color: #64748b;
}

.term-level.INFO {
  color: #38bdf8;
}

.term-level.WARN {
  color: #fbbf24;
}

.term-mod {
  color: #a78bfa;
}

.term-msg {
  color: #e2e8f0;
}

.mono {
  font-family: monospace;
}
</style>
