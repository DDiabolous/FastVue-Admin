<template>
  <PageContainer
    class="business-page business-devices"
    title="资产资源示例"
    description="维护资产台账、连接状态与资源信息，支持列表和卡片。本页使用本地演示数据。"
  >
    <!-- Top Filter Form -->

    <!-- Table Card & Operations -->
    <el-card shadow="never" class="data-card business-data-card">
      <FilterPanel :model="queryForm" @search="handleSearch">
        <el-form-item label="关键词">
          <el-input
            v-model="queryForm.keyword"
            placeholder="名称 / 编号 / Client ID"
            title="支持资产名称、资源编号和 Client ID"
            clearable
          />
        </el-form-item>

        <el-form-item label="类别">
          <el-select v-model="queryForm.type" placeholder="全部类型" clearable style="width: 155px">
            <el-option label="云端接入网关" value="gateway" />
            <el-option label="计算应用主机" value="server" />
            <el-option label="商用智能终端" value="terminal" />
            <el-option label="环境传感设备" value="sensor" />
            <el-option label="网络基础设施" value="network" />
            <el-option label="AI算力工作站" value="ai_vision" />
            <el-option label="移动服务机器人" value="robot" />
          </el-select>
        </el-form-item>

        <el-form-item label="状态">
          <el-select
            v-model="queryForm.status"
            placeholder="全部状态"
            clearable
            style="width: 130px"
          >
            <el-option label="在线" value="online" />
            <el-option label="告警" value="warning" />
            <el-option label="离线" value="offline" />
          </el-select>
        </el-form-item>

        <el-form-item label="Topic" class="filter-topic">
          <el-input
            v-model="queryForm.topic"
            placeholder="输入 Topic"
            clearable
            style="width: 190px"
          />
        </el-form-item>

        <template #actions>
          <el-form-item class="form-btn-item">
            <el-button type="primary" :icon="Search" native-type="submit">查询</el-button>
            <el-button :icon="Refresh" @click="handleReset">重置</el-button>
          </el-form-item>
        </template>
      </FilterPanel>
      <TableToolbar
        :loading="tableLoading"
        :total="filteredDevices.length"
        :selected="selectedRows.length"
        :columns="businessTable.columns"
        v-model:visible-columns="businessTable.visible.value"
        @reset-columns="businessTable.resetColumns"
        @refresh="loadDeviceData"
      >
        <el-button type="primary" :icon="Plus" @click="openCreateModal">新增</el-button>
        <el-button
          type="warning"
          plain
          :icon="Promotion"
          :disabled="selectedRows.length === 0"
          @click="handleBatchCommand"
        >
          批量指令
        </el-button>
        <el-button
          type="danger"
          plain
          :icon="Delete"
          :disabled="selectedRows.length === 0"
          @click="handleBatchDelete"
        >
          批量删除
        </el-button>
        <el-button :icon="Connection" :loading="syncLoading" @click="handleSyncStatus">
          同步状态
        </el-button>
        <el-button :icon="Download" @click="handleExportDevices">导出</el-button>
        <el-button v-if="selectedRows.length" link @click="clearSelection">清空已选</el-button>
        <template #tools>
          <el-radio-group v-model="viewMode" class="view-mode-group">
            <el-tooltip content="列表视图" placement="top">
              <el-radio-button value="table" aria-label="列表视图">
                <el-icon :size="15"><List /></el-icon>
              </el-radio-button>
            </el-tooltip>
            <el-tooltip content="卡片视图" placement="top">
              <el-radio-button value="card" aria-label="卡片视图">
                <el-icon :size="15"><Grid /></el-icon>
              </el-radio-button>
            </el-tooltip>
          </el-radio-group>
        </template>
      </TableToolbar>

      <!-- Batch Toolbar Row -->

      <!-- Table View Mode -->
      <el-table
        border
        @header-dragend="businessTable.resize"
        v-if="viewMode === 'table'"
        ref="tableRef"
        v-loading="tableLoading"
        :data="paginatedDevices"
        row-key="id"
        stripe
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="50" align="center" />

        <el-table-column
          label="资产资源名称 / 编码"
          min-width="210"
          key="assetInfo"
          v-if="businessTable.isColumnVisible('assetInfo')"
          :width="businessTable.columnWidth('assetInfo', undefined)"
          prop="assetInfo"
        >
          <template #default="{ row }">
            <div class="device-name-box">
              <span class="device-name-text">{{ row.name }}</span>
              <div class="device-sn-sub">
                <span class="device-sn">{{ row.id }}</span>
                <span class="device-type-tag">{{ row.typeName }}</span>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column
          label="运行状态"
          align="center"
          key="status"
          v-if="businessTable.isColumnVisible('status')"
          :width="businessTable.columnWidth('status', 120)"
          prop="status"
        >
          <template #default="{ row }">
            <div class="status-cell">
              <span class="pulse-badge" :class="row.status"></span>
              <span class="status-text" :class="row.status">
                {{ row.status === 'online' ? '在线' : row.status === 'warning' ? '告警' : '离线' }}
              </span>
            </div>
          </template>
        </el-table-column>

        <el-table-column
          label="通信与接入参数"
          min-width="190"
          key="connection"
          v-if="businessTable.isColumnVisible('connection')"
          :width="businessTable.columnWidth('connection', undefined)"
          prop="connection"
        >
          <template #default="{ row }">
            <div class="mqtt-info-cell">
              <div class="topic-row">
                <el-icon :size="12" color="#64748b"><Link /></el-icon>
                <span class="topic-text mono" :title="row.topic">{{ row.topic }}</span>
              </div>
              <span class="client-id mono">Client: {{ row.clientId }}</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column
          label="通信协议"
          key="protocol"
          v-if="businessTable.isColumnVisible('protocol')"
          :width="businessTable.columnWidth('protocol', 120)"
          prop="protocol"
        >
          <template #default="{ row }">
            <el-tag size="small" type="info" effect="plain">{{ row.protocol }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column
          label="核心指标与健康度"
          min-width="180"
          key="telemetry"
          v-if="businessTable.isColumnVisible('telemetry')"
          :width="businessTable.columnWidth('telemetry', undefined)"
          prop="telemetry"
        >
          <template #default="{ row }">
            <div class="telemetry-compact" v-if="row.status !== 'offline'">
              <div class="tel-item" v-if="row.temperature">
                <span class="tel-label">温度</span>
                <span class="tel-val" :class="{ 'val-warn': row.temperature > 45 }">
                  {{ row.temperature }}°C
                </span>
              </div>
              <div class="tel-item" v-if="row.cpuUsage !== undefined">
                <span class="tel-label">CPU</span>
                <span class="tel-val">{{ row.cpuUsage }}%</span>
              </div>
              <div class="tel-item" v-if="row.rssi">
                <span class="tel-label">信号</span>
                <span class="tel-val">{{ row.rssi }}dBm</span>
              </div>
            </div>
            <span v-else class="text-muted">资源离线中</span>
          </template>
        </el-table-column>

        <el-table-column
          prop="location"
          label="部署节点与位置"
          min-width="150"
          show-overflow-tooltip
          key="location"
          v-if="businessTable.isColumnVisible('location')"
          :width="businessTable.columnWidth('location', undefined)"
        />

        <el-table-column
          label="最后同步"
          key="heartbeat"
          v-if="businessTable.isColumnVisible('heartbeat')"
          :width="businessTable.columnWidth('heartbeat', 140)"
          prop="heartbeat"
        >
          <template #default="{ row }">
            <span class="heartbeat-text" :class="{ 'is-stale': row.status === 'offline' }">
              {{ row.lastHeartbeat }}
            </span>
          </template>
        </el-table-column>

        <!-- Operation Action Buttons (Streamlined to 3 clear actions, strictly in one horizontal row) -->
        <el-table-column label="操作" width="194" fixed="right" align="center">
          <template #default="{ row }">
            <div class="table-op-btns">
              <el-button
                link
                type="primary"
                size="small"
                :icon="Monitor"
                @click="openTelemetryDrawer(row)"
              >
                遥测
              </el-button>
              <el-button link type="primary" size="small" :icon="Edit" @click="openEditModal(row)">
                编辑
              </el-button>
              <el-popconfirm
                title="确定删除该资产吗？"
                confirm-button-text="删除"
                cancel-button-text="取消"
                confirm-button-type="danger"
                width="auto"
                @confirm="handleDeleteDevice(row)"
              >
                <template #reference>
                  <el-button link type="danger" size="small" :icon="Delete">删除</el-button>
                </template>
              </el-popconfirm>
            </div>
          </template>
        </el-table-column>
        <template #empty>
          <TableEmpty
            :loading="tableLoading"
            :filtered="businessTable.isFiltered.value"
            @reset="handleReset"
          />
        </template>
      </el-table>

      <!-- Card View Mode -->
      <div v-else class="device-card-grid">
        <el-card
          v-for="device in paginatedDevices"
          :key="device.id"
          shadow="hover"
          class="device-tile-card"
        >
          <div class="tile-header">
            <div class="tile-title-box">
              <span class="pulse-badge" :class="device.status"></span>
              <strong class="tile-name" :title="device.name">{{ device.name }}</strong>
            </div>
            <el-tag
              size="small"
              :type="
                device.status === 'online'
                  ? 'success'
                  : device.status === 'warning'
                    ? 'warning'
                    : 'info'
              "
            >
              {{
                device.status === 'online' ? '在线' : device.status === 'warning' ? '告警' : '离线'
              }}
            </el-tag>
          </div>

          <div class="tile-body">
            <p class="tile-prop">
              <span class="k">设备SN:</span>
              <span class="v mono" :title="device.sn">{{ device.sn }}</span>
            </p>
            <p class="tile-prop">
              <span class="k">MQTT主题:</span>
              <span class="v mono" :title="device.topic">{{ device.topic }}</span>
            </p>
            <p class="tile-prop">
              <span class="k">部署位置:</span>
              <span class="v" :title="device.location">{{ device.location }}</span>
            </p>
            <p class="tile-prop">
              <span class="k">心跳状态:</span>
              <span class="v" :title="device.lastHeartbeat">{{ device.lastHeartbeat }}</span>
            </p>
          </div>

          <div class="tile-footer">
            <el-button
              size="small"
              type="primary"
              plain
              :icon="Monitor"
              @click="openTelemetryDrawer(device)"
            >
              遥测
            </el-button>
            <el-button
              size="small"
              type="warning"
              plain
              :icon="Promotion"
              @click="openCommandModal(device)"
            >
              指令
            </el-button>
            <el-button size="small" :icon="Edit" @click="openEditModal(device)">编辑</el-button>
          </div>
        </el-card>
      </div>

      <!-- Pagination -->
      <TableEmpty
        v-if="viewMode === 'card' && !filteredDevices.length"
        :loading="tableLoading"
        :filtered="businessTable.isFiltered.value"
        @reset="handleReset"
      />
      <div class="business-pagination">
        <span class="page-total-text">
          已筛选
          <strong>{{ filteredDevices.length }}</strong>
          台设备
        </span>
        <el-pagination
          v-model:current-page="pagination.currentPage"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[6, 12, 24, 48]"
          :total="filteredDevices.length"
          layout="total, sizes, prev, pager, next"
        />
      </div>
    </el-card>

    <!-- Create / Edit Device Dialog -->
    <el-dialog
      :before-close="formDraft.beforeClose"
      :close-on-click-modal="false"
      class="business-overlay"
      v-model="deviceDialogVisible"
      :title="isEditMode ? '编辑资产资源配置' : '登记新接入资产资源'"
      width="min(720px, 94vw)"
      destroy-on-close
    >
      <el-form
        ref="deviceFormRef"
        :model="deviceFormData"
        :rules="deviceFormRules"
        label-width="110px"
        style="padding: 10px 10px 0"
      >
        <el-row :gutter="16">
          <el-col :xs="24" :sm="12">
            <el-form-item label="资产资源名称" prop="name">
              <el-input v-model="deviceFormData.name" placeholder="如: 分布式API网关-02" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item label="资源类别" prop="deviceType">
              <el-select
                v-model="deviceFormData.deviceType"
                placeholder="选择类别"
                style="width: 100%"
              >
                <el-option label="云端网关" value="gateway" />
                <el-option label="计算服务器" value="server" />
                <el-option label="商用智能终端" value="terminal" />
                <el-option label="环境传感设备" value="sensor" />
                <el-option label="网络基础设施" value="network" />
                <el-option label="AI算力工作站" value="ai_vision" />
                <el-option label="移动服务机器人" value="robot" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :xs="24" :sm="12">
            <el-form-item label="资产序列号" prop="sn">
              <el-input v-model="deviceFormData.sn" placeholder="SN-202610-XXXX" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item label="通信协议" prop="protocol">
              <el-select
                v-model="deviceFormData.protocol"
                placeholder="选择通信协议"
                style="width: 100%"
              >
                <el-option label="MQTT 3.1.1" value="MQTT 3.1.1" />
                <el-option label="MQTT 5.0" value="MQTT 5.0" />
                <el-option label="HTTP / RESTful" value="HTTP / RESTful" />
                <el-option label="WebSocket" value="WebSocket" />
                <el-option label="gRPC" value="gRPC" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :xs="24" :sm="12">
            <el-form-item label="通信管道/Topic" prop="topic">
              <el-input v-model="deviceFormData.topic" placeholder="cloudhub/sample/topic" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item label="Client ID" prop="clientId">
              <el-input v-model="deviceFormData.clientId" placeholder="例如: cloudhub_node_01" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :xs="24" :sm="12">
            <el-form-item label="IP 网络地址" prop="ip">
              <el-input v-model="deviceFormData.ip" placeholder="192.168.10.X" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item label="心跳周期(秒)" prop="heartbeatInterval">
              <el-input-number
                v-model="deviceFormData.heartbeatInterval"
                :min="1"
                :max="3600"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="部署位置/节点" prop="location">
          <el-input
            v-model="deviceFormData.location"
            placeholder="例如: 华北一区集群机房 02机架 / 商业展示区 A-05"
          />
        </el-form-item>

        <el-form-item label="快捷指令" v-if="isEditMode">
          <el-button
            size="small"
            type="warning"
            plain
            :icon="Promotion"
            @click="handleDispatchFromEdit"
          >
            下发 MQTT 控制指令
          </el-button>
        </el-form-item>

        <el-form-item label="资产详细描述" prop="description">
          <el-input
            v-model="deviceFormData.description"
            type="textarea"
            :rows="2"
            placeholder="简述该项资产资源的业务用途与遥测指标定义"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="formDraft.close">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="submitDeviceForm">
          保存资产
        </el-button>
      </template>
    </el-dialog>

    <!-- MQTT Command Dispatch Modal -->
    <el-dialog
      class="business-overlay"
      v-model="cmdDialogVisible"
      :title="`向【${activeCmdDevice?.name || '选中设备'}】下发 MQTT 指令`"
      width="min(600px, 94vw)"
    >
      <div v-if="activeCmdDevice" class="cmd-dialog-content">
        <div class="broker-notice">
          <el-icon><Connection /></el-icon>
          <span>
            目标 Broker: 8.163.51.74:9003 | Topic:
            <strong>{{ activeCmdDevice.topic }}</strong>
          </span>
        </div>

        <el-form label-width="90px" style="margin-top: 14px">
          <el-form-item label="预设快捷指令">
            <el-radio-group v-model="selectedCmdTemplate" @change="applyCmdTemplate">
              <el-radio-button value="ping">设备握手 (Ping)</el-radio-button>
              <el-radio-button value="reboot">远程安全重启</el-radio-button>
              <el-radio-button value="sync_time">对齐NTP时序</el-radio-button>
              <el-radio-button value="custom">自定义JSON</el-radio-button>
            </el-radio-group>
          </el-form-item>

          <el-form-item label="服务质量(QoS)">
            <el-radio-group v-model="cmdForm.qos">
              <el-radio :value="0">QoS 0 (至多一次)</el-radio>
              <el-radio :value="1">QoS 1 (至少一次)</el-radio>
              <el-radio :value="2">QoS 2 (恰好一次)</el-radio>
            </el-radio-group>
          </el-form-item>

          <el-form-item label="指令 Payload">
            <el-input
              v-model="cmdForm.payload"
              type="textarea"
              :rows="5"
              placeholder='{"cmd": "reboot", "timestamp": 1729400000}'
              class="mono-textarea"
            />
          </el-form-item>
        </el-form>
      </div>

      <template #footer>
        <el-button @click="cmdDialogVisible = false">取消</el-button>
        <el-button type="warning" :loading="cmdSending" @click="dispatchMqttCommand">
          立即下发指令
        </el-button>
      </template>
    </el-dialog>

    <!-- Realtime Telemetry Drawer -->
    <el-drawer
      class="business-overlay"
      v-model="telemetryDrawerVisible"
      :title="`${activeDrawerDevice?.name || '设备'} - 实时遥测与数据流`"
      size="min(560px, 100vw)"
      destroy-on-close
    >
      <div v-if="activeDrawerDevice" class="drawer-content">
        <!-- Status Header Card -->
        <div class="drawer-stat-bar">
          <div class="drawer-chip">
            <span class="label">运行状态:</span>
            <el-tag
              :type="
                activeDrawerDevice.status === 'online'
                  ? 'success'
                  : activeDrawerDevice.status === 'warning'
                    ? 'warning'
                    : 'info'
              "
            >
              {{
                activeDrawerDevice.status === 'online'
                  ? '在线传输中'
                  : activeDrawerDevice.status === 'warning'
                    ? '指标告警'
                    : '已断开'
              }}
            </el-tag>
          </div>
          <div class="drawer-chip">
            <span class="label">固件版本:</span>
            <span class="val mono">{{ activeDrawerDevice.firmware }}</span>
          </div>
          <div class="drawer-chip">
            <span class="label">Client ID:</span>
            <span class="val mono">{{ activeDrawerDevice.clientId }}</span>
          </div>
        </div>

        <!-- Telemetry Gauges / Metrics -->
        <div class="metrics-grid">
          <div class="metric-card">
            <span class="m-title">工作温度</span>
            <span class="m-value" :class="{ 'm-danger': activeDrawerDevice.temperature > 45 }">
              {{ activeDrawerDevice.temperature || '--' }}
              <small>°C</small>
            </span>
            <span class="m-sub">正常范围 15~40°C</span>
          </div>

          <div class="metric-card">
            <span class="m-title">CPU 占用率</span>
            <span class="m-value">
              {{ activeDrawerDevice.cpuUsage || '0' }}
              <small>%</small>
            </span>
            <el-progress
              :percentage="activeDrawerDevice.cpuUsage || 0"
              :stroke-width="5"
              :show-text="false"
            />
          </div>

          <div class="metric-card">
            <span class="m-title">无线信号 (RSSI)</span>
            <span class="m-value">
              {{ activeDrawerDevice.rssi || '--' }}
              <small>dBm</small>
            </span>
            <span class="m-sub">网络连接优良</span>
          </div>

          <div class="metric-card">
            <span class="m-title">今日上报数据包</span>
            <span class="m-value">
              {{ (activeDrawerDevice.msgCountToday || 0).toLocaleString() }}
              <small>条</small>
            </span>
            <span class="m-sub">无丢包发生</span>
          </div>
        </div>

        <!-- Realtime MQTT Stream Console -->
        <div class="console-box">
          <div class="console-header">
            <div class="console-title">
              <el-icon><DataBoard /></el-icon>
              <span>MQTT 实时遥测消息流 (Topic: {{ activeDrawerDevice.topic }})</span>
            </div>
            <el-button link type="primary" size="small" @click="clearConsoleLogs">清空</el-button>
          </div>

          <div class="console-logs" ref="consoleLogsRef">
            <div v-for="(log, idx) in simulatedLogs" :key="idx" class="console-log-row">
              <span class="log-time">{{ log.time }}</span>
              <span class="log-topic">[QoS {{ log.qos }}]</span>
              <span class="log-payload">{{ log.payload }}</span>
            </div>
          </div>
        </div>
      </div>
    </el-drawer>
  </PageContainer>
</template>

<script setup>
import PageContainer from '@/components/admin/PageContainer.vue'
import FilterPanel from '@/components/admin/FilterPanel.vue'
import TableToolbar from '@/components/admin/TableToolbar.vue'
import TableEmpty from '@/components/admin/TableEmpty.vue'
import { useBusinessTable } from '@/composables/useBusinessTable'
import { useBusinessDraft } from '@/composables/useBusinessDraft'

import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search,
  Refresh,
  Plus,
  Promotion,
  Delete,
  Connection,
  Download,
  RefreshRight,
  Monitor,
  Edit,
  Link,
  DataBoard,
  Operation,
  InfoFilled,
  List,
  Grid,
} from '@element-plus/icons-vue'
import { getStoredDevices, saveStoredDevices, addAuditLog } from '@/utils/mockData'
import { useAdminStore } from '@/stores/admin'

const userStore = useAdminStore()

const tableRef = ref()
const allDevices = ref([])
const tableLoading = ref(false)
const syncLoading = ref(false)
const selectedRows = ref([])
const viewMode = ref('table')

const clearSelection = () => {
  tableRef.value?.clearSelection()
  selectedRows.value = []
}

const queryForm = reactive({
  keyword: '',
  type: '',
  status: '',
  topic: '',
})

const pagination = reactive({
  currentPage: 1,
  pageSize: 12,
})

const loadDeviceData = () => {
  tableLoading.value = true
  setTimeout(() => {
    allDevices.value = getStoredDevices()
    tableLoading.value = false
  }, 200)
}

onMounted(() => {
  loadDeviceData()
})

const typeNameMap = {
  gateway: '工业网关',
  sensor: '温湿度传感器',
  controller: '继电器控制器',
  ai_vision: 'AI视觉终端',
  robot: '移动机器人',
}

const filteredDevices = computed(() => {
  return allDevices.value.filter((d) => {
    const kw = queryForm.keyword.toLowerCase().trim()
    const matchKw =
      !kw ||
      d.name.toLowerCase().includes(kw) ||
      d.id.toLowerCase().includes(kw) ||
      d.clientId.toLowerCase().includes(kw) ||
      (d.sn && d.sn.toLowerCase().includes(kw))
    const matchType = !queryForm.type || d.deviceType === queryForm.type
    const matchStatus = !queryForm.status || d.status === queryForm.status
    const matchTopic =
      !queryForm.topic || d.topic.toLowerCase().includes(queryForm.topic.toLowerCase().trim())
    return matchKw && matchType && matchStatus && matchTopic
  })
})

const paginatedDevices = computed(() => {
  const start = (pagination.currentPage - 1) * pagination.pageSize
  return filteredDevices.value.slice(start, start + pagination.pageSize)
})

const handleSearch = () => {
  pagination.currentPage = 1
}

const handleReset = () => {
  queryForm.keyword = ''
  queryForm.type = ''
  queryForm.status = ''
  queryForm.topic = ''
  pagination.currentPage = 1
}

const handleSelectionChange = (selection) => {
  selectedRows.value = selection
}

// Sync Broker status simulation
const handleSyncStatus = () => {
  syncLoading.value = true
  setTimeout(() => {
    syncLoading.value = false
    ElMessage.success('成功与 MQTT Broker (8.163.51.74:9003) 完成心跳全量同步')
    addAuditLog({
      operator: userStore.currentUsername,
      action: '同步Broker设备状态',
      target: 'MQTT Broker',
      detail: '触发全量设备客户端连通性校验，心跳包已刷新',
      status: 'success',
      ip: '192.168.1.108',
    })
  }, 700)
}

// Single delete
const handleDeleteDevice = (row) => {
  allDevices.value = allDevices.value.filter((d) => d.id !== row.id)
  saveStoredDevices(allDevices.value)
  ElMessage.success(`设备【${row.name}】已成功移除`)
  addAuditLog({
    operator: userStore.currentUsername,
    action: '移除设备',
    target: row.id,
    detail: `删除了设备 ${row.name} (${row.id})`,
    status: 'warning',
    ip: '192.168.1.108',
  })
}

// Batch delete
const handleBatchDelete = () => {
  if (selectedRows.value.length === 0) return
  ElMessageBox.confirm(
    `确定要注销并删除选中的 ${selectedRows.value.length} 台设备吗？此操作将注销 MQTT 接入凭据！`,
    '批量删除警告',
    { confirmButtonText: '确认注销', cancelButtonText: '取消', type: 'error' },
  )
    .then(() => {
      const ids = selectedRows.value.map((r) => r.id)
      allDevices.value = allDevices.value.filter((d) => !ids.includes(d.id))
      saveStoredDevices(allDevices.value)
      ElMessage.success('已成功批量移除设备')
      selectedRows.value = []
      addAuditLog({
        operator: userStore.currentUsername,
        action: '批量删除设备',
        target: '批量设备',
        detail: `批量注销了 ${ids.length} 台设备节点`,
        status: 'warning',
        ip: '192.168.1.108',
      })
    })
    .catch(() => {})
}

// Batch Command
const handleBatchCommand = () => {
  ElMessageBox.prompt('请输入要向选中的所有设备广播下发的控制指令：', '批量指令下发', {
    confirmButtonText: '立即广播',
    cancelButtonText: '取消',
    inputValue: '{"cmd":"sync_clock","ts":' + Date.now() + '}',
  })
    .then(({ value }) => {
      ElMessage.success(`指令已成功向选中的 ${selectedRows.value.length} 台设备发布`)
      addAuditLog({
        operator: userStore.currentUsername,
        action: '批量下发指令',
        target: '批量设备',
        detail: `广播下发内容: ${value}`,
        status: 'success',
        ip: '192.168.1.108',
      })
    })
    .catch(() => {})
}

// Export Devices CSV
const handleExportDevices = () => {
  const headers = [
    '设备编号',
    '设备名称',
    '设备类型',
    '序列号',
    '通信协议',
    'MQTT主题',
    'Client ID',
    '状态',
    '安装位置',
  ]
  const rows = filteredDevices.value.map((d) => [
    d.id,
    d.name,
    d.typeName,
    d.sn,
    d.protocol,
    d.topic,
    d.clientId,
    d.status,
    d.location,
  ])

  const csvContent =
    'data:text/csv;charset=utf-8,\uFEFF' +
    [headers.join(','), ...rows.map((e) => e.join(','))].join('\n')
  const encodedUri = encodeURI(csvContent)
  const link = document.createElement('a')
  link.setAttribute('href', encodedUri)
  link.setAttribute('download', `IoT设备资产台账_${new Date().toISOString().slice(0, 10)}.csv`)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  ElMessage.success('设备资产台账已生成并下载')
}

// Create / Edit Device Dialog
const deviceDialogVisible = ref(false)
const isEditMode = ref(false)
const submitLoading = ref(false)
const deviceFormRef = ref(null)

const deviceFormData = reactive({
  id: '',
  name: '',
  deviceType: 'sensor',
  sn: '',
  protocol: 'MQTT 3.1.1',
  topic: 'test/topic/sample',
  clientId: '',
  ip: '',
  heartbeatInterval: 60,
  location: '',
  description: '',
})

const deviceFormRules = {
  name: [{ required: true, message: '请输入设备名称', trigger: 'blur' }],
  deviceType: [{ required: true, message: '请选择设备类型', trigger: 'change' }],
  sn: [{ required: true, message: '请输入设备SN序列号', trigger: 'blur' }],
  topic: [{ required: true, message: '请输入MQTT订阅/发布主题', trigger: 'blur' }],
  clientId: [{ required: true, message: '请输入MQTT Client ID', trigger: 'blur' }],
}

const openCreateModal = () => {
  isEditMode.value = false
  const randNum = Math.floor(100 + Math.random() * 900)
  deviceFormData.id = `AST-RES-${randNum}`
  deviceFormData.name = ''
  deviceFormData.deviceType = 'gateway'
  deviceFormData.sn = `SN-RES-202610-${randNum}`
  deviceFormData.protocol = 'MQTT 3.1.1'
  deviceFormData.topic = 'cloudhub/v1/telemetry'
  deviceFormData.clientId = `cloudhub_client_${randNum}`
  deviceFormData.ip = `192.168.10.${randNum % 250}`
  deviceFormData.heartbeatInterval = 60
  deviceFormData.location = '主数据中心 IDC-A区01机架'
  deviceFormData.description = ''
  deviceDialogVisible.value = true
}

const openEditModal = (row) => {
  isEditMode.value = true
  deviceFormData.id = row.id
  deviceFormData.name = row.name
  deviceFormData.deviceType = row.deviceType
  deviceFormData.sn = row.sn
  deviceFormData.protocol = row.protocol
  deviceFormData.topic = row.topic
  deviceFormData.clientId = row.clientId
  deviceFormData.ip = row.ip
  deviceFormData.heartbeatInterval = row.heartbeatInterval || 60
  deviceFormData.location = row.location
  deviceFormData.description = row.description || ''
  deviceDialogVisible.value = true
}

const handleDispatchFromEdit = () => {
  const dev = allDevices.value.find((d) => d.id === deviceFormData.id)
  if (dev) {
    deviceDialogVisible.value = false
    openCommandModal(dev)
  }
}

const submitDeviceForm = async () => {
  if (!deviceFormRef.value) return
  await deviceFormRef.value.validate((valid) => {
    if (valid) {
      submitLoading.value = true
      setTimeout(() => {
        if (isEditMode.value) {
          const idx = allDevices.value.findIndex((d) => d.id === deviceFormData.id)
          if (idx > -1) {
            allDevices.value[idx] = {
              ...allDevices.value[idx],
              name: deviceFormData.name,
              deviceType: deviceFormData.deviceType,
              typeName: typeNameMap[deviceFormData.deviceType] || '终端设备',
              sn: deviceFormData.sn,
              protocol: deviceFormData.protocol,
              topic: deviceFormData.topic,
              clientId: deviceFormData.clientId,
              ip: deviceFormData.ip,
              heartbeatInterval: deviceFormData.heartbeatInterval,
              location: deviceFormData.location,
              description: deviceFormData.description,
            }
          }
          ElMessage.success('设备参数已成功更新')
        } else {
          const newDev = {
            id: deviceFormData.id,
            name: deviceFormData.name,
            deviceType: deviceFormData.deviceType,
            typeName: typeNameMap[deviceFormData.deviceType] || '终端设备',
            sn: deviceFormData.sn,
            protocol: deviceFormData.protocol,
            brokerIp: '8.163.51.74',
            brokerPort: 9003,
            topic: deviceFormData.topic,
            clientId: deviceFormData.clientId,
            status: 'online',
            ip: deviceFormData.ip,
            firmware: 'v1.0.0',
            heartbeatInterval: deviceFormData.heartbeatInterval,
            location: deviceFormData.location,
            cpuUsage: 18,
            memoryUsage: 25,
            temperature: 24.5,
            rssi: -60,
            msgCountToday: 1,
            lastHeartbeat: '刚刚上线',
            description: deviceFormData.description,
          }
          allDevices.value.unshift(newDev)
          ElMessage.success('新设备已成功注册并连通 Broker')
        }

        saveStoredDevices(allDevices.value)
        submitLoading.value = false
        deviceDialogVisible.value = false
      }, 300)
    }
  })
}

// MQTT Command Modal
const cmdDialogVisible = ref(false)
const cmdSending = ref(false)
const activeCmdDevice = ref(null)
const selectedCmdTemplate = ref('ping')
const cmdForm = reactive({
  qos: 0,
  payload: '{"cmd": "ping", "timestamp": ' + Date.now() + '}',
})

const openCommandModal = (device) => {
  activeCmdDevice.value = device
  selectedCmdTemplate.value = 'ping'
  applyCmdTemplate('ping')
  cmdDialogVisible.value = true
}

const applyCmdTemplate = (val) => {
  const ts = Date.now()
  if (val === 'ping') {
    cmdForm.payload = JSON.stringify(
      { cmd: 'ping', client_id: activeCmdDevice.value?.clientId, timestamp: ts },
      null,
      2,
    )
  } else if (val === 'reboot') {
    cmdForm.payload = JSON.stringify(
      { cmd: 'system_reboot', delay: 3, force: true, timestamp: ts },
      null,
      2,
    )
  } else if (val === 'sync_time') {
    cmdForm.payload = JSON.stringify(
      { cmd: 'sync_ntp', server: 'ntp.aliyun.com', timestamp: ts },
      null,
      2,
    )
  } else if (val === 'custom') {
    cmdForm.payload = JSON.stringify({ action: 'set_config', sample_rate: 10 }, null, 2)
  }
}

const dispatchMqttCommand = () => {
  cmdSending.value = true
  setTimeout(() => {
    cmdSending.value = false
    cmdDialogVisible.value = false
    ElMessage.success({
      message: `已向 ${activeCmdDevice.value.name} (Topic: ${activeCmdDevice.value.topic}) 成功发布 MQTT 控制指令`,
      duration: 3000,
    })
    addAuditLog({
      operator: userStore.currentUsername,
      action: '下发控制指令',
      target: activeCmdDevice.value.id,
      detail: `Topic: ${activeCmdDevice.value.topic}, QoS: ${cmdForm.qos}, Payload: ${cmdForm.payload.replace(/\n/g, '')}`,
      status: 'success',
      ip: '192.168.1.108',
    })
  }, 600)
}

// Telemetry Drawer
const telemetryDrawerVisible = ref(false)
const activeDrawerDevice = ref(null)
const simulatedLogs = ref([])

const openTelemetryDrawer = (device) => {
  activeDrawerDevice.value = device
  simulatedLogs.value = [
    {
      time: new Date(Date.now() - 15000).toLocaleTimeString(),
      qos: 0,
      payload: `{"device_id":"${device.id}","temp":${device.temperature || 25.4},"rssi":${device.rssi || -60},"status":"ok"}`,
    },
    {
      time: new Date(Date.now() - 10000).toLocaleTimeString(),
      qos: 0,
      payload: `{"client_id":"${device.clientId}","cpu":${device.cpuUsage || 20},"mem":${device.memoryUsage || 30}}`,
    },
    {
      time: new Date(Date.now() - 3000).toLocaleTimeString(),
      qos: 0,
      payload: `{"msg":"Hello MQTT #${Math.floor(Math.random() * 50)}","heartbeat":true,"uptime_sec":18450}`,
    },
  ]
  telemetryDrawerVisible.value = true
}

const clearConsoleLogs = () => {
  simulatedLogs.value = []
  ElMessage.info('已清空实时遥测日志面板')
}

const businessTable = useBusinessTable(
  'devices',
  [
    { prop: 'assetInfo', label: '资产资源名称 / 编码' },
    { prop: 'status', label: '运行状态' },
    { prop: 'connection', label: '通信与接入参数' },
    { prop: 'protocol', label: '通信协议' },
    { prop: 'telemetry', label: '核心指标与健康度' },
    { prop: 'location', label: '部署节点与位置' },
    { prop: 'heartbeat', label: '最后同步' },
  ],
  {
    query: queryForm,
    pagination,
    clearSelection,
    viewMode,
    loading: tableLoading,
    total: () => filteredDevices.value.length,
    pageSizes: [6, 12, 24, 48],
  },
)
const formDraft = useBusinessDraft(deviceDialogVisible, deviceFormData, submitLoading)
</script>

<style scoped>
.device-name-box {
  display: flex;
  flex-direction: column;
}

.device-name-text {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-main);
}

.device-sn-sub {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 2px;
}

.device-sn {
  font-size: 11px;
  color: var(--text-regular);
  font-family: monospace;
}

.device-type-tag {
  font-size: 11px;
  background-color: var(--tag-sub-bg, var(--surface-muted));
  padding: 1px 7px;
  border-radius: 6px;
  color: var(--tag-sub-color, var(--text-regular));
  border: 1px solid var(--tag-sub-border, var(--border-color));
  transition: all 0.2s ease;
}

.status-cell {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.status-text {
  font-size: 12px;
  font-weight: 500;
}

.status-text.online {
  color: #10b981;
}

.status-text.warning {
  color: #f59e0b;
}

.status-text.offline {
  color: var(--text-muted);
}

.mqtt-info-cell {
  display: flex;
  flex-direction: column;
  line-height: 1.3;
}

.topic-row {
  display: flex;
  align-items: center;
  gap: 4px;
}

.topic-text {
  font-size: 12px;
  color: var(--accent-foreground, var(--primary-color));
  max-width: 170px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.client-id {
  font-size: 11px;
  color: var(--text-regular);
}

.telemetry-compact {
  display: flex;
  gap: 10px;
}

.tel-item {
  display: flex;
  flex-direction: column;
}

.tel-label {
  font-size: 10px;
  color: var(--text-muted);
}

.tel-val {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-main);
  font-family: monospace;
}

.val-warn {
  color: #ef4444;
}

.heartbeat-text {
  font-size: 12px;
  color: #10b981;
}

.heartbeat-text.is-stale {
  color: var(--text-muted);
}

.text-muted {
  font-size: 12px;
  color: var(--text-muted);
}

.mono {
  font-family: monospace;
}

.page-total-text {
  font-size: 12px;
  color: var(--text-regular);
}

/* Card View Mode */
.device-card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
  padding: 6px 0;
}

.device-tile-card {
  border-radius: 12px;
}

.tile-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--border-light);
}

.tile-title-box {
  display: flex;
  align-items: center;
  gap: 6px;
}

.tile-name {
  font-size: 14px;
  color: var(--text-main);
}

.tile-body {
  padding: 12px 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.tile-prop {
  font-size: 12px;
  display: flex;
  justify-content: space-between;
}

.tile-prop .k {
  color: var(--text-regular);
}

.tile-prop .v {
  color: var(--text-main);
  font-weight: 500;
}

.tile-footer {
  display: flex;
  align-items: center;
  justify-content: space-evenly;
  padding-top: 10px;
  border-top: 1px solid var(--border-light);
  flex-wrap: nowrap;
  white-space: nowrap;
  width: 100%;
  box-sizing: border-box;
}

.tile-footer .el-button {
  flex-shrink: 0;
  padding: 6px 14px;
}

/* Broker Notice in Command Dialog */
.broker-notice {
  background-color: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.25);
  padding: 8px 12px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #10b981;
}

.mono-textarea :deep(textarea) {
  font-family: monospace;
  font-size: 12px;
  background-color: var(--tag-sub-bg, var(--surface-muted));
  color: var(--text-main);
}

/* Telemetry Drawer Content */
.drawer-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.drawer-stat-bar {
  background-color: var(--tag-sub-bg, var(--surface-muted));
  border: 1px solid var(--border-color);
  padding: 12px;
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.drawer-chip {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 13px;
}

.drawer-chip .label {
  color: var(--text-regular);
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.metric-card {
  border: 1px solid var(--border-color);
  border-radius: 10px;
  padding: 12px;
  background-color: var(--card-bg);
  display: flex;
  flex-direction: column;
}

.m-title {
  font-size: 12px;
  color: var(--text-regular);
  margin-bottom: 6px;
}

.m-value {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-main);
  margin-bottom: 4px;
}

.m-danger {
  color: #ef4444;
}

.m-value small {
  font-size: 12px;
  font-weight: 400;
  color: var(--text-muted);
}

.m-sub {
  font-size: 11px;
  color: var(--text-muted);
}

.console-box {
  border: 1px solid var(--border-color);
  border-radius: 10px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.console-header {
  background-color: var(--tag-sub-bg, #f1f5f9);
  padding: 8px 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--border-color);
}

.console-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-main);
  display: flex;
  align-items: center;
  gap: 6px;
}

.console-logs {
  background-color: #0f172a;
  color: #f8fafc;
  font-family: monospace;
  font-size: 12px;
  padding: 12px;
  min-height: 180px;
  max-height: 240px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.console-log-row {
  display: flex;
  gap: 8px;
  line-height: 1.4;
  word-break: break-all;
}

.log-time {
  color: var(--text-muted);
}

.log-topic {
  color: #38bdf8;
}

.log-payload {
  color: #4ade80;
}

.table-op-btns {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  white-space: nowrap;
  flex-wrap: nowrap;
}
</style>
