<template>
  <div class="page-container">
    <!-- Filter Bar -->
    <el-card shadow="never" class="search-form-card">
      <el-form :inline="true" :model="queryForm" class="filter-form">
        <el-form-item label="权限名称">
          <el-input
            v-model="queryForm.roleName"
            placeholder="支持模糊匹配"
            clearable
            @keyup.enter="handleSearch"
          />
        </el-form-item>

        <el-form-item label="权限标识">
          <el-input
            v-model="queryForm.roleKey"
            placeholder="如: super_admin"
            clearable
            @keyup.enter="handleSearch"
          />
        </el-form-item>

        <el-form-item label="状态">
          <el-select v-model="queryForm.status" placeholder="全部状态" clearable style="width: 130px;">
            <el-option label="正常" :value="1" />
            <el-option label="停用" :value="0" />
          </el-select>
        </el-form-item>

        <el-form-item class="form-btn-item">
          <el-button type="primary" :icon="Search" @click="handleSearch">查询</el-button>
          <el-button :icon="Refresh" @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- Table Card -->
    <el-card shadow="never" class="table-card">
      <div class="action-bar">
        <div class="left-actions">
          <el-button type="primary" :icon="Plus" @click="openCreateModal">
            新增账号权限
          </el-button>
          <el-button
            type="danger"
            plain
            :icon="Delete"
            :disabled="selectedRows.length === 0"
            @click="handleBatchDelete"
          >
            批量删除 {{ selectedRows.length > 0 ? `(${selectedRows.length})` : '' }}
          </el-button>
        </div>

        <div class="right-actions">
          <el-tooltip content="刷新数据" placement="top">
            <el-button circle :icon="RefreshRight" @click="loadRolesData" />
          </el-tooltip>
        </div>
      </div>

      <!-- Batch Toolbar Row -->
      <transition name="el-fade-in-linear">
        <div v-if="selectedRows.length > 0" class="batch-alert-bar">
          <div class="batch-alert-left">
            <el-icon color="#3b82f6" :size="16"><InfoFilled /></el-icon>
            <span>已勾选 <strong>{{ selectedRows.length }}</strong> 项权限规则</span>
          </div>
          <div class="batch-alert-right">
            <el-button
              type="danger"
              size="small"
              plain
              :icon="Delete"
              @click="handleBatchDelete"
            >
              批量删除
            </el-button>
            <el-button size="small" @click="clearSelection">清空已选</el-button>
          </div>
        </div>
      </transition>

      <el-table
        ref="tableRef"
        v-loading="tableLoading"
        :data="filteredRoles"
        row-key="id"
        stripe
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="50" align="center" />
        <el-table-column prop="id" label="权限编号" width="90" align="center" />

        <el-table-column label="权限名称" min-width="160">
          <template #default="{ row }">
            <div class="role-cell">
              <el-icon color="#2563eb" style="margin-right: 6px;"><Stamp /></el-icon>
              <strong>{{ row.roleName }}</strong>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="roleKey" label="权限标识" width="160">
          <template #default="{ row }">
            <el-tag size="small" type="primary" effect="plain" class="mono">{{ row.roleKey }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="description" label="权限职责说明" min-width="200" show-overflow-tooltip />

        <el-table-column label="数据范围" width="150">
          <template #default="{ row }">
            <el-tag size="small" :type="getDataScopeTagType(row.dataScope)">
              {{ getDataScopeLabel(row.dataScope) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="orderNum" label="显示顺序" width="90" align="center" />

        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-switch
              v-model="row.status"
              :active-value="1"
              :inactive-value="0"
              @change="(val) => handleStatusChange(row, val)"
            />
          </template>
        </el-table-column>

        <el-table-column prop="createTime" label="创建时间" width="170" />

        <!-- Operations Column (Streamlined to 3 clear actions, strictly in one horizontal row) -->
        <el-table-column label="操作" width="215" fixed="right" align="center">
          <template #default="{ row }">
            <div class="table-op-btns">
              <el-button link type="primary" size="small" :icon="Menu" @click="openPermissionDrawer(row)">
                授权
              </el-button>
              <el-button link type="primary" size="small" :icon="Edit" @click="openEditModal(row)">
                编辑
              </el-button>
              <el-popconfirm
                title="确定要删除该权限项吗？"
                confirm-button-text="确认"
                cancel-button-text="取消"
                confirm-button-type="danger"
                @confirm="handleDeleteRole(row)"
              >
                <template #reference>
                  <el-button link type="danger" size="small" :icon="Delete">
                    删除
                  </el-button>
                </template>
              </el-popconfirm>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Create / Edit Role Dialog -->
    <el-dialog
      v-model="roleDialogVisible"
      :title="isEditMode ? '编辑账号权限' : '新增账号权限'"
      width="520px"
      destroy-on-close
    >
      <el-form
        ref="roleFormRef"
        :model="roleFormData"
        :rules="roleFormRules"
        label-width="95px"
        style="padding: 10px 10px 0;"
      >
        <el-form-item label="权限名称" prop="roleName">
          <el-input v-model="roleFormData.roleName" placeholder="例如: 运营总监 / 财务审计" />
        </el-form-item>

        <el-form-item label="权限标识" prop="roleKey">
          <el-input v-model="roleFormData.roleKey" placeholder="例如: operation_director" />
        </el-form-item>

        <el-form-item label="数据权限" prop="dataScope">
          <el-select v-model="roleFormData.dataScope" placeholder="选择数据可见范围" style="width: 100%;">
            <el-option label="全部数据权限 (跨部门全域可见)" value="ALL" />
            <el-option label="本部门及以下数据权限 (含下属机构)" value="DEPT_AND_CHILD" />
            <el-option label="仅本部门数据权限 (本级不可穿透)" value="DEPT_ONLY" />
            <el-option label="仅本人数据权限 (个人独立范围)" value="SELF" />
          </el-select>
        </el-form-item>

        <el-form-item label="显示顺序" prop="orderNum">
          <el-input-number v-model="roleFormData.orderNum" :min="1" :max="99" style="width: 100%;" />
        </el-form-item>

        <el-form-item label="启用状态">
          <el-radio-group v-model="roleFormData.status">
            <el-radio :value="1">正常启用</el-radio>
            <el-radio :value="0">停用禁用</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="职责说明">
          <el-input
            v-model="roleFormData.description"
            type="textarea"
            :rows="3"
            placeholder="说明该权限身份的业务定位与职责边界"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="roleDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="submitRoleForm">
          保存权限
        </el-button>
      </template>
    </el-dialog>

    <!-- Permission Tree Drawer -->
    <el-drawer
      v-model="permDrawerVisible"
      :title="`分配菜单与操作权限 - 【${activeRole?.roleName}】`"
      size="440px"
      destroy-on-close
    >
      <div class="perm-drawer-content">
        <div class="perm-tip-box">
          <el-icon color="#2563eb"><InfoFilled /></el-icon>
          <span>勾选该角色可访问的左侧菜单、功能页面及按钮级操作权限</span>
        </div>

        <div class="tree-tools">
          <el-button size="small" @click="toggleSelectAllPerms">
            {{ isAllPermsSelected ? '取消全选' : '全部全选' }}
          </el-button>
        </div>

        <el-scrollbar class="tree-scrollbar">
          <el-tree
            ref="permTreeRef"
            :data="permissionTreeData"
            show-checkbox
            node-key="id"
            default-expand-all
            :props="{ label: 'label', children: 'children' }"
          />
        </el-scrollbar>

        <div class="drawer-bottom-actions">
          <el-button @click="permDrawerVisible = false">取消</el-button>
          <el-button type="primary" :loading="savePermLoading" @click="saveRolePermissions">
            确认应用授权
          </el-button>
        </div>
      </div>
    </el-drawer>

    <!-- Data Scope Dialog -->
    <el-dialog
      v-model="scopeDialogVisible"
      :title="`配置数据权限范围 - 【${activeRole?.roleName}】`"
      width="460px"
    >
      <div class="scope-body">
        <p class="scope-desc">设定该角色登录系统时，对业务数据和资产台账的可见范围：</p>
        <el-radio-group v-model="tempDataScope" class="scope-radios">
          <el-radio value="ALL">
            <div class="scope-item">
              <span class="scope-title">全部数据权限</span>
              <span class="scope-sub">可跨部门查看和操作全公司所有业务数据</span>
            </div>
          </el-radio>
          <el-radio value="DEPT_AND_CHILD">
            <div class="scope-item">
              <span class="scope-title">本部门及以下数据权限</span>
              <span class="scope-sub">仅可查看本部门以及所有下属子部门的数据</span>
            </div>
          </el-radio>
          <el-radio value="DEPT_ONLY">
            <div class="scope-item">
              <span class="scope-title">仅本部门数据权限</span>
              <span class="scope-sub">严格限定在本部门内部，不可穿透子部门</span>
            </div>
          </el-radio>
          <el-radio value="SELF">
            <div class="scope-item">
              <span class="scope-title">仅本人数据权限</span>
              <span class="scope-sub">只能查看并维护自己创建或负责的数据项</span>
            </div>
          </el-radio>
        </el-radio-group>
      </div>
      <template #footer>
        <el-button @click="scopeDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveDataScope">保存设置</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search,
  Refresh,
  Plus,
  Delete,
  RefreshRight,
  Stamp,
  Edit,
  Menu,
  FolderChecked,
  InfoFilled,
  Operation
} from '@element-plus/icons-vue'
import {
  getStoredRoles,
  saveStoredRoles,
  addAuditLog
} from '@/utils/mockData'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

const tableRef = ref()
const allRoles = ref([])
const tableLoading = ref(false)
const selectedRows = ref([])

const clearSelection = () => {
  tableRef.value?.clearSelection()
  selectedRows.value = []
}

const queryForm = reactive({
  roleName: '',
  roleKey: '',
  status: ''
})

const loadRolesData = () => {
  tableLoading.value = true
  setTimeout(() => {
    allRoles.value = getStoredRoles()
    tableLoading.value = false
  }, 150)
}

onMounted(() => {
  loadRolesData()
})

const filteredRoles = computed(() => {
  return allRoles.value.filter((r) => {
    const matchName = !queryForm.roleName || r.roleName.toLowerCase().includes(queryForm.roleName.toLowerCase().trim())
    const matchKey = !queryForm.roleKey || r.roleKey.toLowerCase().includes(queryForm.roleKey.toLowerCase().trim())
    const matchStatus = queryForm.status === '' || r.status === queryForm.status
    return matchName && matchKey && matchStatus
  })
})

const handleSearch = () => {}
const handleReset = () => {
  queryForm.roleName = ''
  queryForm.roleKey = ''
  queryForm.status = ''
}

const handleSelectionChange = (selection) => {
  selectedRows.value = selection
}

const getDataScopeLabel = (scope) => {
  const map = {
    ALL: '全部数据权限',
    DEPT_AND_CHILD: '本部门及子部门',
    DEPT_ONLY: '仅本部门',
    SELF: '仅本人数据'
  }
  return map[scope] || '自定义'
}

const getDataScopeTagType = (scope) => {
  const map = {
    ALL: 'danger',
    DEPT_AND_CHILD: 'primary',
    DEPT_ONLY: 'success',
    SELF: 'info'
  }
  return map[scope] || 'info'
}

const handleStatusChange = (row, val) => {
  saveStoredRoles(allRoles.value)
  ElMessage.success(`角色【${row.roleName}】状态已变更为【${val === 1 ? '正常' : '停用'}】`)
  addAuditLog({
    operator: userStore.currentUsername,
    action: '更新角色状态',
    target: row.roleKey,
    detail: `状态: ${val === 1 ? '正常' : '停用'}`,
    status: 'success',
    ip: '192.168.1.108'
  })
}

// Create / Edit Role Modal
const roleDialogVisible = ref(false)
const isEditMode = ref(false)
const submitLoading = ref(false)
const roleFormRef = ref(null)

const roleFormData = reactive({
  id: 0,
  roleName: '',
  roleKey: '',
  orderNum: 1,
  status: 1,
  description: '',
  dataScope: 'DEPT_ONLY'
})

const roleFormRules = {
  roleName: [{ required: true, message: '请输入角色名称', trigger: 'blur' }],
  roleKey: [{ required: true, message: '请输入权限字符', trigger: 'blur' }]
}

const openCreateModal = () => {
  isEditMode.value = false
  roleFormData.id = Date.now()
  roleFormData.roleName = ''
  roleFormData.roleKey = ''
  roleFormData.orderNum = allRoles.value.length + 1
  roleFormData.status = 1
  roleFormData.description = ''
  roleFormData.dataScope = 'DEPT_ONLY'
  roleDialogVisible.value = true
}

const openEditModal = (row) => {
  isEditMode.value = true
  roleFormData.id = row.id
  roleFormData.roleName = row.roleName
  roleFormData.roleKey = row.roleKey
  roleFormData.orderNum = row.orderNum
  roleFormData.status = row.status
  roleFormData.description = row.description || ''
  roleFormData.dataScope = row.dataScope
  roleDialogVisible.value = true
}

const submitRoleForm = async () => {
  if (!roleFormRef.value) return
  await roleFormRef.value.validate((valid) => {
    if (valid) {
      submitLoading.value = true
      setTimeout(() => {
        if (isEditMode.value) {
          const idx = allRoles.value.findIndex((r) => r.id === roleFormData.id)
          if (idx > -1) {
            allRoles.value[idx] = {
              ...allRoles.value[idx],
              roleName: roleFormData.roleName,
              roleKey: roleFormData.roleKey,
              orderNum: roleFormData.orderNum,
              status: roleFormData.status,
              description: roleFormData.description,
              dataScope: roleFormData.dataScope
            }
          }
          ElMessage.success('账号权限信息已更新')
        } else {
          allRoles.value.push({
            id: roleFormData.id,
            roleName: roleFormData.roleName,
            roleKey: roleFormData.roleKey,
            orderNum: roleFormData.orderNum,
            status: roleFormData.status,
            description: roleFormData.description,
            dataScope: roleFormData.dataScope || 'DEPT_ONLY',
            createTime: new Date().toISOString().slice(0, 19).replace('T', ' '),
            permissionKeys: ['dashboard']
          })
          ElMessage.success('新账号权限配置成功创建')
        }

        saveStoredRoles(allRoles.value)
        addAuditLog({
          operator: userStore.currentUsername,
          action: isEditMode.value ? '修改角色' : '新增角色',
          target: roleFormData.roleName,
          detail: `权限标识: ${roleFormData.roleKey}`,
          status: 'success',
          ip: '192.168.1.108'
        })

        submitLoading.value = false
        roleDialogVisible.value = false
      }, 250)
    }
  })
}

// Delete role
const handleDeleteRole = (row) => {
  if (row.roleKey === 'super_admin') {
    ElMessage.warning('系统内置超级管理员角色禁止删除！')
    return
  }
  allRoles.value = allRoles.value.filter((r) => r.id !== row.id)
  saveStoredRoles(allRoles.value)
  ElMessage.success(`角色【${row.roleName}】已删除`)
}

const handleBatchDelete = () => {
  if (selectedRows.value.length === 0) return
  ElMessageBox.confirm(
    `确定要批量删除选中的 ${selectedRows.value.length} 个角色吗？`,
    '确认批量删除',
    { confirmButtonText: '删除', cancelButtonText: '取消', type: 'error' }
  ).then(() => {
    const ids = selectedRows.value.map((r) => r.id)
    allRoles.value = allRoles.value.filter((r) => !ids.includes(r.id) || r.roleKey === 'super_admin')
    saveStoredRoles(allRoles.value)
    ElMessage.success('批量删除完成')
    selectedRows.value = []
  }).catch(() => {})
}

// Permission Tree Drawer
const permDrawerVisible = ref(false)
const activeRole = ref(null)
const permTreeRef = ref(null)
const savePermLoading = ref(false)
const isAllPermsSelected = ref(false)

const permissionTreeData = [
  {
    id: 'dashboard',
    label: '控制台概览 (Dashboard)',
    children: [
      { id: 'dashboard:view', label: '查看监控指标与概览卡片' }
    ]
  },
  {
    id: 'system',
    label: '组织与权限体系',
    children: [
      {
        id: 'users',
        label: '用户管理模块',
        children: [
          { id: 'users:add', label: '新增中台用户' },
          { id: 'users:edit', label: '编辑资料与重置密码' },
          { id: 'users:delete', label: '删除与批量删除' },
          { id: 'users:export', label: '导出用户报表' }
        ]
      },
      {
        id: 'departments',
        label: '部门组织架构',
        children: [
          { id: 'dept:add', label: '新增部门' },
          { id: 'dept:edit', label: '修改部门' },
          { id: 'dept:delete', label: '删除部门' }
        ]
      },
      {
        id: 'roles',
        label: '角色与权限控制',
        children: [
          { id: 'role:add', label: '新增角色' },
          { id: 'role:edit', label: '修改角色' },
          { id: 'role:perm', label: '菜单与数据授权' }
        ]
      }
    ]
  },
  {
    id: 'devices',
    label: '资产与设备中心',
    children: [
      { id: 'devices:add', label: '注册新设备资产' },
      { id: 'devices:edit', label: '修改设备参数' },
      { id: 'devices:cmd', label: 'MQTT远程控制指令下发' },
      { id: 'devices:telemetry', label: '遥测实时数据流监听' },
      { id: 'devices:export', label: '导出设备台账' }
    ]
  },
  {
    id: 'ops',
    label: '系统与运维监控',
    children: [
      { id: 'dictionary', label: '数据字典维护与配置' },
      { id: 'monitor', label: '服务器与微服务健康监控' },
      { id: 'settings', label: '全局系统与MQTT网关设置' }
    ]
  }
]

const openPermissionDrawer = (row) => {
  activeRole.value = row
  permDrawerVisible.value = true
  nextTick(() => {
    if (permTreeRef.value) {
      permTreeRef.value.setCheckedKeys(row.permissionKeys || ['dashboard'])
    }
  })
}

const toggleSelectAllPerms = () => {
  isAllPermsSelected.value = !isAllPermsSelected.value
  if (isAllPermsSelected.value) {
    const allKeys = getAllTreeKeys(permissionTreeData)
    permTreeRef.value.setCheckedKeys(allKeys)
  } else {
    permTreeRef.value.setCheckedKeys([])
  }
}

const getAllTreeKeys = (nodes) => {
  let keys = []
  for (const n of nodes) {
    keys.push(n.id)
    if (n.children) {
      keys = keys.concat(getAllTreeKeys(n.children))
    }
  }
  return keys
}

const saveRolePermissions = () => {
  savePermLoading.value = true
  setTimeout(() => {
    savePermLoading.value = false
    const checked = permTreeRef.value.getCheckedKeys()
    const halfChecked = permTreeRef.value.getHalfCheckedKeys()
    const allChecked = [...checked, ...halfChecked]

    const idx = allRoles.value.findIndex((r) => r.id === activeRole.value.id)
    if (idx > -1) {
      allRoles.value[idx].permissionKeys = allChecked
      saveStoredRoles(allRoles.value)
    }

    ElMessage.success(`角色【${activeRole.value.roleName}】权限已成功应用`)
    permDrawerVisible.value = false
  }, 300)
}

// Data Scope Modal
const scopeDialogVisible = ref(false)
const tempDataScope = ref('ALL')

const openDataScopeModal = (row) => {
  activeRole.value = row
  tempDataScope.value = row.dataScope || 'DEPT_ONLY'
  scopeDialogVisible.value = true
}

const saveDataScope = () => {
  const idx = allRoles.value.findIndex((r) => r.id === activeRole.value.id)
  if (idx > -1) {
    allRoles.value[idx].dataScope = tempDataScope.value
    saveStoredRoles(allRoles.value)
    ElMessage.success('数据权限范围设置已更新')
  }
  scopeDialogVisible.value = false
}
</script>

<style scoped>
.filter-form {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 12px;
}

.role-cell {
  display: flex;
  align-items: center;
}

.mono {
  font-family: monospace;
}

.perm-drawer-content {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.perm-tip-box {
  background-color: rgba(37, 99, 235, 0.08);
  border: 1px solid rgba(37, 99, 235, 0.2);
  padding: 10px 12px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--primary-color);
  margin-bottom: 12px;
}

.tree-tools {
  margin-bottom: 8px;
  display: flex;
  justify-content: flex-end;
}

.tree-scrollbar {
  flex: 1;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  padding: 10px;
}

.drawer-bottom-actions {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.scope-body {
  padding: 4px;
}

.scope-desc {
  font-size: 13px;
  color: #475569;
  margin-bottom: 14px;
}

.scope-radios {
  display: flex;
  flex-direction: column;
  gap: 12px;
  width: 100%;
}

.scope-item {
  display: flex;
  flex-direction: column;
  margin-left: 8px;
}

.scope-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-main);
}

.scope-sub {
  font-size: 11px;
  color: #64748b;
  margin-top: 2px;
}

.batch-alert-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: var(--menu-hover-bg, rgba(59, 130, 246, 0.08));
  border: 1px dashed rgba(59, 130, 246, 0.35);
  border-radius: var(--radius-md, 8px);
  padding: 8px 14px;
  margin-bottom: 14px;
}

.batch-alert-left {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--text-regular);
}

.batch-alert-left strong {
  color: var(--primary-color, #3b82f6);
}

.batch-alert-right {
  display: flex;
  align-items: center;
  gap: 8px;
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
