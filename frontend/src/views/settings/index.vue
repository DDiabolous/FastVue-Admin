<template>
  <div class="page-container settings-page">
    <el-card shadow="never" class="settings-card">
      <el-tabs v-model="activeTab" class="settings-tabs">
        <!-- Tab 1: MQTT Broker Settings -->
        <el-tab-pane name="mqtt">
          <template #label>
            <span class="tab-label">
              <el-icon><Connection /></el-icon>
              <span>通信网关与接口配置</span>
            </span>
          </template>

          <div class="tab-pane-content">
            <div class="pane-header">
              <div>
                <h3 class="pane-title">分布式通信网关与数据接入配置</h3>
                <p class="pane-desc">配置分布式网络节点、微服务与终端双向数据管道与接入服务参数</p>
              </div>
              <el-tag type="success" effect="plain" class="connection-tag">
                <span class="pulse-badge online"></span> 网关接入服务正常
              </el-tag>
            </div>

            <el-form
              ref="mqttFormRef"
              :model="settings.mqtt"
              label-width="150px"
              class="settings-form"
            >
              <el-row :gutter="24">
                <el-col :span="12">
                  <el-form-item label="Broker 主机地址" prop="brokerIp">
                    <el-input v-model="settings.mqtt.brokerIp" placeholder="8.163.51.74" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="通信端口 (Port)" prop="brokerPort">
                    <el-input-number v-model="settings.mqtt.brokerPort" :min="1" :max="65535" style="width: 100%;" />
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row :gutter="24">
                <el-col :span="12">
                  <el-form-item label="默认监听主题" prop="defaultTopic">
                    <el-input v-model="settings.mqtt.defaultTopic" placeholder="test/topic/sample" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="客户端ID前缀" prop="clientIdPrefix">
                    <el-input v-model="settings.mqtt.clientIdPrefix" placeholder="iot_web_admin_" />
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row :gutter="24">
                <el-col :span="12">
                  <el-form-item label="心跳维持 (Keepalive)" prop="keepalive">
                    <el-input-number v-model="settings.mqtt.keepalive" :min="10" :max="600" style="width: 100%;" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="默认消息服务质量" prop="qos">
                    <el-select v-model="settings.mqtt.qos" style="width: 100%;">
                      <el-option label="QoS 0 (至多一次)" :value="0" />
                      <el-option label="QoS 1 (至少一次)" :value="1" />
                      <el-option label="QoS 2 (恰好一次)" :value="2" />
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row :gutter="24">
                <el-col :span="12">
                  <el-form-item label="认证用户名">
                    <el-input v-model="settings.mqtt.username" placeholder="留空则为匿名连接" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="认证密码">
                    <el-input v-model="settings.mqtt.password" type="password" show-password placeholder="••••••••" />
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row :gutter="24">
                <el-col :span="12">
                  <el-form-item label="启用 SSL/TLS 加密">
                    <el-switch v-model="settings.mqtt.enableSsl" active-text="开启安全加密传输 (MQTTS)" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="清理会话 (Clean Session)">
                    <el-switch v-model="settings.mqtt.cleanSession" active-text="重连时新建独立会话" />
                  </el-form-item>
                </el-col>
              </el-row>

              <div class="form-action-row">
                <el-button type="success" :icon="Connection" :loading="pingLoading" @click="handleTestBroker">
                  测试网关接入连通性
                </el-button>
                <el-button type="primary" :icon="Check" :loading="saveLoading" @click="handleSaveSettings('mqtt')">
                  保存并应用配置
                </el-button>
                <el-button :icon="Refresh" @click="resetToDefault('mqtt')">恢复默认</el-button>
              </div>
            </el-form>
          </div>
        </el-tab-pane>

        <!-- Tab 2: General System Settings -->
        <el-tab-pane name="general">
          <template #label>
            <span class="tab-label">
              <el-icon><Setting /></el-icon>
              <span>基本信息与平台设置</span>
            </span>
          </template>

          <div class="tab-pane-content">
            <div class="pane-header">
              <div>
                <h3 class="pane-title">平台常规信息</h3>
                <p class="pane-desc">定制管理中台名称、版权备案信息与全局交互偏好</p>
              </div>
            </div>

            <el-form :model="settings.general" label-width="140px" class="settings-form">
              <el-row :gutter="24">
                <el-col :span="12">
                  <el-form-item label="系统平台名称">
                    <el-input v-model="settings.general.siteName" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="平台副标题">
                    <el-input v-model="settings.general.siteSubTitle" />
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row :gutter="24">
                <el-col :span="12">
                  <el-form-item label="ICP 备案号">
                    <el-input v-model="settings.general.recordNo" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="技术支持邮箱">
                    <el-input v-model="settings.general.adminEmail" />
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row :gutter="24">
                <el-col :span="12">
                  <el-form-item label="版权归属文本">
                    <el-input v-model="settings.general.copyright" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="遥测自动轮询频率">
                    <el-select v-model="settings.general.autoRefreshInterval" style="width: 100%;">
                      <el-option label="5 秒 (高频实时)" :value="5" />
                      <el-option label="15 秒 (推荐标准)" :value="15" />
                      <el-option label="30 秒 (节能适度)" :value="30" />
                      <el-option label="关闭自动轮询" :value="0" />
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>

              <div class="form-action-row">
                <el-button type="primary" :icon="Check" :loading="saveLoading" @click="handleSaveSettings('general')">
                  保存平台信息
                </el-button>
              </div>
            </el-form>
          </div>
        </el-tab-pane>

        <!-- Tab 3: Security & Policies -->
        <el-tab-pane name="security">
          <template #label>
            <span class="tab-label">
              <el-icon><Lock /></el-icon>
              <span>安全与认证策略</span>
            </span>
          </template>

          <div class="tab-pane-content">
            <div class="pane-header">
              <div>
                <h3 class="pane-title">账户与安全合规策略</h3>
                <p class="pane-desc">配置管理员密码强度要求、登录防暴力破解锁定及会话超时限制</p>
              </div>
            </div>

            <el-form :model="settings.security" label-width="160px" class="settings-form">
              <el-row :gutter="24">
                <el-col :span="12">
                  <el-form-item label="密码最短长度要求">
                    <el-input-number v-model="settings.security.minPasswordLength" :min="6" :max="32" style="width: 100%;" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="密码强复杂度校验">
                    <el-switch v-model="settings.security.requireSpecialChars" active-text="强制包含字母、数字及特殊字符" />
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row :gutter="24">
                <el-col :span="12">
                  <el-form-item label="登录连续失败锁定次数">
                    <el-input-number v-model="settings.security.maxLoginFailAttempts" :min="3" :max="10" style="width: 100%;" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="账号锁定时长 (分钟)">
                    <el-input-number v-model="settings.security.lockoutDurationMinutes" :min="5" :max="1440" style="width: 100%;" />
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row :gutter="24">
                <el-col :span="12">
                  <el-form-item label="无操作会话超时(分钟)">
                    <el-input-number v-model="settings.security.sessionTimeoutMinutes" :min="10" :max="480" style="width: 100%;" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="双因素认证 (2FA)">
                    <el-switch v-model="settings.security.enable2FA" active-text="登录时需要动态验证码" />
                  </el-form-item>
                </el-col>
              </el-row>

              <el-form-item label="后台允许访问 IP 白名单">
                <el-input
                  v-model="settings.security.ipWhitelist"
                  placeholder="例如: 192.168.1.0/24, 127.0.0.1 (多个用逗号隔开)"
                />
              </el-form-item>

              <div class="form-action-row">
                <el-button type="primary" :icon="Check" :loading="saveLoading" @click="handleSaveSettings('security')">
                  保存安全策略
                </el-button>
              </div>
            </el-form>
          </div>
        </el-tab-pane>

        <!-- Tab 4: Notifications & Webhook -->
        <el-tab-pane name="notifications">
          <template #label>
            <span class="tab-label">
              <el-icon><Bell /></el-icon>
              <span>告警通知与机器人</span>
            </span>
          </template>

          <div class="tab-pane-content">
            <div class="pane-header">
              <div>
                <h3 class="pane-title">设备异常告警通道</h3>
                <p class="pane-desc">当设备离线、传感器温度超标或 MQTT 丢包时，自动触发推送</p>
              </div>
            </div>

            <el-form :model="settings.notification" label-width="160px" class="settings-form">
              <el-form-item label="邮件通知服务">
                <el-switch v-model="settings.notification.enableEmailAlerts" active-text="发生严重告警时发送邮件" />
              </el-form-item>

              <el-form-item label="告警接收邮箱" v-if="settings.notification.enableEmailAlerts">
                <el-input v-model="settings.notification.emailRecipients" placeholder="alert-ops@iot-cloud.com" />
              </el-form-item>

              <el-form-item label="钉钉/企业微信群机器人">
                <el-switch v-model="settings.notification.enableDingTalk" active-text="通过 Webhook 实时推送到运维群" />
              </el-form-item>

              <el-form-item label="Webhook URL" v-if="settings.notification.enableDingTalk">
                <el-input
                  v-model="settings.notification.dingTalkWebhook"
                  placeholder="https://oapi.dingtalk.com/robot/send?access_token=..."
                />
              </el-form-item>

              <el-row :gutter="24">
                <el-col :span="12">
                  <el-form-item label="判定设备离线心跳阈值">
                    <el-input-number v-model="settings.notification.deviceOfflineAlertTime" :min="30" :max="3600" style="width: 100%;" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="设备高温告警阈值(°C)">
                    <el-input-number v-model="settings.notification.warningAlertThreshold" :min="30" :max="120" style="width: 100%;" />
                  </el-form-item>
                </el-col>
              </el-row>

              <div class="form-action-row">
                <el-button :icon="Promotion" @click="handleSendTestAlert">
                  发送测试告警消息
                </el-button>
                <el-button type="primary" :icon="Check" :loading="saveLoading" @click="handleSaveSettings('notification')">
                  保存告警配置
                </el-button>
              </div>
            </el-form>
          </div>
        </el-tab-pane>

        <!-- Tab 5: Audit & Operation Logs -->
        <el-tab-pane name="logs">
          <template #label>
            <span class="tab-label">
              <el-icon><Tickets /></el-icon>
              <span>系统审计与操作日志</span>
            </span>
          </template>

          <div class="tab-pane-content">
            <div class="pane-header">
              <div>
                <h3 class="pane-title">全链路操作审计历史</h3>
                <p class="pane-desc">记录用户登录登出、设备控制指令下发、系统配置修改等关键动作</p>
              </div>
              <div class="header-btns">
                <el-button :icon="Download" @click="handleExportLogs">导出日志</el-button>
                <el-button type="danger" plain :icon="Delete" @click="handleClearLogs">清空审计日志</el-button>
              </div>
            </div>

            <el-table :data="logs" stripe style="width: 100%; margin-top: 12px;">
              <el-table-column prop="time" label="操作时间" width="180" />
              <el-table-column prop="operator" label="操作账号" width="130">
                <template #default="{ row }">
                  <el-tag size="small" :type="row.operator === 'admin' ? 'danger' : 'info'">
                    {{ row.operator }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="action" label="操作类型" width="140" />
              <el-table-column prop="target" label="操作目标" width="160">
                <template #default="{ row }">
                  <span class="mono">{{ row.target }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="detail" label="详细描述 / Payload" min-width="260" show-overflow-tooltip />
              <el-table-column prop="status" label="执行结果" width="100" align="center">
                <template #default="{ row }">
                  <el-tag
                    size="small"
                    :type="row.status === 'success' ? 'success' : row.status === 'warning' ? 'warning' : 'info'"
                  >
                    {{ row.status === 'success' ? '成功' : row.status === 'warning' ? '告警' : '信息' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="ip" label="操作IP" width="140" />
            </el-table>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Connection,
  Setting,
  Lock,
  Bell,
  Tickets,
  Check,
  Refresh,
  Promotion,
  Download,
  Delete
} from '@element-plus/icons-vue'
import {
  getStoredSettings,
  saveStoredSettings,
  getStoredLogs,
  addAuditLog
} from '@/utils/mockData'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

const activeTab = ref('mqtt')
const saveLoading = ref(false)
const pingLoading = ref(false)

const settings = reactive({
  general: {},
  mqtt: {},
  security: {},
  notification: {}
})

const logs = ref([])

const loadSettingsData = () => {
  const loaded = getStoredSettings()
  settings.general = { ...loaded.general }
  settings.mqtt = { ...loaded.mqtt }
  settings.security = { ...loaded.security }
  settings.notification = { ...loaded.notification }
  logs.value = getStoredLogs()
}

onMounted(() => {
  loadSettingsData()
})

const handleTestBroker = () => {
  pingLoading.value = true
  setTimeout(() => {
    pingLoading.value = false
    ElMessage.success({
      message: `Broker (${settings.mqtt.brokerIp}:${settings.mqtt.brokerPort}) 握手成功，网络往返时延 11ms，Keepalive 保持正常！`,
      duration: 3500
    })
    addAuditLog({
      operator: userStore.currentUsername,
      action: '测试Broker连通性',
      target: `${settings.mqtt.brokerIp}:${settings.mqtt.brokerPort}`,
      detail: '触发网络连通性与 TCP 端口探测测试',
      status: 'success',
      ip: '192.168.1.108'
    })
  }, 800)
}

const handleSaveSettings = (category) => {
  saveLoading.value = true
  setTimeout(() => {
    saveLoading.value = false
    saveStoredSettings(settings)
    ElMessage.success('配置已保存并立即热生效')
    addAuditLog({
      operator: userStore.currentUsername,
      action: '更新系统配置',
      target: `分类: ${category}`,
      detail: `修改并保存了 ${category} 相关的配置项`,
      status: 'success',
      ip: '192.168.1.108'
    })
    logs.value = getStoredLogs()
  }, 400)
}

const resetToDefault = (category) => {
  ElMessageBox.confirm('确定将该模块配置恢复至初始出厂设置吗？', '确认重置', {
    confirmButtonText: '确定重置',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    localStorage.removeItem('iot_settings_data')
    loadSettingsData()
    ElMessage.success('已恢复为默认配置')
  }).catch(() => {})
}

const handleSendTestAlert = () => {
  ElMessage.success('测试告警通知已成功推送到指定机器人与管理员邮箱！')
  addAuditLog({
    operator: userStore.currentUsername,
    action: '触发测试告警',
    target: '通知服务',
    detail: '管理员主动触发了告警通道可达性测试',
    status: 'info',
    ip: '192.168.1.108'
  })
  logs.value = getStoredLogs()
}

const handleExportLogs = () => {
  const headers = ['时间', '操作者', '操作类型', '操作目标', '详细信息', '结果', 'IP']
  const rows = logs.value.map((l) => [
    l.time,
    l.operator,
    l.action,
    l.target,
    `"${(l.detail || '').replace(/"/g, '""')}"`,
    l.status,
    l.ip
  ])
  const csvContent = 'data:text/csv;charset=utf-8,\uFEFF' + [headers.join(','), ...rows.map(e => e.join(','))].join('\n')
  const encodedUri = encodeURI(csvContent)
  const link = document.createElement('a')
  link.setAttribute('href', encodedUri)
  link.setAttribute('download', `中台系统审计日志_${new Date().toISOString().slice(0, 10)}.csv`)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  ElMessage.success('系统审计日志已导出')
}

const handleClearLogs = () => {
  ElMessageBox.confirm('确定要清空全部系统操作审计日志吗？该动作将被记录！', '高危操作警告', {
    confirmButtonText: '确认清空',
    cancelButtonText: '取消',
    type: 'error'
  }).then(() => {
    localStorage.setItem('iot_logs_data', JSON.stringify([]))
    logs.value = []
    ElMessage.success('审计日志已清空')
    addAuditLog({
      operator: userStore.currentUsername,
      action: '清空审计日志',
      target: '审计模块',
      detail: '执行了全量日志清除',
      status: 'warning',
      ip: '192.168.1.108'
    })
    logs.value = getStoredLogs()
  }).catch(() => {})
}
</script>

<style scoped>
.settings-page {
  padding: 16px;
}

.settings-card {
  min-height: calc(100vh - var(--header-height) - var(--tags-height) - 32px);
  display: flex;
  flex-direction: column;
}

.settings-tabs {
  flex: 1;
}

.tab-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
}

.tab-pane-content {
  padding: 12px 16px 24px;
  max-width: 900px;
}

.pane-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  padding-bottom: 14px;
  border-bottom: 1px solid var(--border-light);
}

.pane-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-main);
  margin-bottom: 4px;
}

.pane-desc {
  font-size: 13px;
  color: #64748b;
}

.connection-tag {
  height: 28px;
  line-height: 26px;
  font-size: 12px;
}

.settings-form {
  margin-top: 10px;
}

.form-action-row {
  margin-top: 28px;
  padding-top: 18px;
  border-top: 1px solid var(--border-light);
  display: flex;
  gap: 12px;
}

.mono {
  font-family: monospace;
}

.header-btns {
  display: flex;
  gap: 8px;
}
</style>
