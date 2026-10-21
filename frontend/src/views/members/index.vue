<template>
  <PageContainer
    class="business-page business-members"
    title="会员管理示例"
    description="管理会员资料、等级与状态。统计及操作均使用本地演示数据。"
  >
    <template #actions>
      <el-button :icon="showStats ? ArrowUp : DataAnalysis" @click="showStats = !showStats">
        {{ showStats ? '收起统计' : '展开统计' }}
      </el-button>
    </template>
    <!-- Top KPI Stats Row (Collapsible & Compact) -->
    <el-collapse-transition>
      <div v-show="showStats" class="stats-collapse-wrap">
        <el-row :gutter="16" class="stats-row">
          <el-col :xs="12" :sm="12" :lg="6">
            <StatisticCard label="全平台用户总量" unit="人" tone="primary">
              <template #icon>
                <el-icon :size="18"><User /></el-icon>
              </template>
              {{ totalUserCount.toLocaleString() }}
              <template #hint>
                <el-icon :size="11"><TopRight /></el-icon>
                +12.8%
              </template>
            </StatisticCard>
          </el-col>

          <el-col :xs="12" :sm="12" :lg="6">
            <StatisticCard label="今日新增活跃" unit="人" tone="success">
              <template #icon>
                <el-icon :size="18"><Opportunity /></el-icon>
              </template>
              1,248
              <template #hint>
                <el-icon :size="11"><TopRight /></el-icon>
                92.4%
              </template>
            </StatisticCard>
          </el-col>

          <el-col :xs="12" :sm="12" :lg="6">
            <StatisticCard label="VIP / 核心客户" unit="人" tone="warning">
              <template #icon>
                <el-icon :size="18"><Medal /></el-icon>
              </template>
              18,320
              <template #hint>14.3%</template>
            </StatisticCard>
          </el-col>

          <el-col :xs="12" :sm="12" :lg="6">
            <StatisticCard label="风控受限 / 冻结" unit="人" tone="danger">
              <template #icon>
                <el-icon :size="18"><Warning /></el-icon>
              </template>
              {{ frozenUserCount }}
              <template #hint>IP防护</template>
            </StatisticCard>
          </el-col>
        </el-row>
      </div>
    </el-collapse-transition>

    <!-- Filter Card (Compact Single Row by Default) -->

    <!-- Table Card -->
    <el-card shadow="never" class="data-card business-data-card">
      <FilterPanel :model="queryForm" @search="handleSearch">
        <el-form-item label="关键词">
          <el-input
            v-model="queryForm.keyword"
            placeholder="UID / 姓名 / 手机号"
            title="支持 UID、昵称、姓名和手机号"
            clearable
            style="width: 200px"
          />
        </el-form-item>

        <el-form-item label="等级">
          <el-select
            v-model="queryForm.level"
            placeholder="全部等级"
            clearable
            style="width: 130px"
          >
            <el-option label="普通会员" value="regular" />
            <el-option label="白银会员" value="silver" />
            <el-option label="黄金VIP" value="gold" />
            <el-option label="钻石企业客户" value="diamond" />
          </el-select>
        </el-form-item>

        <el-form-item label="状态">
          <el-select
            v-model="queryForm.status"
            placeholder="全部状态"
            clearable
            style="width: 110px"
          >
            <el-option label="正常" :value="1" />
            <el-option label="冻结" :value="0" />
          </el-select>
        </el-form-item>

        <template v-if="showMoreFilter">
          <el-form-item label="实名">
            <el-select
              v-model="queryForm.verifyStatus"
              placeholder="实名状态"
              clearable
              style="width: 120px"
            >
              <el-option label="已实名" :value="1" />
              <el-option label="审核中" :value="2" />
              <el-option label="未实名" :value="0" />
            </el-select>
          </el-form-item>

          <el-form-item label="渠道">
            <el-select
              v-model="queryForm.channel"
              placeholder="全部渠道"
              clearable
              style="width: 130px"
            >
              <el-option label="Web 官方网站" value="web" />
              <el-option label="微信小程序" value="wechat" />
              <el-option label="移动端 App" value="app" />
              <el-option label="开放平台 API" value="open_api" />
            </el-select>
          </el-form-item>
        </template>

        <el-form-item class="form-btn-item">
          <el-button type="primary" :icon="Search" native-type="submit">查询</el-button>
          <el-button :icon="Refresh" @click="handleReset">重置</el-button>
          <el-button link type="primary" size="small" @click="showMoreFilter = !showMoreFilter">
            {{ showMoreFilter ? '收起' : '展开' }}
            <el-icon class="el-icon--right">
              <component :is="showMoreFilter ? ArrowUp : ArrowDown" />
            </el-icon>
          </el-button>
        </el-form-item>
      </FilterPanel>
      <TableToolbar
        :loading="tableLoading"
        :total="filteredMembers.length"
        :selected="selectedRows.length"
        :columns="businessTable.columns"
        v-model:visible-columns="businessTable.visible.value"
        @reset-columns="businessTable.resetColumns"
        @refresh="loadMembersData"
      >
        <el-button type="primary" :icon="Plus" @click="openCreateModal">新增</el-button>
        <el-button
          type="warning"
          plain
          :icon="Medal"
          :disabled="selectedRows.length === 0"
          @click="openBatchLevelModal"
        >
          批量调级
        </el-button>
        <el-button
          type="danger"
          plain
          :icon="Lock"
          :disabled="selectedRows.length === 0"
          @click="handleBatchFreeze"
        >
          批量冻结
        </el-button>
        <el-button :icon="Download" @click="handleExportMembers">导出</el-button>
        <el-button v-if="selectedRows.length" link @click="clearSelection">清空已选</el-button>
      </TableToolbar>

      <!-- Batch Toolbar Row -->

      <!-- Main Member Table -->
      <el-table
        border
        @header-dragend="businessTable.resize"
        ref="tableRef"
        v-loading="tableLoading"
        :data="paginatedMembers"
        row-key="id"
        stripe
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="48" align="center" />

        <el-table-column
          prop="id"
          label="用户 UID"
          key="id"
          v-if="businessTable.isColumnVisible('id')"
          :width="businessTable.columnWidth('id', 120)"
        >
          <template #default="{ row }">
            <span class="uid-tag">{{ row.id }}</span>
          </template>
        </el-table-column>

        <el-table-column
          label="用户画像"
          min-width="190"
          key="profile"
          v-if="businessTable.isColumnVisible('profile')"
          :width="businessTable.columnWidth('profile', undefined)"
          prop="profile"
        >
          <template #default="{ row }">
            <div class="user-profile-cell">
              <el-avatar :size="36" :src="row.avatar" />
              <div class="profile-info">
                <div class="nickname-row">
                  <span class="user-nickname">{{ row.nickname }}</span>
                  <el-tag
                    v-if="row.memberLevel === 'diamond'"
                    size="small"
                    effect="dark"
                    type="danger"
                    class="mini-level-tag"
                  >
                    KA钻石
                  </el-tag>
                </div>
                <span class="realname-sub">{{ row.realName }} (@{{ row.username }})</span>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column
          label="联系方式"
          min-width="180"
          key="contact"
          v-if="businessTable.isColumnVisible('contact')"
          :width="businessTable.columnWidth('contact', undefined)"
          prop="contact"
        >
          <template #default="{ row }">
            <div class="contact-box">
              <div class="contact-line">
                <el-icon :size="13"><Iphone /></el-icon>
                <span>{{ row.phone }}</span>
              </div>
              <div class="contact-line email">
                <el-icon :size="13"><Message /></el-icon>
                <span>{{ row.email }}</span>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column
          label="会员等级"
          align="center"
          key="memberLevel"
          v-if="businessTable.isColumnVisible('memberLevel')"
          :width="businessTable.columnWidth('memberLevel', 130)"
          prop="memberLevel"
        >
          <template #default="{ row }">
            <el-tag :type="getLevelTagType(row.memberLevel)" effect="light" class="level-badge">
              {{ getLevelName(row.memberLevel) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column
          label="账户资产"
          min-width="150"
          key="assets"
          v-if="businessTable.isColumnVisible('assets')"
          :width="businessTable.columnWidth('assets', undefined)"
          prop="assets"
        >
          <template #default="{ row }">
            <div class="asset-cell">
              <div class="asset-row">
                <span class="asset-label">积分:</span>
                <span class="asset-points">{{ row.points.toLocaleString() }} pt</span>
              </div>
              <div class="asset-row">
                <span class="asset-label">余额:</span>
                <span class="asset-balance">¥{{ row.balance.toFixed(2) }}</span>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column
          label="实名认证"
          align="center"
          key="verifyStatus"
          v-if="businessTable.isColumnVisible('verifyStatus')"
          :width="businessTable.columnWidth('verifyStatus', 120)"
          prop="verifyStatus"
        >
          <template #default="{ row }">
            <el-tag v-if="row.verifyStatus === 1" type="success" size="small" effect="plain">
              <el-icon><Select /></el-icon>
              已实名
            </el-tag>
            <el-tag v-else-if="row.verifyStatus === 2" type="warning" size="small" effect="plain">
              <el-icon><Clock /></el-icon>
              审核中
            </el-tag>
            <el-tag v-else type="info" size="small" effect="plain">未实名</el-tag>
          </template>
        </el-table-column>

        <el-table-column
          label="注册渠道"
          align="center"
          key="channel"
          v-if="businessTable.isColumnVisible('channel')"
          :width="businessTable.columnWidth('channel', 120)"
          prop="channel"
        >
          <template #default="{ row }">
            <span class="channel-badge">{{ getChannelName(row.channel) }}</span>
          </template>
        </el-table-column>

        <el-table-column
          label="账号状态"
          align="center"
          key="status"
          v-if="businessTable.isColumnVisible('status')"
          :width="businessTable.columnWidth('status', 100)"
          prop="status"
        >
          <template #default="{ row }">
            <el-switch
              v-model="row.status"
              :active-value="1"
              :inactive-value="0"
              active-color="#10b981"
              inactive-color="#ef4444"
              :before-change="() => beforeStatusChange(row)"
              @change="(val) => handleStatusChange(row, val)"
            />
          </template>
        </el-table-column>

        <el-table-column
          label="活跃时间"
          key="lastActiveTime"
          v-if="businessTable.isColumnVisible('lastActiveTime')"
          :width="businessTable.columnWidth('lastActiveTime', 165)"
          prop="lastActiveTime"
        >
          <template #default="{ row }">
            <div class="time-box">
              <span class="time-active">{{ row.lastActiveTime }}</span>
              <span class="time-register">注册: {{ row.registerTime.slice(0, 10) }}</span>
            </div>
          </template>
        </el-table-column>

        <!-- Operations Column (Streamlined to 3 clear actions, strictly in one horizontal row) -->
        <el-table-column label="操作" width="215" fixed="right" align="center">
          <template #default="{ row }">
            <div class="table-op-btns">
              <el-button
                link
                type="primary"
                size="small"
                :icon="View"
                @click="openProfileDrawer(row)"
              >
                画像
              </el-button>
              <el-button link type="primary" size="small" :icon="Edit" @click="openEditModal(row)">
                编辑
              </el-button>
              <el-popconfirm
                title="确定要删除该用户档案吗？此操作不可逆！"
                confirm-button-text="确认删除"
                cancel-button-text="取消"
                confirm-button-type="danger"
                @confirm="handleDeleteMemberRow(row)"
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

      <!-- Pagination -->
      <div class="business-pagination">
        <span class="page-total-text">
          已检索共
          <strong>{{ filteredMembers.length }}</strong>
          位平台注册用户
        </span>
        <el-pagination
          v-model:current-page="pagination.currentPage"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[5, 10, 20, 50]"
          :total="filteredMembers.length"
          layout="total, sizes, prev, pager, next"
        />
      </div>
    </el-card>

    <!-- User Full Profile Drawer -->
    <el-drawer
      class="business-overlay"
      v-model="drawerVisible"
      title="用户全景画像与行为轨迹"
      size="min(560px, 100vw)"
      destroy-on-close
    >
      <div v-if="currentMember" class="drawer-body">
        <!-- Top Profile Banner -->
        <div class="drawer-header-card">
          <el-avatar :size="56" :src="currentMember.avatar" />
          <div class="drawer-header-meta">
            <div class="title-with-tag">
              <span class="drawer-nickname">{{ currentMember.nickname }}</span>
              <el-tag :type="getLevelTagType(currentMember.memberLevel)" size="small">
                {{ getLevelName(currentMember.memberLevel) }}
              </el-tag>
            </div>
            <span class="drawer-sub">
              UID: {{ currentMember.id }} · 姓名: {{ currentMember.realName }}
            </span>
            <div class="drawer-tags-wrap">
              <el-tag
                v-for="t in currentMember.tags"
                :key="t"
                size="small"
                effect="plain"
                class="user-tag"
              >
                # {{ t }}
              </el-tag>
            </div>
          </div>
        </div>

        <el-divider content-position="left">账户资产与权益</el-divider>
        <el-row :gutter="12" class="asset-cards-row">
          <el-col :xs="24" :sm="12">
            <div class="drawer-asset-box">
              <span class="box-label">可用积分点数</span>
              <span class="box-val text-primary">{{ currentMember.points.toLocaleString() }}</span>
              <span class="box-desc">支持兑换平台API配额</span>
            </div>
          </el-col>
          <el-col :xs="24" :sm="12">
            <div class="drawer-asset-box">
              <span class="box-label">现金账户余额</span>
              <span class="box-val text-success">¥{{ currentMember.balance.toFixed(2) }}</span>
              <span class="box-desc">支持在线订单原路扣除</span>
            </div>
          </el-col>
        </el-row>

        <el-divider content-position="left">实名与合规档案</el-divider>
        <el-descriptions :column="1" border size="small">
          <el-descriptions-item label="实名认证状态">
            <el-tag v-if="currentMember.verifyStatus === 1" type="success" size="small">
              已认证 (公安权威库核验一致)
            </el-tag>
            <el-tag v-else-if="currentMember.verifyStatus === 2" type="warning" size="small">
              人工审核中
            </el-tag>
            <el-tag v-else type="info" size="small">未实名认证</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="真实姓名">{{ currentMember.realName }}</el-descriptions-item>
          <el-descriptions-item label="身份证件号">
            {{ currentMember.idCard || '未登记实名身份证件' }}
          </el-descriptions-item>
          <el-descriptions-item label="绑定手机">{{ currentMember.phone }}</el-descriptions-item>
          <el-descriptions-item label="电子邮箱">{{ currentMember.email }}</el-descriptions-item>
          <el-descriptions-item label="注册来源">
            {{ getChannelName(currentMember.channel) }}
          </el-descriptions-item>
          <el-descriptions-item label="累计登录次数">
            {{ currentMember.loginCount || 1 }} 次
          </el-descriptions-item>
          <el-descriptions-item label="首次注册时间">
            {{ currentMember.registerTime }}
          </el-descriptions-item>
          <el-descriptions-item label="最后活跃时间">
            {{ currentMember.lastActiveTime }}
          </el-descriptions-item>
        </el-descriptions>

        <el-divider content-position="left">运营备注与风控信息</el-divider>
        <div class="remark-box">
          <p class="remark-text">{{ currentMember.remark || '暂无运营审计备注记录。' }}</p>
        </div>

        <div class="drawer-footer-actions">
          <el-button type="primary" :icon="Edit" @click="openEditModal(currentMember)">
            编辑用户资料
          </el-button>
          <el-button :icon="Coin" @click="openAdjustPointsModal(currentMember)">调整资产</el-button>
        </div>
      </div>
    </el-drawer>

    <!-- Create / Edit Member Dialog -->
    <el-dialog
      :before-close="formDraft.beforeClose"
      :close-on-click-modal="false"
      class="business-overlay"
      v-model="memberDialogVisible"
      :title="isEditMode ? '编辑平台注册用户' : '新增注册用户'"
      width="min(600px, 94vw)"
      destroy-on-close
    >
      <el-form
        ref="memberFormRef"
        :model="memberFormData"
        :rules="memberFormRules"
        label-width="100px"
        style="padding: 10px 10px 0"
      >
        <el-row :gutter="16">
          <el-col :xs="24" :sm="12">
            <el-form-item label="用户昵称" prop="nickname">
              <el-input v-model="memberFormData.nickname" placeholder="展示昵称" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item label="真实姓名" prop="realName">
              <el-input v-model="memberFormData.realName" placeholder="实名姓名" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :xs="24" :sm="12">
            <el-form-item label="手机号码" prop="phone">
              <el-input v-model="memberFormData.phone" placeholder="11位手机号" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item label="电子邮箱" prop="email">
              <el-input v-model="memberFormData.email" placeholder="常用电子邮箱" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :xs="24" :sm="12">
            <el-form-item label="会员等级" prop="memberLevel">
              <el-select v-model="memberFormData.memberLevel" style="width: 100%">
                <el-option label="普通会员" value="regular" />
                <el-option label="白银会员" value="silver" />
                <el-option label="黄金VIP" value="gold" />
                <el-option label="钻石企业客户" value="diamond" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item label="注册渠道" prop="channel">
              <el-select v-model="memberFormData.channel" style="width: 100%">
                <el-option label="Web 官方网站" value="web" />
                <el-option label="微信小程序" value="wechat" />
                <el-option label="移动端 App" value="app" />
                <el-option label="开放平台 API" value="open_api" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :xs="24" :sm="12">
            <el-form-item label="实名认证" prop="verifyStatus">
              <el-select v-model="memberFormData.verifyStatus" style="width: 100%">
                <el-option label="已实名认证" :value="1" />
                <el-option label="实名审核中" :value="2" />
                <el-option label="未实名" :value="0" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item label="账号状态" prop="status">
              <el-select v-model="memberFormData.status" style="width: 100%">
                <el-option label="正常正常" :value="1" />
                <el-option label="冻结受限" :value="0" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :xs="24" :sm="12">
            <el-form-item label="积分点数">
              <el-input-number
                v-model="memberFormData.points"
                :min="0"
                :step="100"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item label="现金余额">
              <el-input-number
                v-model="memberFormData.balance"
                :precision="2"
                :min="0"
                :step="50"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="登录凭证" v-if="isEditMode">
          <div style="display: flex; gap: 8px; width: 100%">
            <el-input
              v-model="memberFormData.newPassword"
              placeholder="留空则保持原密码不变"
              type="password"
              show-password
            />
            <el-button type="warning" plain :icon="Key" @click="handleResetMemberPwdInModal">
              设为默认
            </el-button>
          </div>
        </el-form-item>

        <el-form-item label="身份证件号">
          <el-input v-model="memberFormData.idCard" placeholder="实名认证二代身份证件" />
        </el-form-item>

        <el-form-item label="运营审计备注">
          <el-input
            v-model="memberFormData.remark"
            type="textarea"
            :rows="2"
            placeholder="填写用户业务备注或合规备忘"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="formDraft.close">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSaveMember">
          确认保存
        </el-button>
      </template>
    </el-dialog>

    <!-- Adjust Points / Balance Dialog -->
    <el-dialog
      class="business-overlay"
      v-model="adjustDialogVisible"
      title="账户资产与积分手动调账"
      width="min(480px, 94vw)"
    >
      <div v-if="targetAdjustMember" style="padding: 10px 10px 0">
        <p style="margin-bottom: 16px; font-size: 13.5px; color: var(--text-regular)">
          操作对象:
          <strong>{{ targetAdjustMember.nickname }} ({{ targetAdjustMember.id }})</strong>
        </p>

        <el-form label-width="90px">
          <el-form-item label="调整项目">
            <el-radio-group v-model="adjustType">
              <el-radio value="points">积分点数</el-radio>
              <el-radio value="balance">现金余额 (元)</el-radio>
            </el-radio-group>
          </el-form-item>

          <el-form-item label="变动增减">
            <el-radio-group v-model="adjustDirection">
              <el-radio :value="1">增加 (+)</el-radio>
              <el-radio :value="-1">扣除 (-)</el-radio>
            </el-radio-group>
          </el-form-item>

          <el-form-item label="变更数额">
            <el-input-number v-model="adjustAmount" :min="1" :max="100000" style="width: 100%" />
          </el-form-item>

          <el-form-item label="调账说明">
            <el-input v-model="adjustReason" placeholder="如: 运营活动赠送 / 售后补偿 / 纠错扣减" />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="adjustDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmAdjust">确认调账</el-button>
      </template>
    </el-dialog>

    <!-- Batch Adjust Level Modal -->
    <el-dialog
      class="business-overlay"
      v-model="batchLevelVisible"
      title="批量调整会员等级"
      width="min(480px, 94vw)"
    >
      <div style="padding: 12px 10px 0">
        <p style="font-size: 13.5px; margin-bottom: 14px; color: var(--text-regular)">
          即将调整已选中的
          <strong>{{ selectedRows.length }}</strong>
          位用户的会员等级:
        </p>
        <el-select v-model="batchTargetLevel" style="width: 100%">
          <el-option label="普通会员" value="regular" />
          <el-option label="白银会员" value="silver" />
          <el-option label="黄金VIP" value="gold" />
          <el-option label="钻石企业客户" value="diamond" />
        </el-select>
      </div>
      <template #footer>
        <el-button @click="batchLevelVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmBatchLevel">确认批量更新</el-button>
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
  View,
  Edit,
  ArrowDown,
  ArrowUp,
  DataAnalysis,
  User,
  Opportunity,
  Medal,
  Warning,
  TopRight,
  Iphone,
  Message,
  Select,
  Clock,
  Coin,
  Key,
  Lock,
  Operation,
  InfoFilled,
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { getStoredMembers, saveStoredMembers, addAuditLog } from '@/utils/mockData'

const userStore = useUserStore()

// State
const tableRef = ref()
const tableLoading = ref(false)
const allMembers = ref([])
const selectedRows = ref([])
const showStats = ref(true)
const showMoreFilter = ref(false)

const clearSelection = () => {
  tableRef.value?.clearSelection()
  selectedRows.value = []
}

// KPI Counters
const totalUserCount = computed(() => 128490 + allMembers.value.length)
const frozenUserCount = computed(() => allMembers.value.filter((m) => m.status === 0).length + 35)

// Query Form
const queryForm = reactive({
  keyword: '',
  level: '',
  verifyStatus: '',
  channel: '',
  status: '',
})

// Pagination
const pagination = reactive({
  currentPage: 1,
  pageSize: 10,
})

// Filtered List
const filteredMembers = computed(() => {
  return allMembers.value.filter((m) => {
    if (queryForm.keyword) {
      const kw = queryForm.keyword.toLowerCase().trim()
      const matchUid = m.id.toLowerCase().includes(kw)
      const matchNick = m.nickname.toLowerCase().includes(kw)
      const matchReal = m.realName.toLowerCase().includes(kw)
      const matchPhone = m.phone.includes(kw)
      if (!matchUid && !matchNick && !matchReal && !matchPhone) return false
    }
    if (queryForm.level && m.memberLevel !== queryForm.level) {
      return false
    }
    if (queryForm.verifyStatus !== '' && m.verifyStatus !== queryForm.verifyStatus) {
      return false
    }
    if (queryForm.channel && m.channel !== queryForm.channel) {
      return false
    }
    if (queryForm.status !== '' && m.status !== queryForm.status) {
      return false
    }
    return true
  })
})

const paginatedMembers = computed(() => {
  const start = (pagination.currentPage - 1) * pagination.pageSize
  return filteredMembers.value.slice(start, start + pagination.pageSize)
})

// Helpers
const getLevelName = (lvl) => {
  const map = {
    regular: '普通会员',
    silver: '白银会员',
    gold: '黄金VIP',
    diamond: '钻石客户',
  }
  return map[lvl] || lvl
}

const getLevelTagType = (lvl) => {
  const map = {
    regular: 'info',
    silver: 'primary',
    gold: 'warning',
    diamond: 'danger',
  }
  return map[lvl] !== undefined ? map[lvl] : 'info'
}

const getChannelName = (ch) => {
  const map = {
    web: '官方网站',
    wechat: '微信小程序',
    app: '手机 App',
    open_api: '开放平台 API',
  }
  return map[ch] || ch
}

// Data loader
const loadMembersData = () => {
  tableLoading.value = true
  setTimeout(() => {
    allMembers.value = getStoredMembers()
    tableLoading.value = false
  }, 250)
}

const handleSearch = () => {
  pagination.currentPage = 1
}

const handleReset = () => {
  queryForm.keyword = ''
  queryForm.level = ''
  queryForm.verifyStatus = ''
  queryForm.channel = ''
  queryForm.status = ''
  pagination.currentPage = 1
}

const handleSelectionChange = (rows) => {
  selectedRows.value = rows
}

// Status Switch
const beforeStatusChange = (row) => {
  const target = row.status === 1 ? '冻结限制' : '解除冻结'
  return new Promise((resolve) => {
    ElMessageBox.confirm(
      `确定要对用户【${row.nickname}】执行【${target}】操作吗？`,
      '用户状态变更确认',
      { confirmButtonText: '确定变更', cancelButtonText: '取消', type: 'warning' },
    )
      .then(() => resolve(true))
      .catch(() => resolve(false))
  })
}

const handleStatusChange = (row, newVal) => {
  saveStoredMembers(allMembers.value)
  ElMessage.success(
    `用户【${row.nickname}】账号状态已变更为【${newVal === 1 ? '正常使用' : '冻结受限'}】`,
  )
  addAuditLog({
    operator: userStore.currentUsername,
    action: '用户状态变更',
    target: row.id,
    detail: `将用户 ${row.nickname} 状态变更为 ${newVal === 1 ? '正常' : '冻结'}`,
    status: 'success',
    ip: '192.168.1.108',
  })
}

// Profile Drawer
const drawerVisible = ref(false)
const currentMember = ref(null)

const openProfileDrawer = (row) => {
  currentMember.value = row
  drawerVisible.value = true
}

// Dialog: Create & Edit
const memberDialogVisible = ref(false)
const isEditMode = ref(false)
const memberFormRef = ref(null)
const submitLoading = ref(false)

const memberFormData = reactive({
  id: '',
  username: '',
  nickname: '',
  realName: '',
  phone: '',
  email: '',
  memberLevel: 'regular',
  points: 100,
  balance: 0,
  newPassword: '',
  channel: 'web',
  verifyStatus: 1,
  status: 1,
  idCard: '',
  remark: '',
})

const memberFormRules = {
  nickname: [{ required: true, message: '请输入用户昵称', trigger: 'blur' }],
  phone: [{ required: true, message: '请输入联系手机', trigger: 'blur' }],
  email: [{ required: true, message: '请输入电子邮箱', trigger: 'blur' }],
}

const openCreateModal = () => {
  isEditMode.value = false
  const randNum = Math.floor(1000 + Math.random() * 9000)
  memberFormData.id = `UID-80${randNum}`
  memberFormData.username = `user_${randNum}`
  memberFormData.nickname = ''
  memberFormData.realName = ''
  memberFormData.phone = ''
  memberFormData.email = ''
  memberFormData.memberLevel = 'regular'
  memberFormData.points = 100
  memberFormData.balance = 0.0
  memberFormData.newPassword = ''
  memberFormData.channel = 'web'
  memberFormData.verifyStatus = 0
  memberFormData.status = 1
  memberFormData.idCard = ''
  memberFormData.remark = ''
  memberDialogVisible.value = true
}

const openEditModal = (row) => {
  isEditMode.value = true
  memberFormData.id = row.id
  memberFormData.username = row.username
  memberFormData.nickname = row.nickname
  memberFormData.realName = row.realName
  memberFormData.phone = row.phone
  memberFormData.email = row.email
  memberFormData.memberLevel = row.memberLevel
  memberFormData.points = row.points || 0
  memberFormData.balance = row.balance || 0
  memberFormData.newPassword = ''
  memberFormData.channel = row.channel
  memberFormData.verifyStatus = row.verifyStatus
  memberFormData.status = row.status
  memberFormData.idCard = row.idCard || ''
  memberFormData.remark = row.remark || ''
  memberDialogVisible.value = true
}

const handleResetMemberPwdInModal = () => {
  memberFormData.newPassword = 'UserPass@2026'
  ElMessage.info('已预填默认密码: UserPass@2026，确认保存后生效')
}

const handleDeleteMemberRow = (row) => {
  allMembers.value = allMembers.value.filter((m) => m.id !== row.id)
  saveStoredMembers(allMembers.value)
  ElMessage.success(`用户【${row.nickname}】档案已彻底移除`)
}

const handleSaveMember = () => {
  memberFormRef.value.validate((valid) => {
    if (valid) {
      submitLoading.value = true
      setTimeout(() => {
        if (isEditMode.value) {
          const idx = allMembers.value.findIndex((m) => m.id === memberFormData.id)
          if (idx > -1) {
            allMembers.value[idx] = {
              ...allMembers.value[idx],
              nickname: memberFormData.nickname,
              realName: memberFormData.realName,
              phone: memberFormData.phone,
              email: memberFormData.email,
              memberLevel: memberFormData.memberLevel,
              points: Number(memberFormData.points),
              balance: Number(memberFormData.balance),
              channel: memberFormData.channel,
              verifyStatus: memberFormData.verifyStatus,
              status: memberFormData.status,
              idCard: memberFormData.idCard,
              remark: memberFormData.remark,
            }
          }
          if (memberFormData.newPassword) {
            ElMessage.success(`用户资料已更新，密码已重置为: ${memberFormData.newPassword}`)
          } else {
            ElMessage.success('用户资料已更新')
          }
        } else {
          const newMem = {
            id: memberFormData.id,
            username: memberFormData.username,
            nickname: memberFormData.nickname,
            realName: memberFormData.realName,
            phone: memberFormData.phone,
            email: memberFormData.email,
            avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png',
            memberLevel: memberFormData.memberLevel,
            points: Number(memberFormData.points) || 100,
            balance: Number(memberFormData.balance) || 0.0,
            channel: memberFormData.channel,
            verifyStatus: memberFormData.verifyStatus,
            status: memberFormData.status,
            tags: ['新注册用户'],
            idCard: memberFormData.idCard,
            registerTime: new Date().toISOString().slice(0, 19).replace('T', ' '),
            lastActiveTime: '刚刚',
            loginCount: 1,
            remark: memberFormData.remark,
          }
          allMembers.value.unshift(newMem)
          ElMessage.success('新注册用户添加成功')
        }
        saveStoredMembers(allMembers.value)
        submitLoading.value = false
        memberDialogVisible.value = false
      }, 300)
    }
  })
}

// Adjust Points / Balance
const adjustDialogVisible = ref(false)
const targetAdjustMember = ref(null)
const adjustType = ref('points')
const adjustDirection = ref(1)
const adjustAmount = ref(100)
const adjustReason = ref('')

const openAdjustPointsModal = (row) => {
  targetAdjustMember.value = row
  adjustType.value = 'points'
  adjustDirection.value = 1
  adjustAmount.value = 500
  adjustReason.value = '平台运营活动权益赠送'
  adjustDialogVisible.value = true
}

const confirmAdjust = () => {
  if (!targetAdjustMember.value) return
  const mem = allMembers.value.find((m) => m.id === targetAdjustMember.value.id)
  if (!mem) return
  const delta = adjustAmount.value * adjustDirection.value
  if (adjustType.value === 'points') {
    mem.points = Math.max(0, mem.points + delta)
    ElMessage.success(`用户积分已更新，当前积分: ${mem.points} pt`)
  } else {
    mem.balance = Math.max(0, mem.balance + delta)
    ElMessage.success(`用户余额已更新，当前余额: ¥${mem.balance.toFixed(2)}`)
  }
  saveStoredMembers(allMembers.value)
  adjustDialogVisible.value = false
  addAuditLog({
    operator: userStore.currentUsername,
    action: '调整用户资产',
    target: mem.id,
    detail: `调账项目: ${adjustType.value === 'points' ? '积分' : '余额'}, 变动值: ${delta}, 原因: ${adjustReason.value}`,
    status: 'success',
    ip: '192.168.1.108',
  })
}

// Batch Level
const batchLevelVisible = ref(false)
const batchTargetLevel = ref('gold')

const openBatchLevelModal = () => {
  batchLevelVisible.value = true
}

const confirmBatchLevel = () => {
  const ids = selectedRows.value.map((r) => r.id)
  allMembers.value.forEach((m) => {
    if (ids.includes(m.id)) {
      m.memberLevel = batchTargetLevel.value
    }
  })
  saveStoredMembers(allMembers.value)
  ElMessage.success(
    `已批量更新 ${ids.length} 位用户的会员等级为【${getLevelName(batchTargetLevel.value)}】`,
  )
  batchLevelVisible.value = false
  selectedRows.value = []
}

// Batch Freeze
const handleBatchFreeze = () => {
  if (selectedRows.value.length === 0) return
  ElMessageBox.confirm(
    `确定要对选中的 ${selectedRows.value.length} 位用户进行安全冻结管控吗？`,
    '批量风控确认',
    { confirmButtonText: '执行冻结', cancelButtonText: '取消', type: 'error' },
  )
    .then(() => {
      const ids = selectedRows.value.map((r) => r.id)
      allMembers.value.forEach((m) => {
        if (ids.includes(m.id)) {
          m.status = 0
        }
      })
      saveStoredMembers(allMembers.value)
      ElMessage.success(`已对选中的 ${ids.length} 位用户执行冻结管控`)
      selectedRows.value = []
    })
    .catch(() => {})
}

// Dropdown Commands
const handleMoreCommand = (cmd, row) => {
  if (cmd === 'adjust_points') {
    openAdjustPointsModal(row)
  } else if (cmd === 'reset_pwd') {
    ElMessageBox.prompt(`请输入为用户【${row.nickname}】重置的新登录密码：`, '重置登录密码', {
      confirmButtonText: '确认重置',
      cancelButtonText: '取消',
      inputValue: 'UserPass@2026',
    })
      .then(({ value }) => {
        ElMessage.success(`用户【${row.nickname}】的密码已重置为: ${value}`)
      })
      .catch(() => {})
  } else if (cmd === 'delete_user') {
    ElMessageBox.confirm(
      `确定要删除用户【${row.nickname}】的所有注册档案吗？此操作不可逆！`,
      '删除警告',
      { confirmButtonText: '确定删除', cancelButtonText: '取消', type: 'error' },
    )
      .then(() => {
        allMembers.value = allMembers.value.filter((m) => m.id !== row.id)
        saveStoredMembers(allMembers.value)
        ElMessage.success('用户已成功删除')
      })
      .catch(() => {})
  }
}

// Export CSV
const handleExportMembers = () => {
  const headers = [
    'UID',
    '登录账号',
    '用户昵称',
    '真实姓名',
    '手机号码',
    '电子邮箱',
    '会员等级',
    '积分',
    '余额',
    '实名状态',
    '渠道',
    '状态',
    '注册时间',
  ]
  const rows = filteredMembers.value.map((m) => [
    m.id,
    m.username,
    m.nickname,
    m.realName,
    m.phone,
    m.email,
    getLevelName(m.memberLevel),
    m.points,
    m.balance,
    m.verifyStatus === 1 ? '已实名' : m.verifyStatus === 2 ? '审核中' : '未实名',
    getChannelName(m.channel),
    m.status === 1 ? '正常' : '冻结',
    m.registerTime,
  ])

  const csvContent =
    'data:text/csv;charset=utf-8,\uFEFF' +
    [headers.join(','), ...rows.map((e) => e.join(','))].join('\n')
  const encodedUri = encodeURI(csvContent)
  const link = document.createElement('a')
  link.setAttribute('href', encodedUri)
  link.setAttribute('download', `全平台用户清单_${new Date().toISOString().slice(0, 10)}.csv`)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  ElMessage.success('平台用户清单导出成功并已开始下载')
}

onMounted(() => {
  loadMembersData()
})

const businessTable = useBusinessTable(
  'members',
  [
    { prop: 'id', label: '用户 UID' },
    { prop: 'profile', label: '用户画像' },
    { prop: 'contact', label: '联系方式' },
    { prop: 'memberLevel', label: '会员等级' },
    { prop: 'assets', label: '账户资产' },
    { prop: 'verifyStatus', label: '实名认证' },
    { prop: 'channel', label: '注册渠道' },
    { prop: 'status', label: '账号状态' },
    { prop: 'lastActiveTime', label: '活跃时间' },
  ],
  {
    query: queryForm,
    pagination,
    clearSelection,
    showStats,
    showMoreFilter,
    loading: tableLoading,
    total: () => filteredMembers.value.length,
    pageSizes: [10, 20, 50, 100],
  },
)
const formDraft = useBusinessDraft(memberDialogVisible, memberFormData, submitLoading)
</script>

<style scoped>
.stats-collapse-wrap {
  width: 100%;
}

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

.uid-tag {
  font-family: monospace;
  font-weight: 600;
  color: var(--text-regular);
  font-size: 12.5px;
}

.user-profile-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.profile-info {
  display: flex;
  flex-direction: column;
}

.nickname-row {
  display: flex;
  align-items: center;
  gap: 6px;
}

.user-nickname {
  font-weight: 600;
  font-size: 14px;
  color: var(--text-main);
}

.mini-level-tag {
  font-size: 10px;
  padding: 0 4px;
  height: 18px;
  line-height: 16px;
  border-radius: 4px;
}

.realname-sub {
  font-size: 12px;
  color: var(--text-muted);
}

.contact-box {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.contact-line {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12.5px;
  color: var(--text-regular);
}

.contact-line.email {
  color: var(--text-muted);
}

.level-badge {
  font-weight: 500;
  border-radius: 6px;
}

.asset-cell {
  display: flex;
  flex-direction: column;
  gap: 2px;
  font-size: 12.5px;
}

.asset-row {
  display: flex;
  align-items: center;
  gap: 4px;
}

.asset-label {
  color: var(--text-muted);
}

.asset-points {
  font-weight: 600;
  color: var(--accent-foreground, var(--primary-color));
}

.asset-balance {
  font-weight: 600;
  color: #10b981;
}

.channel-badge {
  font-size: 12px;
  color: var(--text-muted);
}

.time-box {
  display: flex;
  flex-direction: column;
  font-size: 12px;
}

.time-active {
  color: var(--text-regular);
}

.time-register {
  color: var(--text-muted);
}

.page-total-text {
  font-size: 13px;
  color: var(--text-muted);
}

/* Drawer Styles */
.drawer-body {
  padding: 4px 10px;
}

.drawer-header-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background-color: var(--bg-color);
  border-radius: var(--radius-lg, 12px);
  margin-bottom: 12px;
}

.drawer-header-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.title-with-tag {
  display: flex;
  align-items: center;
  gap: 8px;
}

.drawer-nickname {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-main);
}

.drawer-sub {
  font-size: 12.5px;
  color: var(--text-muted);
}

.drawer-tags-wrap {
  display: flex;
  gap: 6px;
  margin-top: 4px;
}

.user-tag {
  border-radius: 4px;
  font-size: 11px;
}

.asset-cards-row {
  margin-bottom: 16px;
}

.drawer-asset-box {
  padding: 12px;
  border-radius: var(--radius-md, 10px);
  background-color: var(--bg-color);
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.box-label {
  font-size: 12px;
  color: var(--text-muted);
}

.box-val {
  font-size: 20px;
  font-weight: 700;
}

.box-desc {
  font-size: 11px;
  color: var(--text-muted);
}

.text-primary {
  color: var(--accent-foreground, var(--primary-color));
}

.text-success {
  color: #10b981;
}

.remark-box {
  padding: 12px;
  border-radius: var(--radius-md, 10px);
  background-color: var(--bg-color);
  margin-bottom: 24px;
}

.remark-text {
  font-size: 13px;
  color: var(--text-regular);
  line-height: 1.6;
  margin: 0;
}

.drawer-footer-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
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
