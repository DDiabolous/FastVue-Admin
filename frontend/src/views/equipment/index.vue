<template>
  <PageContainer
    class="business-page business-equipment"
    title="设备管理示例"
    description="管理设备接入、状态与遥测信息，支持列表和卡片视图。本页使用本地演示数据。"
  >
    <!-- Top KPI Stats Row -->
    <div class="stats-collapse-box">
      <div class="stats-collapse-inner">
        <el-row :gutter="16" class="stats-row">
          <el-col :xs="12" :sm="12" :lg="6">
            <StatisticCard label="设备接入总台数" unit="台" tone="primary">
              <template #icon>
                <el-icon :size="18"><Monitor /></el-icon>
              </template>
              {{ totalEquipmentCount }}
              <template #hint>全域纳管</template>
            </StatisticCard>
          </el-col>

          <el-col :xs="12" :sm="12" :lg="6">
            <StatisticCard label="正常在线运行" unit="台" tone="success">
              <template #icon>
                <el-icon :size="18"><Connection /></el-icon>
              </template>
              {{ runningCount }}
              <template #hint>94.6% 在线</template>
            </StatisticCard>
          </el-col>

          <el-col :xs="12" :sm="12" :lg="6">
            <StatisticCard label="指标预警 / 异常" unit="台" tone="warning">
              <template #icon>
                <el-icon :size="18"><Warning /></el-icon>
              </template>
              {{ warningCount }}
              <template #hint>需关注</template>
            </StatisticCard>
          </el-col>

          <el-col :xs="12" :sm="12" :lg="6">
            <StatisticCard label="网络脱机 / 离线" unit="台" tone="danger">
              <template #icon>
                <el-icon :size="18"><CircleClose /></el-icon>
              </template>
              {{ offlineCount }}
              <template #hint>待复位</template>
            </StatisticCard>
          </el-col>
        </el-row>
      </div>
    </div>

    <!-- Filter Card (Compact Single Row by Default) -->

    <!-- Table Card -->
    <el-card shadow="never" class="data-card business-data-card">
      <FilterPanel :model="queryForm" @search="handleSearch">
        <el-form-item label="关键词">
          <el-input
            v-model="queryForm.keyword"
            placeholder="名称 / 编码 / MAC / 位置"
            title="支持设备名称、编码、MAC 和部署位置"
            clearable
            style="width: 220px"
          />
        </el-form-item>

        <el-form-item label="分类">
          <el-select
            v-model="queryForm.category"
            placeholder="全部类别"
            clearable
            style="width: 145px"
          >
            <el-option label="智能商用终端" value="terminal" />
            <el-option label="环境传感设备" value="sensor" />
            <el-option label="边缘智能网关" value="gateway" />
            <el-option label="AI视觉终端" value="ai_camera" />
            <el-option label="移动巡检终端" value="robot" />
            <el-option label="手持终端" value="pda" />
          </el-select>
        </el-form-item>

        <el-form-item label="状态">
          <el-select
            v-model="queryForm.status"
            placeholder="全部状态"
            clearable
            style="width: 125px"
          >
            <el-option label="运行" value="running" />
            <el-option label="待机" value="standby" />
            <el-option label="预警" value="warning" />
            <el-option label="离线" value="offline" />
          </el-select>
        </el-form-item>

        <template v-if="showMoreFilter">
          <el-form-item label="网络">
            <el-select
              v-model="queryForm.networkType"
              placeholder="全部网络"
              clearable
              style="width: 135px"
            >
              <el-option label="5G 全网通" value="5G" />
              <el-option label="Wi-Fi 6" value="Wi-Fi" />
              <el-option label="工业以太网" value="以太网" />
            </el-select>
          </el-form-item>
        </template>

        <template #actions>
          <el-form-item class="form-btn-item">
            <el-button link type="primary" size="small" class="expand-btn" @click="showMoreFilter = !showMoreFilter">
              {{ showMoreFilter ? '收起' : '展开' }}
              <el-icon class="el-icon--right">
                <component :is="showMoreFilter ? ArrowUp : ArrowDown" />
              </el-icon>
            </el-button>
            <el-button type="primary" :icon="Search" native-type="submit">查询</el-button>
            <el-button :icon="Refresh" @click="handleReset">重置</el-button>
          </el-form-item>
        </template>
      </FilterPanel>
      <TableToolbar
        :total="filteredEquipments.length"
        :selected="selectedRows.length"
        :columns="businessTable.columns"
        v-model:visible-columns="businessTable.visible.value"
        @reset-columns="businessTable.resetColumns"
      >
        <el-button type="primary" :icon="Plus" @click="openCreateModal">新增</el-button>
        <el-button
          type="warning"
          plain
          :icon="Promotion"
          :disabled="selectedRows.length === 0"
          @click="openBatchCommandModal"
        >
          批量指令
        </el-button>
        <el-button
          type="info"
          plain
          :icon="Upload"
          :disabled="selectedRows.length === 0"
          @click="openBatchOtaModal"
        >
          批量 OTA
        </el-button>
        <el-button
          type="danger"
          plain
          :icon="Delete"
          :disabled="selectedRows.length === 0"
          @click="handleBatchDelete"
        >
          批量注销
        </el-button>
        <el-button :icon="Download" @click="handleExportEquipments">导出</el-button>
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

      <!-- Table View Mode -->
      <el-table
        ref="tableRef"
        border
        @header-dragend="businessTable.resize"
        v-if="viewMode === 'table'"
        v-loading="tableLoading"
        :data="paginatedEquipments"
        row-key="id"
        stripe
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="48" align="center" />

        <el-table-column
          label="设备信息"
          min-width="210"
          key="deviceInfo"
          v-if="businessTable.isColumnVisible('deviceInfo')"
          :width="businessTable.columnWidth('deviceInfo', undefined)"
          prop="deviceInfo"
        >
          <template #default="{ row }">
            <div class="device-cell">
              <div class="device-icon-box" :class="getCategoryIconClass(row.category)">
                <el-icon :size="18"><component :is="getCategoryIcon(row.category)" /></el-icon>
              </div>
              <div class="device-meta">
                <span class="device-name">{{ row.name }}</span>
                <span class="device-model">{{ row.model }}</span>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column
          prop="deviceCode"
          label="设备编码"
          key="deviceCode"
          v-if="businessTable.isColumnVisible('deviceCode')"
          :width="businessTable.columnWidth('deviceCode', 160)"
        >
          <template #default="{ row }">
            <span class="code-tag">{{ row.deviceCode }}</span>
          </template>
        </el-table-column>

        <el-table-column
          label="设备分类"
          align="center"
          key="category"
          v-if="businessTable.isColumnVisible('category')"
          :width="businessTable.columnWidth('category', 130)"
          prop="category"
        >
          <template #default="{ row }">
            <el-tag size="small" effect="plain" class="category-tag">
              {{ row.categoryName }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column
          label="网络与信号"
          min-width="160"
          key="connection"
          v-if="businessTable.isColumnVisible('connection')"
          :width="businessTable.columnWidth('connection', undefined)"
          prop="connection"
        >
          <template #default="{ row }">
            <div class="network-cell">
              <div class="net-row">
                <span class="net-type">{{ row.networkType }}</span>
                <div class="signal-bars">
                  <span
                    v-for="i in 5"
                    :key="i"
                    class="signal-bar"
                    :class="{ active: i <= row.signalLevel }"
                  />
                </div>
              </div>
              <span class="ip-text">{{ row.ip }}</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column
          label="遥测负荷"
          min-width="150"
          key="telemetry"
          v-if="businessTable.isColumnVisible('telemetry')"
          :width="businessTable.columnWidth('telemetry', undefined)"
          prop="telemetry"
        >
          <template #default="{ row }">
            <div class="telemetry-compact">
              <div class="load-line">
                <span class="load-label">CPU:</span>
                <el-progress
                  :percentage="row.cpuLoad"
                  :color="getProgressColor(row.cpuLoad)"
                  :stroke-width="5"
                  style="width: 70px"
                />
              </div>
              <div class="temp-line">
                <span>
                  温度:
                  <strong>{{ row.temperature > 0 ? row.temperature + '℃' : '-' }}</strong>
                </span>
                <span v-if="row.battery < 100" class="battery-sub">电量: {{ row.battery }}%</span>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column
          prop="firmwareVersion"
          label="固件版本"
          align="center"
          key="firmwareVersion"
          v-if="businessTable.isColumnVisible('firmwareVersion')"
          :width="businessTable.columnWidth('firmwareVersion', 130)"
        >
          <template #default="{ row }">
            <span class="firmware-tag">{{ row.firmwareVersion }}</span>
          </template>
        </el-table-column>

        <el-table-column
          label="运行状态"
          align="center"
          key="status"
          v-if="businessTable.isColumnVisible('status')"
          :width="businessTable.columnWidth('status', 115)"
          prop="status"
        >
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" effect="light">
              <span class="status-dot" :class="row.status" />
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column
          label="远程电源"
          align="center"
          key="power"
          v-if="businessTable.isColumnVisible('power')"
          :width="businessTable.columnWidth('power', 90)"
          prop="power"
        >
          <template #default="{ row }">
            <el-switch
              v-model="row.powerStatus"
              :active-value="true"
              :inactive-value="false"
              active-color="#10b981"
              inactive-color="#94a3b8"
              @change="(val) => handlePowerChange(row, val)"
            />
          </template>
        </el-table-column>

        <el-table-column
          prop="location"
          label="部署物理位置"
          min-width="170"
          show-overflow-tooltip
          key="location"
          v-if="businessTable.isColumnVisible('location')"
          :width="businessTable.columnWidth('location', undefined)"
        />

        <!-- Operations Column (Streamlined to 3 clear actions, strictly in one horizontal row) -->
        <el-table-column label="操作" width="194" fixed="right" align="center">
          <template #default="{ row }">
            <div class="table-op-btns">
              <el-button
                link
                type="primary"
                size="small"
                :icon="Odometer"
                @click="openTelemetryDrawer(row)"
              >
                调测
              </el-button>
              <el-button link type="primary" size="small" :icon="Edit" @click="openEditModal(row)">
                编辑
              </el-button>
              <el-popconfirm
                title="确定删除该设备吗？"
                confirm-button-text="删除"
                cancel-button-text="取消"
                confirm-button-type="danger"
                width="auto"
                @confirm="handleDeleteEquipmentRow(row)"
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
      <div v-else class="card-view-grid">
        <el-card
          v-for="item in paginatedEquipments"
          :key="item.id"
          shadow="hover"
          class="device-grid-card"
        >
          <div class="grid-card-header">
            <div class="header-left">
              <div class="device-icon-box" :class="getCategoryIconClass(item.category)">
                <el-icon :size="18"><component :is="getCategoryIcon(item.category)" /></el-icon>
              </div>
              <div class="header-title-box">
                <span class="card-device-name" :title="item.name">{{ item.name }}</span>
                <span class="card-device-code" :title="item.deviceCode">{{ item.deviceCode }}</span>
              </div>
            </div>
            <el-tag :type="getStatusTagType(item.status)" size="small">
              {{ getStatusLabel(item.status) }}
            </el-tag>
          </div>

          <div class="grid-card-body">
            <div class="grid-metric-row">
              <div class="metric-item">
                <span class="metric-label">CPU 负载</span>
                <span class="metric-val">{{ item.cpuLoad }}%</span>
              </div>
              <div class="metric-item">
                <span class="metric-label">核心温度</span>
                <span class="metric-val" :class="{ 'text-warning': item.temperature > 60 }">
                  {{ item.temperature > 0 ? item.temperature + '℃' : '-' }}
                </span>
              </div>
              <div class="metric-item">
                <span class="metric-label">通信网络</span>
                <span class="metric-val">{{ item.networkType.slice(0, 7) }}</span>
              </div>
            </div>

            <div class="grid-loc-line">
              <el-icon><Location /></el-icon>
              <span :title="item.location">{{ item.location }}</span>
            </div>
          </div>

          <div class="grid-card-footer has-toggle">
            <div class="footer-left">
              <el-tooltip
                :content="item.powerStatus ? '设备运行中（点击停用）' : '设备已脱机（点击启用）'"
                placement="top"
              >
                <el-switch
                  v-model="item.powerStatus"
                  active-color="#10b981"
                  inactive-color="#94a3b8"
                  @change="(val) => handlePowerChange(item, val)"
                />
              </el-tooltip>
            </div>
            <div class="footer-actions">
              <el-button
                size="small"
                type="primary"
                plain
                :icon="Odometer"
                @click="openTelemetryDrawer(item)"
              >
                调测
              </el-button>
              <el-button size="small" :icon="Edit" @click="openEditModal(item)">编辑</el-button>
              <el-button size="small" :icon="Refresh" @click="handleQuickReboot(item)">
                重启
              </el-button>
            </div>
          </div>
        </el-card>
      </div>

      <!-- Pagination -->
      <TableEmpty
        v-if="viewMode === 'card' && !filteredEquipments.length"
        :loading="tableLoading"
        :filtered="businessTable.isFiltered.value"
        @reset="handleReset"
      />
      <div class="business-pagination">
        <span class="page-total-text">
          已纳管检索共
          <strong>{{ filteredEquipments.length }}</strong>
          台硬件终端设备
        </span>
        <el-pagination
          v-model:current-page="pagination.currentPage"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[6, 12, 24, 48]"
          :total="filteredEquipments.length"
          layout="total, sizes, prev, pager, next"
        />
      </div>
    </el-card>

    <!-- Telemetry & Remote Control Drawer -->
    <el-drawer
      class="business-overlay"
      v-model="drawerVisible"
      title="设备实时遥测调测面板与指令下发"
      size="min(560px, 100vw)"
      destroy-on-close
    >
      <div v-if="currentEquipment" class="drawer-content">
        <div class="drawer-header-device">
          <div class="device-icon-box lg" :class="getCategoryIconClass(currentEquipment.category)">
            <el-icon :size="24">
              <component :is="getCategoryIcon(currentEquipment.category)" />
            </el-icon>
          </div>
          <div class="drawer-header-meta">
            <div class="name-status-row">
              <span class="device-header-title">{{ currentEquipment.name }}</span>
              <el-tag :type="getStatusTagType(currentEquipment.status)" size="small">
                {{ getStatusLabel(currentEquipment.status) }}
              </el-tag>
            </div>
            <span class="sub-code">
              资产编码: {{ currentEquipment.deviceCode }} · 型号: {{ currentEquipment.model }}
            </span>
            <span class="sub-loc">部署位置: {{ currentEquipment.location }}</span>
          </div>
        </div>

        <el-divider content-position="left">实时遥测运行参数</el-divider>
        <el-row :gutter="12" class="telemetry-cards">
          <el-col :xs="24" :sm="8">
            <div class="telemetry-box">
              <span class="t-label">CPU 负载率</span>
              <span class="t-value" :style="{ color: getProgressColor(currentEquipment.cpuLoad) }">
                {{ currentEquipment.cpuLoad }}%
              </span>
              <el-progress
                :percentage="currentEquipment.cpuLoad"
                :color="getProgressColor(currentEquipment.cpuLoad)"
                :show-text="false"
                :stroke-width="4"
              />
            </div>
          </el-col>
          <el-col :xs="24" :sm="8">
            <div class="telemetry-box">
              <span class="t-label">系统内存</span>
              <span class="t-value text-primary">{{ currentEquipment.memoryLoad }}%</span>
              <el-progress
                :percentage="currentEquipment.memoryLoad"
                color="var(--accent-foreground, var(--primary-color))"
                :show-text="false"
                :stroke-width="4"
              />
            </div>
          </el-col>
          <el-col :xs="24" :sm="8">
            <div class="telemetry-box">
              <span class="t-label">核心工作温升</span>
              <span class="t-value" :class="{ 'text-danger': currentEquipment.temperature > 65 }">
                {{ currentEquipment.temperature > 0 ? currentEquipment.temperature + '℃' : '-' }}
              </span>
              <span class="t-sub">报警阈值: 75℃</span>
            </div>
          </el-col>
        </el-row>

        <el-divider content-position="left">硬件与网络规格</el-divider>
        <el-descriptions :column="1" border size="small">
          <el-descriptions-item label="设备物理 MAC">
            {{ currentEquipment.macAddress }}
          </el-descriptions-item>
          <el-descriptions-item label="分配 IP 地址">
            {{ currentEquipment.ip }}
          </el-descriptions-item>
          <el-descriptions-item label="接入通信网络">
            {{ currentEquipment.networkType }}
          </el-descriptions-item>
          <el-descriptions-item label="固件版本号">
            {{ currentEquipment.firmwareVersion }}
          </el-descriptions-item>
          <el-descriptions-item label="已持续在线时长">
            {{ currentEquipment.onlineDuration }}
          </el-descriptions-item>
          <el-descriptions-item label="最近心跳上报">
            {{ currentEquipment.lastHeartbeat }}
          </el-descriptions-item>
        </el-descriptions>

        <el-divider content-position="left">远程运维与指令下发</el-divider>
        <div class="control-actions-grid">
          <el-button
            type="warning"
            plain
            :icon="Refresh"
            :loading="rebooting"
            @click="handleRebootDevice"
          >
            重启设备系统
          </el-button>
          <el-button type="primary" plain :icon="Upload" @click="openOtaModal(currentEquipment)">
            下发固件升级
          </el-button>
          <el-button type="success" plain :icon="Select" @click="handleSelfDiagnose">
            一键硬件自检
          </el-button>
          <el-button type="info" plain :icon="Setting" @click="handleReloadConfig">
            重载业务参数
          </el-button>
        </div>

        <div class="command-log-box">
          <div class="log-title">最近指令执行流水:</div>
          <div class="log-entry" v-for="(log, idx) in recentLogs" :key="idx">
            <span class="log-time">{{ log.time }}</span>
            <span class="log-cmd">{{ log.action }}</span>
            <el-tag size="small" type="success" effect="dark" class="log-tag">成功</el-tag>
          </div>
        </div>
      </div>
    </el-drawer>

    <!-- Create / Edit Device Dialog -->
    <el-dialog
      :before-close="formDraft.beforeClose"
      :close-on-click-modal="false"
      class="business-overlay"
      v-model="deviceDialogVisible"
      :title="isEditMode ? '编辑设备参数' : '登记新硬件设备'"
      width="min(600px, 94vw)"
      destroy-on-close
    >
      <el-form
        ref="deviceFormRef"
        :model="deviceFormData"
        :rules="deviceFormRules"
        label-width="100px"
        style="padding: 10px 10px 0"
      >
        <el-row :gutter="16">
          <el-col :xs="24" :sm="12">
            <el-form-item label="设备名称" prop="name">
              <el-input v-model="deviceFormData.name" placeholder="如: 智能收银终端-02" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item label="设备编码" prop="deviceCode">
              <el-input v-model="deviceFormData.deviceCode" placeholder="如: POS-SH-2026-XXX" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :xs="24" :sm="12">
            <el-form-item label="设备分类" prop="category">
              <el-select v-model="deviceFormData.category" style="width: 100%">
                <el-option label="智能商用终端" value="terminal" />
                <el-option label="环境传感设备" value="sensor" />
                <el-option label="边缘智能网关" value="gateway" />
                <el-option label="AI视觉终端" value="ai_camera" />
                <el-option label="移动巡检终端" value="robot" />
                <el-option label="手持手持终端" value="pda" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item label="硬件型号" prop="model">
              <el-input v-model="deviceFormData.model" placeholder="如: SmartPOS-Ultra-X8" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :xs="24" :sm="12">
            <el-form-item label="通信网络" prop="networkType">
              <el-select v-model="deviceFormData.networkType" style="width: 100%">
                <el-option label="5G 全网通 + Wi-Fi 6" value="5G 全网通 + Wi-Fi 6" />
                <el-option label="工业级千兆以太网" value="工业级千兆以太网" />
                <el-option label="Wi-Fi 6 双频" value="Wi-Fi 6 双频" />
                <el-option label="5G 专网无线切片" value="5G 专网无线切片" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item label="IP 地址" prop="ip">
              <el-input v-model="deviceFormData.ip" placeholder="192.168.10.X" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :xs="24" :sm="12">
            <el-form-item label="MAC 地址" prop="macAddress">
              <el-input v-model="deviceFormData.macAddress" placeholder="00:1B:44:XX:XX:XX" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item label="固件版本" prop="firmwareVersion">
              <el-input v-model="deviceFormData.firmwareVersion" placeholder="v2.8.4" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="部署位置" prop="location">
          <el-input
            v-model="deviceFormData.location"
            placeholder="如: 华东旗舰展厅 智慧收银区A-01"
          />
        </el-form-item>

        <el-form-item label="快捷指令" v-if="isEditMode">
          <div style="display: flex; gap: 8px">
            <el-button
              size="small"
              type="warning"
              plain
              :icon="Refresh"
              @click="handleRebootFromEdit"
            >
              重启此设备
            </el-button>
            <el-button size="small" type="primary" plain :icon="Upload" @click="handleOtaFromEdit">
              推送固件升级
            </el-button>
          </div>
        </el-form-item>

        <el-form-item label="详细说明">
          <el-input
            v-model="deviceFormData.description"
            type="textarea"
            :rows="2"
            placeholder="填写设备用途与安装环境信息"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="formDraft.close">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSaveDevice">
          确认保存
        </el-button>
      </template>
    </el-dialog>

    <!-- OTA Firmware Dialog -->
    <el-dialog
      class="business-overlay"
      v-model="otaDialogVisible"
      title="下发固件 OTA 远程升级"
      width="min(480px, 94vw)"
    >
      <div style="padding: 10px 10px 0">
        <p style="margin-bottom: 14px; font-size: 13.5px; color: var(--text-regular)">
          目标升级目标:
          <strong>
            {{ targetOtaDevice ? targetOtaDevice.name : `已选 ${selectedRows.length} 台设备` }}
          </strong>
        </p>

        <el-form label-width="90px">
          <el-form-item label="目标固件">
            <el-select v-model="otaVersion" style="width: 100%">
              <el-option label="v3.2.0-LTS (推荐稳定版 - 2026Q4)" value="v3.2.0-LTS" />
              <el-option label="v3.1.5-Hotfix (安全修复补丁)" value="v3.1.5-Hotfix" />
              <el-option label="v4.0.0-Beta (AI加速固件预览版)" value="v4.0.0-Beta" />
            </el-select>
          </el-form-item>

          <el-form-item label="升级策略">
            <el-radio-group v-model="otaPolicy">
              <el-radio value="now">立即下发升级</el-radio>
              <el-radio value="idle">设备空闲时升级</el-radio>
            </el-radio-group>
          </el-form-item>
        </el-form>
      </div>

      <template #footer>
        <el-button @click="otaDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="otaLoading" @click="confirmOta">
          确认下发升级包
        </el-button>
      </template>
    </el-dialog>
  </PageContainer>
</template>

<script setup>
import PageContainer from '@/components/admin/PageContainer.vue'
import FilterPanel from '@/components/admin/FilterPanel.vue'
import TableToolbar from '@/components/admin/TableToolbar.vue'
import TableEmpty from '@/components/admin/TableEmpty.vue'
import StatisticCard from '@/components/admin/StatisticCard.vue'
import { useBusinessTable } from '@/composables/useBusinessTable'
import { useBusinessDraft } from '@/composables/useBusinessDraft'

import { ref, reactive, computed, onMounted } from 'vue'
import {
  Search,
  Refresh,
  Plus,
  Delete,
  Download,
  RefreshRight,
  Edit,
  ArrowDown,
  ArrowUp,
  Monitor,
  Connection,
  Warning,
  CircleClose,
  TopRight,
  Select,
  Promotion,
  Upload,
  Odometer,
  Location,
  Cpu,
  Setting,
  Operation,
  List,
  Grid,
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAdminStore } from '@/stores/admin'
import { getStoredEquipments, saveStoredEquipments, addAuditLog } from '@/utils/mockData'

const userStore = useAdminStore()

// State
const tableRef = ref()
const clearSelection = () => {
  tableRef.value?.clearSelection()
  selectedRows.value = []
}
const tableLoading = ref(false)
const allEquipments = ref([])
const selectedRows = ref([])
const viewMode = ref('table')
const showStats = ref(true)
const showMoreFilter = ref(false)

// Query Form
const queryForm = reactive({
  keyword: '',
  category: '',
  status: '',
  networkType: '',
})

// Pagination
const pagination = reactive({
  currentPage: 1,
  pageSize: 10,
})

// Counters
const totalEquipmentCount = computed(() => 1580 + allEquipments.value.length - 6)
const runningCount = computed(
  () => allEquipments.value.filter((e) => e.status === 'running').length + 1488,
)
const warningCount = computed(
  () => allEquipments.value.filter((e) => e.status === 'warning').length + 22,
)
const offlineCount = computed(
  () => allEquipments.value.filter((e) => e.status === 'offline').length + 64,
)

// Filter
const filteredEquipments = computed(() => {
  return allEquipments.value.filter((e) => {
    if (queryForm.keyword) {
      const kw = queryForm.keyword.toLowerCase().trim()
      const matchName = e.name.toLowerCase().includes(kw)
      const matchCode = e.deviceCode.toLowerCase().includes(kw)
      const matchMac = e.macAddress.toLowerCase().includes(kw)
      const matchLoc = e.location.toLowerCase().includes(kw)
      if (!matchName && !matchCode && !matchMac && !matchLoc) return false
    }
    if (queryForm.category && e.category !== queryForm.category) return false
    if (queryForm.status && e.status !== queryForm.status) return false
    if (queryForm.networkType && !e.networkType.includes(queryForm.networkType)) return false
    return true
  })
})

const paginatedEquipments = computed(() => {
  const start = (pagination.currentPage - 1) * pagination.pageSize
  return filteredEquipments.value.slice(start, start + pagination.pageSize)
})

// Helpers
const getCategoryIcon = (cat) => {
  const map = {
    terminal: 'Monitor',
    sensor: 'Connection',
    gateway: 'Cpu',
    ai_camera: 'View',
    robot: 'Promotion',
    pda: 'Iphone',
  }
  return map[cat] || 'Monitor'
}

const getCategoryIconClass = (cat) => {
  const map = {
    terminal: 'icon-terminal',
    sensor: 'icon-sensor',
    gateway: 'icon-gateway',
    ai_camera: 'icon-ai',
    robot: 'icon-robot',
    pda: 'icon-pda',
  }
  return map[cat] || 'icon-terminal'
}

const getStatusLabel = (st) => {
  const map = {
    running: '在线运行',
    standby: '就绪待机',
    warning: '指标预警',
    offline: '网络脱机',
  }
  return map[st] || st
}

const getStatusTagType = (st) => {
  const map = {
    running: 'success',
    standby: 'info',
    warning: 'warning',
    offline: 'danger',
  }
  return map[st] || 'info'
}

const getProgressColor = (val) => {
  if (val >= 80) return '#ef4444'
  if (val >= 60) return '#f59e0b'
  return '#10b981'
}

// Load data
const loadEquipmentData = () => {
  tableLoading.value = true
  setTimeout(() => {
    allEquipments.value = getStoredEquipments()
    tableLoading.value = false
  }, 250)
}

const handleSearch = () => {
  pagination.currentPage = 1
}

const handleReset = () => {
  queryForm.keyword = ''
  queryForm.category = ''
  queryForm.status = ''
  queryForm.networkType = ''
  pagination.currentPage = 1
}

const handleSelectionChange = (rows) => {
  selectedRows.value = rows
}

// Power toggle
const handlePowerChange = (row, val) => {
  row.status = val ? 'running' : 'offline'
  saveStoredEquipments(allEquipments.value)
  ElMessage.success(`设备【${row.name}】远程电源已${val ? '开启 (上电就绪)' : '关闭 (进入脱机)'}`)
  addAuditLog({
    operator: userStore.currentUsername,
    action: '远程控制电源',
    target: row.deviceCode,
    detail: `电源指令: ${val ? '开机' : '断电'}, 设备: ${row.name}`,
    status: 'success',
    ip: '192.168.1.108',
  })
}

// Drawer
const drawerVisible = ref(false)
const currentEquipment = ref(null)
const rebooting = ref(false)

const recentLogs = ref([
  { time: '16:05:12', action: '接收到遥测心跳报文 (Heartbeat ACK)' },
  { time: '15:42:30', action: '同步下发网络时间 NTP 校验' },
  { time: '14:20:18', action: '采集并上报工作温度与内存负荷' },
])

const openTelemetryDrawer = (row) => {
  currentEquipment.value = row
  drawerVisible.value = true
}

const handleRebootDevice = () => {
  rebooting.value = true
  setTimeout(() => {
    rebooting.value = false
    ElMessage.success(`重启指令下发成功！设备【${currentEquipment.value.name}】正在进行安全热复位`)
    recentLogs.value.unshift({
      time: new Date().toTimeString().slice(0, 8),
      action: '下发远程软复位热重启指令 (SysReboot)',
    })
  }, 1000)
}

const handleQuickReboot = (item) => {
  ElMessageBox.confirm(`确定要远程重启设备【${item.name}】吗？`, '远程指令确认', {
    confirmButtonText: '立即重启',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(() => {
      ElMessage.success(`设备【${item.name}】重启指令已发送`)
    })
    .catch(() => {})
}

const handleSelfDiagnose = () => {
  ElMessage.success('已启动硬件多传感器自检自查程序，自检通过 (Status 200 OK)')
}

const handleReloadConfig = () => {
  ElMessage.success('已下发最新业务路由与心跳配置参数')
}

// Device Dialog
const deviceDialogVisible = ref(false)
const isEditMode = ref(false)
const deviceFormRef = ref(null)
const submitLoading = ref(false)

const deviceFormData = reactive({
  id: '',
  name: '',
  deviceCode: '',
  category: 'terminal',
  model: '',
  networkType: '5G 全网通 + Wi-Fi 6',
  ip: '',
  macAddress: '',
  firmwareVersion: 'v2.8.4',
  location: '',
  description: '',
})

const deviceFormRules = {
  name: [{ required: true, message: '请输入设备名称', trigger: 'blur' }],
  deviceCode: [{ required: true, message: '请输入设备资产编码', trigger: 'blur' }],
  model: [{ required: true, message: '请输入硬件型号', trigger: 'blur' }],
  location: [{ required: true, message: '请输入部署物理位置', trigger: 'blur' }],
}

const openCreateModal = () => {
  isEditMode.value = false
  const randNum = Math.floor(100 + Math.random() * 900)
  deviceFormData.id = `EQP-${randNum}`
  deviceFormData.name = ''
  deviceFormData.deviceCode = `EQP-DEV-2026-${randNum}`
  deviceFormData.category = 'terminal'
  deviceFormData.model = 'SmartEdge-Node-X5'
  deviceFormData.networkType = '5G 全网通 + Wi-Fi 6'
  deviceFormData.ip = `192.168.10.${randNum % 250}`
  deviceFormData.macAddress = `00:1B:44:A1:${randNum % 90}:${randNum % 90}`
  deviceFormData.firmwareVersion = 'v2.8.4'
  deviceFormData.location = '主数据中心 智能展厅A-01'
  deviceFormData.description = ''
  deviceDialogVisible.value = true
}

const openEditModal = (row) => {
  isEditMode.value = true
  deviceFormData.id = row.id
  deviceFormData.name = row.name
  deviceFormData.deviceCode = row.deviceCode
  deviceFormData.category = row.category
  deviceFormData.model = row.model
  deviceFormData.networkType = row.networkType
  deviceFormData.ip = row.ip
  deviceFormData.macAddress = row.macAddress
  deviceFormData.firmwareVersion = row.firmwareVersion
  deviceFormData.location = row.location
  deviceFormData.description = row.description || ''
  deviceDialogVisible.value = true
}

const categoryNameMap = {
  terminal: '智能商用终端',
  sensor: '环境传感设备',
  gateway: '边缘智能网关',
  ai_camera: 'AI视觉终端',
  robot: '移动巡检终端',
  pda: '手持手持终端',
}

const handleSaveDevice = () => {
  deviceFormRef.value.validate((valid) => {
    if (valid) {
      submitLoading.value = true
      setTimeout(() => {
        if (isEditMode.value) {
          const idx = allEquipments.value.findIndex((e) => e.id === deviceFormData.id)
          if (idx > -1) {
            allEquipments.value[idx] = {
              ...allEquipments.value[idx],
              name: deviceFormData.name,
              deviceCode: deviceFormData.deviceCode,
              category: deviceFormData.category,
              categoryName: categoryNameMap[deviceFormData.category],
              model: deviceFormData.model,
              networkType: deviceFormData.networkType,
              ip: deviceFormData.ip,
              macAddress: deviceFormData.macAddress,
              firmwareVersion: deviceFormData.firmwareVersion,
              location: deviceFormData.location,
              description: deviceFormData.description,
            }
          }
          ElMessage.success('设备参数已更新')
        } else {
          const newEq = {
            id: deviceFormData.id,
            name: deviceFormData.name,
            deviceCode: deviceFormData.deviceCode,
            category: deviceFormData.category,
            categoryName: categoryNameMap[deviceFormData.category],
            model: deviceFormData.model,
            networkType: deviceFormData.networkType,
            ip: deviceFormData.ip,
            macAddress: deviceFormData.macAddress,
            firmwareVersion: deviceFormData.firmwareVersion,
            signalLevel: 5,
            status: 'running',
            powerStatus: true,
            cpuLoad: 25,
            memoryLoad: 35,
            temperature: 36.2,
            battery: 100,
            location: deviceFormData.location,
            lastHeartbeat: '刚刚',
            onlineDuration: '新纳管',
            description: deviceFormData.description,
          }
          allEquipments.value.unshift(newEq)
          ElMessage.success('新硬件设备登记成功')
        }
        saveStoredEquipments(allEquipments.value)
        submitLoading.value = false
        deviceDialogVisible.value = false
      }, 300)
    }
  })
}

// OTA
const otaDialogVisible = ref(false)
const targetOtaDevice = ref(null)
const otaVersion = ref('v3.2.0-LTS')
const otaPolicy = ref('now')
const otaLoading = ref(false)

const openOtaModal = (row) => {
  targetOtaDevice.value = row
  otaDialogVisible.value = true
}

const openBatchOtaModal = () => {
  targetOtaDevice.value = null
  otaDialogVisible.value = true
}

const confirmOta = () => {
  otaLoading.value = true
  setTimeout(() => {
    otaLoading.value = false
    otaDialogVisible.value = false
    if (targetOtaDevice.value) {
      targetOtaDevice.value.firmwareVersion = otaVersion.value
      ElMessage.success(
        `固件升级任务已推送给【${targetOtaDevice.value.name}】，固件版本目标: ${otaVersion.value}`,
      )
    } else {
      const ids = selectedRows.value.map((r) => r.id)
      allEquipments.value.forEach((e) => {
        if (ids.includes(e.id)) {
          e.firmwareVersion = otaVersion.value
        }
      })
      ElMessage.success(`已向选中的 ${ids.length} 台设备批量分发升级固件包 (${otaVersion.value})`)
      selectedRows.value = []
    }
    saveStoredEquipments(allEquipments.value)
  }, 800)
}

const handleDeleteEquipmentRow = (row) => {
  allEquipments.value = allEquipments.value.filter((e) => e.id !== row.id)
  saveStoredEquipments(allEquipments.value)
  ElMessage.success(`设备【${row.name}】已成功注销`)
}

const handleRebootFromEdit = () => {
  deviceDialogVisible.value = false
  ElMessage.success(`已向设备【${deviceFormData.name}】下发远程软复位重启指令`)
}

const handleOtaFromEdit = () => {
  const dev = allEquipments.value.find((e) => e.id === deviceFormData.id)
  if (dev) {
    deviceDialogVisible.value = false
    openOtaModal(dev)
  }
}

// Batch Command
const openBatchCommandModal = () => {
  ElMessageBox.confirm(
    `确定要向选中的 ${selectedRows.value.length} 台设备统一发送遥测自检与状态上报指令吗？`,
    '批量控制指令',
    {
      confirmButtonText: '立即发送',
      cancelButtonText: '取消',
      type: 'warning',
    },
  )
    .then(() => {
      ElMessage.success(`指令已通过集群通信网关广播至选中的 ${selectedRows.value.length} 台设备`)
      selectedRows.value = []
    })
    .catch(() => {})
}

// Batch Delete
const handleBatchDelete = () => {
  ElMessageBox.confirm(
    `确定要从平台中彻底注销选中的 ${selectedRows.value.length} 台设备吗？`,
    '注销警示',
    {
      confirmButtonText: '确认注销',
      cancelButtonText: '取消',
      type: 'error',
    },
  )
    .then(() => {
      const ids = selectedRows.value.map((r) => r.id)
      allEquipments.value = allEquipments.value.filter((e) => !ids.includes(e.id))
      saveStoredEquipments(allEquipments.value)
      ElMessage.success(`已注销 ${ids.length} 台设备台账`)
      selectedRows.value = []
    })
    .catch(() => {})
}

// Commands
const handleDeviceCommand = (cmd, row) => {
  if (cmd === 'reboot') {
    handleQuickReboot(row)
  } else if (cmd === 'ota') {
    openOtaModal(row)
  } else if (cmd === 'diagnose') {
    ElMessage.success(`已启动设备【${row.name}】远程全面诊断`)
  } else if (cmd === 'delete') {
    ElMessageBox.confirm(`确定要从台账中注销设备【${row.name}】吗？`, '注销确认', {
      confirmButtonText: '确定注销',
      cancelButtonText: '取消',
      type: 'error',
    })
      .then(() => {
        allEquipments.value = allEquipments.value.filter((e) => e.id !== row.id)
        saveStoredEquipments(allEquipments.value)
        ElMessage.success('设备台账已注销')
      })
      .catch(() => {})
  }
}

// Export CSV
const handleExportEquipments = () => {
  const headers = [
    '设备编号',
    '设备名称',
    '设备编码',
    '设备分类',
    '硬件型号',
    '通信网络',
    'IP地址',
    'MAC地址',
    '固件版本',
    '状态',
    '部署位置',
  ]
  const rows = filteredEquipments.value.map((e) => [
    e.id,
    e.name,
    e.deviceCode,
    e.categoryName,
    e.model,
    e.networkType,
    e.ip,
    e.macAddress,
    e.firmwareVersion,
    getStatusLabel(e.status),
    e.location,
  ])

  const csvContent =
    'data:text/csv;charset=utf-8,\uFEFF' +
    [headers.join(','), ...rows.map((r) => r.join(','))].join('\n')
  const encodedUri = encodeURI(csvContent)
  const link = document.createElement('a')
  link.setAttribute('href', encodedUri)
  link.setAttribute('download', `硬件设备资产台账_${new Date().toISOString().slice(0, 10)}.csv`)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  ElMessage.success('设备台账 CSV 已生成并开始下载')
}

onMounted(() => {
  loadEquipmentData()
})

const businessTable = useBusinessTable(
  'equipment',
  [
    { prop: 'deviceInfo', label: '设备信息' },
    { prop: 'deviceCode', label: '设备编码' },
    { prop: 'category', label: '设备分类' },
    { prop: 'connection', label: '网络与信号' },
    { prop: 'telemetry', label: '遥测负荷' },
    { prop: 'firmwareVersion', label: '固件版本' },
    { prop: 'status', label: '运行状态' },
    { prop: 'power', label: '远程电源' },
    { prop: 'location', label: '部署物理位置' },
  ],
  {
    query: queryForm,
    pagination,
    clearSelection,
    viewMode,
    showStats,
    showMoreFilter,
    loading: tableLoading,
    total: () => filteredEquipments.value.length,
    pageSizes: [10, 20, 50, 100],
  },
)
const formDraft = useBusinessDraft(deviceDialogVisible, deviceFormData, submitLoading)
</script>

<style scoped>
.stats-row {
  margin-bottom: 0px;
}

.icon-primary {
  background-color: rgba(var(--accent-rgb), 0.12);
  color: var(--accent-foreground, var(--primary-color));
}

.icon-success {
  background-color: rgba(16, 185, 129, 0.12);
  color: #10b981;
}

.icon-warning {
  background-color: rgba(245, 158, 11, 0.12);
  color: #f59e0b;
}

.icon-danger {
  background-color: rgba(239, 68, 68, 0.12);
  color: #ef4444;
}

.device-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.device-icon-box {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.device-icon-box.lg {
  width: 48px;
  height: 48px;
  border-radius: 10px;
}

.icon-terminal {
  background: rgba(59, 130, 246, 0.12);
  color: #3b82f6;
}
.icon-sensor {
  background: rgba(16, 185, 129, 0.12);
  color: #10b981;
}
.icon-gateway {
  background: rgba(139, 92, 246, 0.12);
  color: #8b5cf6;
}
.icon-ai {
  background: rgba(236, 72, 153, 0.12);
  color: #ec4899;
}
.icon-robot {
  background: rgba(245, 158, 11, 0.12);
  color: #f59e0b;
}
.icon-pda {
  background: rgba(14, 165, 233, 0.12);
  color: #0ea5e9;
}

.device-meta {
  display: flex;
  flex-direction: column;
}

.device-name {
  font-weight: 600;
  font-size: 13.5px;
  color: var(--text-main);
}

.device-model {
  font-size: 12px;
  color: var(--text-muted);
}

.code-tag {
  font-family: monospace;
  font-weight: 600;
  color: var(--text-regular);
  font-size: 12px;
}

.category-tag,
:global(html.dark) .category-tag {
  background-color: transparent !important;
  border-color: transparent !important;
  border: none !important;
  color: var(--primary-color) !important;
  font-weight: 500;
  padding: 0 4px;
}

.network-cell {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.net-row {
  display: flex;
  align-items: center;
  gap: 6px;
}

.net-type {
  font-size: 12px;
  color: var(--text-regular);
}

.signal-bars {
  display: flex;
  align-items: flex-end;
  gap: 2px;
  height: 12px;
}

.signal-bar {
  width: 3px;
  height: 4px;
  background-color: var(--border-color);
  border-radius: 1px;
}

.signal-bar:nth-child(2) {
  height: 6px;
}
.signal-bar:nth-child(3) {
  height: 8px;
}
.signal-bar:nth-child(4) {
  height: 10px;
}
.signal-bar:nth-child(5) {
  height: 12px;
}

.signal-bar.active {
  background-color: #10b981;
}

.ip-text {
  font-size: 11.5px;
  color: var(--text-muted);
  font-family: monospace;
}

.telemetry-compact {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.load-line {
  display: flex;
  align-items: center;
  gap: 6px;
}

.load-label {
  font-size: 11px;
  color: var(--text-muted);
}

.temp-line {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11.5px;
  color: var(--text-regular);
}

.battery-sub {
  color: var(--text-muted);
}

.firmware-tag {
  font-family: monospace;
  font-size: 11.5px;
  color: var(--text-muted);
  background: var(--bg-color);
  padding: 2px 6px;
  border-radius: 4px;
}

.status-dot {
  display: inline-block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  margin-right: 4px;
}

.status-dot.running {
  background-color: #10b981;
}
.status-dot.standby {
  background-color: var(--text-muted);
}
.status-dot.warning {
  background-color: #f59e0b;
}
.status-dot.offline {
  background-color: #ef4444;
}

/* Grid View */
.card-view-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
  margin-top: 8px;
}

.device-grid-card {
  border-radius: var(--radius-lg, 12px);
  background: var(--card-bg);
  border: 1px solid var(--border-color);
}

.grid-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-title-box {
  display: flex;
  flex-direction: column;
}

.card-device-name {
  font-weight: 600;
  font-size: 14px;
  color: var(--text-main);
}

.card-device-code {
  font-size: 11.5px;
  color: var(--text-muted);
  font-family: monospace;
}

.grid-card-body {
  padding: 10px 0;
  border-top: 1px solid var(--border-color);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.grid-metric-row {
  display: flex;
  justify-content: space-between;
}

.metric-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.metric-label {
  font-size: 11px;
  color: var(--text-muted);
}

.metric-val {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-main);
}

.grid-loc-line {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--text-muted);
}

.grid-card-footer {
  display: flex;
  align-items: center;
  justify-content: space-evenly;
  gap: 8px;
  margin-top: 12px;
  padding-top: 10px;
  border-top: 1px solid var(--border-light);
  flex-wrap: nowrap;
  white-space: nowrap;
}

.grid-card-footer.has-toggle {
  justify-content: space-between;
}

.grid-card-footer .footer-left {
  display: inline-flex;
  align-items: center;
  flex-shrink: 0;
}

.grid-card-footer .footer-actions {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
  flex-wrap: nowrap;
}

.grid-card-footer .footer-actions .el-button {
  flex-shrink: 0;
}

.page-total-text {
  font-size: 13px;
  color: var(--text-muted);
}

/* Drawer */
.drawer-content {
  padding: 4px 10px;
}

.drawer-header-device {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px;
  background: var(--bg-color);
  border-radius: var(--radius-lg, 12px);
  margin-bottom: 12px;
}

.drawer-header-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.name-status-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.device-header-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-main);
}

.sub-code,
.sub-loc {
  font-size: 12px;
  color: var(--text-muted);
}

.telemetry-cards {
  margin-bottom: 16px;
}

.telemetry-box {
  padding: 12px;
  border-radius: var(--radius-md, 10px);
  background: var(--bg-color);
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.t-label {
  font-size: 11.5px;
  color: var(--text-muted);
}

.t-value {
  font-size: 18px;
  font-weight: 700;
}

.t-sub {
  font-size: 10px;
  color: var(--text-muted);
}

.control-actions-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-bottom: 18px;
}

.command-log-box {
  padding: 12px;
  border-radius: var(--radius-md, 10px);
  background: var(--bg-color);
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.log-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
}

.log-entry {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 12px;
}

.log-time {
  color: var(--text-muted);
  font-family: monospace;
}

.log-cmd {
  color: var(--text-regular);
  flex: 1;
  margin: 0 8px;
}

.log-tag {
  font-size: 10px;
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
