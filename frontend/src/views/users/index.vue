<template>
  <div class="page-container">
    <!-- Top Filter & Search Bar -->
    <el-card shadow="never" class="search-form-card">
      <el-form :inline="true" :model="queryForm" class="filter-form">
        <el-form-item label="登录账号">
          <el-input
            v-model="queryForm.username"
            placeholder="支持模糊搜索"
            clearable
            @keyup.enter="handleSearch"
          />
        </el-form-item>

        <el-form-item label="真实姓名">
          <el-input
            v-model="queryForm.realName"
            placeholder="搜索姓名"
            clearable
            @keyup.enter="handleSearch"
          />
        </el-form-item>

        <el-form-item label="账号权限">
          <el-select v-model="queryForm.role" placeholder="全部权限" clearable style="width: 150px;">
            <el-option label="超级管理员" value="super_admin" />
            <el-option label="设备运维专家" value="device_admin" />
            <el-option label="嵌入式开发" value="developer" />
            <el-option label="安全审计员" value="auditor" />
            <el-option label="访客只读" value="guest" />
          </el-select>
        </el-form-item>

        <el-form-item label="账号状态">
          <el-select v-model="queryForm.status" placeholder="全部状态" clearable style="width: 120px;">
            <el-option label="已启用" :value="1" />
            <el-option label="已禁用" :value="0" />
          </el-select>
        </el-form-item>

        <el-form-item class="form-btn-item">
          <el-button type="primary" :icon="Search" @click="handleSearch">查询</el-button>
          <el-button :icon="Refresh" @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- Table Card with Action Buttons -->
    <el-card shadow="never" class="table-card">
      <div class="action-bar">
        <div class="left-actions">
          <el-button type="primary" :icon="Plus" @click="openCreateModal">
            新增账号
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
          <el-button :icon="Download" @click="handleExportUsers">
            批量导出
          </el-button>
        </div>

        <div class="right-actions">
          <el-tooltip content="刷新表格数据" placement="top">
            <el-button circle :icon="RefreshRight" @click="loadUserData" />
          </el-tooltip>
        </div>
      </div>

      <!-- Batch Toolbar Row (Revealed automatically when items are checked) -->
      <transition name="el-fade-in-linear">
        <div v-if="selectedRows.length > 0" class="batch-alert-bar">
          <div class="batch-alert-left">
            <el-icon color="#3b82f6" :size="16"><InfoFilled /></el-icon>
            <span>已勾选 <strong>{{ selectedRows.length }}</strong> 项系统账号</span>
          </div>
          <div class="batch-alert-right">
            <el-button
              type="danger"
              size="small"
              :icon="Delete"
              @click="handleBatchDelete"
            >
              批量删除
            </el-button>
            <el-button size="small" @click="clearSelection">清空已选</el-button>
          </div>
        </div>
      </transition>

      <!-- Main Users Table -->
      <el-table
        ref="tableRef"
        v-loading="tableLoading"
        :data="paginatedUsers"
        row-key="id"
        stripe
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="50" align="center" />

        <el-table-column prop="id" label="账号编号" width="110" />

        <el-table-column label="账号身份" min-width="170">
          <template #default="{ row }">
            <div class="user-cell">
              <el-avatar :size="34" :src="row.avatar" />
              <div class="user-info">
                <span class="user-realname">{{ row.realName }}</span>
                <span class="user-subname">@{{ row.username }}</span>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="账号权限" width="140">
          <template #default="{ row }">
            <el-tag :type="getRoleTagType(row.role)" effect="light" size="small" :disable-transitions="true">
              {{ row.roleName }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="department" label="所属部门" min-width="140" show-overflow-tooltip />

        <el-table-column prop="phone" label="联系电话" width="130" />

        <el-table-column prop="email" label="邮箱地址" min-width="170" show-overflow-tooltip />

        <el-table-column label="账号状态" width="100" align="center">
          <template #default="{ row }">
            <el-switch
              v-model="row.status"
              :active-value="1"
              :inactive-value="0"
              :before-change="() => beforeStatusChange(row)"
              @change="(val) => handleStatusChange(row, val)"
            />
          </template>
        </el-table-column>

        <el-table-column label="最后登录" width="170">
          <template #default="{ row }">
            <div class="time-cell">
              <span>{{ row.lastLoginTime || '-' }}</span>
              <span class="ip-sub">{{ row.lastLoginIp || '-' }}</span>
            </div>
          </template>
        </el-table-column>

        <!-- Operations Column (Streamlined to 3 clear actions, strictly in one horizontal row) -->
        <el-table-column label="操作" width="194" fixed="right" align="center">
          <template #default="{ row }">
            <div class="table-op-btns">
              <el-button link type="primary" size="small" :icon="Stamp" @click="openRoleModal(row)">
                权限
              </el-button>
              <el-button link type="primary" size="small" :icon="Edit" @click="openEditModal(row)">
                编辑
              </el-button>
              <el-popconfirm
                title="确定删除该用户吗？"
                confirm-button-text="删除"
                cancel-button-text="取消"
                confirm-button-type="danger"
                width="auto"
                @confirm="handleDeleteUser(row)"
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

      <!-- Pagination Footer -->
      <div class="pagination-footer">
        <span class="page-total-text">
          已筛选共 <strong>{{ filteredUsers.length }}</strong> 条数据
        </span>
        <el-pagination
          v-model:current-page="pagination.currentPage"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[5, 10, 20, 50]"
          :total="filteredUsers.length"
          layout="total, sizes, prev, pager, next, jumper"
          background
          small
        />
      </div>
    </el-card>

    <!-- Create / Edit User Dialog -->
    <el-dialog
      v-model="userDialogVisible"
      :title="isEditMode ? '编辑系统账号' : '新增系统账号'"
      width="560px"
      destroy-on-close
    >
      <el-form
        ref="userFormRef"
        :model="userFormData"
        :rules="userFormRules"
        label-width="95px"
        style="padding: 10px 10px 0;"
      >
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="登录账号" prop="username">
              <el-input
                v-model="userFormData.username"
                :disabled="isEditMode"
                placeholder="例如: ops_wang"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="真实姓名" prop="realName">
              <el-input v-model="userFormData.realName" placeholder="例如: 王建国" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="权限角色" prop="role">
              <el-select v-model="userFormData.role" placeholder="选择权限角色" style="width: 100%;">
                <el-option label="超级管理员" value="super_admin" />
                <el-option label="设备运维专家" value="device_admin" />
                <el-option label="嵌入式开发" value="developer" />
                <el-option label="安全审计员" value="auditor" />
                <el-option label="访客只读" value="guest" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="所属部门" prop="department">
              <el-input v-model="userFormData.department" placeholder="如: 技术部/运维组" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="手机号码" prop="phone">
              <el-input v-model="userFormData.phone" placeholder="11位手机号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="电子邮箱" prop="email">
              <el-input v-model="userFormData.email" placeholder="name@company.com" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16" v-if="!isEditMode">
          <el-col :span="24">
            <el-form-item label="初始密码" prop="password">
              <el-input
                v-model="userFormData.password"
                type="password"
                show-password
                placeholder="默认建议使用 8 位以上高强度密码"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16" v-else>
          <el-col :span="24">
            <el-form-item label="登录凭证">
              <div style="display: flex; gap: 8px; width: 100%;">
                <el-input
                  v-model="userFormData.newPassword"
                  placeholder="留空则保持原密码不变；输入则重置"
                  type="password"
                  show-password
                />
                <el-button type="warning" plain :icon="Key" @click="handleQuickResetInModal">
                  重置初始
                </el-button>
              </div>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="账号状态">
          <el-radio-group v-model="userFormData.status">
            <el-radio :value="1">正常启用</el-radio>
            <el-radio :value="0">锁定禁用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="userDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="submitUserForm">
          保存提交
        </el-button>
      </template>
    </el-dialog>

    <!-- Assign Role Dialog -->
    <el-dialog v-model="roleDialogVisible" title="分配账号角色与权限" width="480px">
      <div v-if="selectedUserForRole" class="role-modal-body">
        <p class="role-target-text">
          当前账号: <strong>{{ selectedUserForRole.realName }} ({{ selectedUserForRole.username }})</strong>
        </p>

        <el-radio-group v-model="tempSelectedRole" class="role-radio-group">
          <div class="role-card-option" :class="{ selected: tempSelectedRole === 'super_admin' }">
            <el-radio value="super_admin">
              <div class="role-desc-inner">
                <span class="role-title">超级管理员 (Super Admin)</span>
                <span class="role-sub">拥有系统全部权限，包括设备控制、用户增删改查及全局系统设置</span>
              </div>
            </el-radio>
          </div>

          <div class="role-card-option" :class="{ selected: tempSelectedRole === 'device_admin' }">
            <el-radio value="device_admin">
              <div class="role-desc-inner">
                <span class="role-title">设备运维专家 (Device Operator)</span>
                <span class="role-sub">拥有设备录入、远程指令下发、遥测监控及状态重启权限</span>
              </div>
            </el-radio>
          </div>

          <div class="role-card-option" :class="{ selected: tempSelectedRole === 'developer' }">
            <el-radio value="developer">
              <div class="role-desc-inner">
                <span class="role-title">嵌入式开发工程师 (Developer)</span>
                <span class="role-sub">具备 MQTT 调试、Topic 订阅配置及遥测数据调优权限</span>
              </div>
            </el-radio>
          </div>

          <div class="role-card-option" :class="{ selected: tempSelectedRole === 'auditor' }">
            <el-radio value="auditor">
              <div class="role-desc-inner">
                <span class="role-title">安全审计员 (Auditor)</span>
                <span class="role-sub">具备安全审计日志查看与导出权限，不可变更系统核心参数</span>
              </div>
            </el-radio>
          </div>

          <div class="role-card-option" :class="{ selected: tempSelectedRole === 'guest' }">
            <el-radio value="guest">
              <div class="role-desc-inner">
                <span class="role-title">只读访客 (Guest)</span>
                <span class="role-sub">仅可查看概览和数据看板，无任何写入或控制操作权限</span>
              </div>
            </el-radio>
          </div>
        </el-radio-group>
      </div>
      <template #footer>
        <el-button @click="roleDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveRoleAssignment">确定分配</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search,
  Refresh,
  Plus,
  Delete,
  Download,
  RefreshRight,
  Edit,
  Key,
  User,
  Stamp,
  Operation,
  InfoFilled
} from '@element-plus/icons-vue'
import {
  getStoredUsers,
  saveStoredUsers,
  addAuditLog
} from '@/utils/mockData'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

const tableRef = ref()
const allUsers = ref([])
const tableLoading = ref(false)
const selectedRows = ref([])

const clearSelection = () => {
  tableRef.value?.clearSelection()
  selectedRows.value = []
}

const queryForm = reactive({
  username: '',
  realName: '',
  role: '',
  status: ''
})

const pagination = reactive({
  currentPage: 1,
  pageSize: 10
})

const loadUserData = () => {
  tableLoading.value = true
  setTimeout(() => {
    allUsers.value = getStoredUsers()
    tableLoading.value = false
  }, 200)
}

onMounted(() => {
  loadUserData()
})

const filteredUsers = computed(() => {
  return allUsers.value.filter((user) => {
    const matchUsername = !queryForm.username || user.username.toLowerCase().includes(queryForm.username.toLowerCase().trim())
    const matchRealName = !queryForm.realName || user.realName.toLowerCase().includes(queryForm.realName.toLowerCase().trim())
    const matchRole = !queryForm.role || user.role === queryForm.role
    const matchStatus = queryForm.status === '' || user.status === queryForm.status
    return matchUsername && matchRealName && matchRole && matchStatus
  })
})

const paginatedUsers = computed(() => {
  const start = (pagination.currentPage - 1) * pagination.pageSize
  return filteredUsers.value.slice(start, start + pagination.pageSize)
})

const handleSearch = () => {
  pagination.currentPage = 1
}

const handleReset = () => {
  queryForm.username = ''
  queryForm.realName = ''
  queryForm.role = ''
  queryForm.status = ''
  pagination.currentPage = 1
}

const handleSelectionChange = (selection) => {
  selectedRows.value = selection
}

const getRoleTagType = (role) => {
  const map = {
    super_admin: 'danger',
    device_admin: 'primary',
    developer: 'success',
    auditor: 'warning',
    guest: 'info'
  }
  return map[role] || 'info'
}

const roleNameMap = {
  super_admin: '超级管理员',
  device_admin: '设备运维专家',
  developer: '嵌入式开发',
  auditor: '安全审计员',
  guest: '访客只读'
}

// User status switch
const beforeStatusChange = (row) => {
  const targetState = row.status === 1 ? '禁用' : '启用'
  return new Promise((resolve) => {
    ElMessageBox.confirm(
      `确定要【${targetState}】系统账号【${row.realName}】吗？`,
      '账号状态变更确认',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
    ).then(() => {
      resolve(true)
    }).catch(() => {
      resolve(false)
    })
  })
}

const handleStatusChange = (row, newVal) => {
  saveStoredUsers(allUsers.value)
  ElMessage.success(`账号 ${row.realName} 状态已更新为【${newVal === 1 ? '启用' : '禁用'}】`)
  addAuditLog({
    operator: userStore.currentUsername,
    action: '更新账号状态',
    target: row.username,
    detail: `状态变更: ${newVal === 1 ? '已启用' : '已禁用'}`,
    status: 'success',
    ip: '192.168.1.108'
  })
}

// Delete single user
const handleDeleteUser = (row) => {
  if (row.username === 'admin') {
    ElMessage.warning('系统内置超级管理员账号禁止删除！')
    return
  }
  allUsers.value = allUsers.value.filter((u) => u.id !== row.id)
  saveStoredUsers(allUsers.value)
  ElMessage.success(`系统账号【${row.realName}】已删除`)
  addAuditLog({
    operator: userStore.currentUsername,
    action: '删除系统账号',
    target: row.username,
    detail: `删除了账号 ID: ${row.id}, 姓名: ${row.realName}`,
    status: 'warning',
    ip: '192.168.1.108'
  })
}

// Batch delete
const handleBatchDelete = () => {
  if (selectedRows.value.length === 0) return
  ElMessageBox.confirm(
    `确定要批量删除选中的 ${selectedRows.value.length} 个账号吗？此操作无法恢复！`,
    '批量删除警示',
    { confirmButtonText: '确认删除', cancelButtonText: '取消', type: 'error' }
  ).then(() => {
    const selectedIds = selectedRows.value.map((r) => r.id)
    allUsers.value = allUsers.value.filter((u) => !selectedIds.includes(u.id) || u.username === 'admin')
    saveStoredUsers(allUsers.value)
    ElMessage.success(`已成功批量删除账号`)
    selectedRows.value = []
    addAuditLog({
      operator: userStore.currentUsername,
      action: '批量删除账号',
      target: '批量操作',
      detail: `批量删除了 ${selectedIds.length} 个系统账号`,
      status: 'warning',
      ip: '192.168.1.108'
    })
  }).catch(() => {})
}

// Export CSV simulated
const handleExportUsers = () => {
  const headers = ['账号编号', '登录账号', '真实姓名', '权限角色', '所属部门', '联系电话', '电子邮箱', '状态']
  const rows = filteredUsers.value.map((u) => [
    u.id,
    u.username,
    u.realName,
    u.roleName,
    u.department,
    u.phone,
    u.email,
    u.status === 1 ? '启用' : '禁用'
  ])

  const csvContent = 'data:text/csv;charset=utf-8,\uFEFF' + [headers.join(','), ...rows.map(e => e.join(','))].join('\n')
  const encodedUri = encodeURI(csvContent)
  const link = document.createElement('a')
  link.setAttribute('href', encodedUri)
  link.setAttribute('download', `系统账号列表_${new Date().toISOString().slice(0, 10)}.csv`)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  ElMessage.success('系统账号数据 CSV 报表已生成并开始下载')
}

// Reset Password
const handleResetPassword = (row) => {
  ElMessageBox.prompt(`请输入为账号【${row.realName}】重置的新密码：`, '重置登录密码', {
    confirmButtonText: '确定重置',
    cancelButtonText: '取消',
    inputValue: 'Cloud@2026',
    inputPattern: /^.{6,}$/,
    inputErrorMessage: '密码长度不能少于6位'
  }).then(({ value }) => {
    ElMessage.success(`账号【${row.realName}】的登录密码已重置为: ${value}`)
    addAuditLog({
      operator: userStore.currentUsername,
      action: '重置密码',
      target: row.username,
      detail: `管理员重置了 ${row.username} 的登录凭证`,
      status: 'info',
      ip: '192.168.1.108'
    })
  }).catch(() => {})
}

// Create / Edit Modal logic
const userDialogVisible = ref(false)
const isEditMode = ref(false)
const submitLoading = ref(false)
const userFormRef = ref(null)

const userFormData = reactive({
  id: '',
  username: '',
  realName: '',
  role: 'developer',
  department: '',
  phone: '',
  email: '',
  password: '',
  newPassword: '',
  status: 1
})

const userFormRules = {
  username: [
    { required: true, message: '请输入登录账号', trigger: 'blur' },
    { min: 3, message: '账号长度不少于3个字符', trigger: 'blur' }
  ],
  realName: [{ required: true, message: '请输入真实姓名', trigger: 'blur' }],
  role: [{ required: true, message: '请选择权限角色', trigger: 'change' }],
  phone: [
    { required: true, message: '请输入手机号码', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入规范的11位手机号', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入电子邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入规范的电子邮箱格式', trigger: 'blur' }
  ],
  password: [{ required: true, message: '请设定初始密码', trigger: 'blur' }]
}

const openCreateModal = () => {
  isEditMode.value = false
  userFormData.id = `USR-${Math.floor(1000 + Math.random() * 9000)}`
  userFormData.username = ''
  userFormData.realName = ''
  userFormData.role = 'device_admin'
  userFormData.department = '智能物联研发部'
  userFormData.phone = ''
  userFormData.email = ''
  userFormData.password = 'Iot@2026'
  userFormData.status = 1
  userDialogVisible.value = true
}

const openEditModal = (row) => {
  isEditMode.value = true
  userFormData.id = row.id
  userFormData.username = row.username
  userFormData.realName = row.realName
  userFormData.role = row.role
  userFormData.department = row.department || ''
  userFormData.phone = row.phone
  userFormData.email = row.email
  userFormData.newPassword = ''
  userFormData.status = row.status
  userDialogVisible.value = true
}

const handleQuickResetInModal = () => {
  userFormData.newPassword = 'Cloud@2026'
  ElMessage.info('已预填初始强密码: Cloud@2026，保存后即可生效')
}

const submitUserForm = async () => {
  if (!userFormRef.value) return
  await userFormRef.value.validate((valid) => {
    if (valid) {
      submitLoading.value = true
      setTimeout(() => {
        if (isEditMode.value) {
          const index = allUsers.value.findIndex((u) => u.id === userFormData.id)
          if (index > -1) {
            allUsers.value[index] = {
              ...allUsers.value[index],
              realName: userFormData.realName,
              role: userFormData.role,
              roleName: roleNameMap[userFormData.role] || userFormData.role,
              department: userFormData.department,
              phone: userFormData.phone,
              email: userFormData.email,
              status: userFormData.status
            }
          }
          if (userFormData.newPassword) {
            ElMessage.success(`账号信息与密码已更新为: ${userFormData.newPassword}`)
            addAuditLog({
              operator: userStore.currentUsername,
              action: '编辑并重置密码',
              target: userFormData.username,
              detail: `管理员在编辑中更新了密码`,
              status: 'info',
              ip: '192.168.1.108'
            })
          } else {
            ElMessage.success('账号信息已更新')
          }
        } else {
          const newUser = {
            id: userFormData.id,
            username: userFormData.username,
            realName: userFormData.realName,
            role: userFormData.role,
            roleName: roleNameMap[userFormData.role] || userFormData.role,
            department: userFormData.department,
            phone: userFormData.phone,
            email: userFormData.email,
            status: userFormData.status,
            avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png',
            lastLoginTime: '-',
            lastLoginIp: '-',
            createdAt: new Date().toISOString().slice(0, 19).replace('T', ' ')
          }
          allUsers.value.unshift(newUser)
          ElMessage.success('新系统账号已成功创建')
        }

        saveStoredUsers(allUsers.value)
        submitLoading.value = false
        userDialogVisible.value = false
      }, 300)
    }
  })
}

// Role Assign modal
const roleDialogVisible = ref(false)
const selectedUserForRole = ref(null)
const tempSelectedRole = ref('')

const openRoleModal = (row) => {
  selectedUserForRole.value = row
  tempSelectedRole.value = row.role
  roleDialogVisible.value = true
}

const saveRoleAssignment = () => {
  if (!selectedUserForRole.value) return
  const index = allUsers.value.findIndex((u) => u.id === selectedUserForRole.value.id)
  if (index > -1) {
    allUsers.value[index].role = tempSelectedRole.value
    allUsers.value[index].roleName = roleNameMap[tempSelectedRole.value]
    saveStoredUsers(allUsers.value)
    ElMessage.success(`已为【${selectedUserForRole.value.realName}】重新分配角色为【${roleNameMap[tempSelectedRole.value]}】`)
    addAuditLog({
      operator: userStore.currentUsername,
      action: '分配账号角色',
      target: selectedUserForRole.value.username,
      detail: `将角色变更为: ${roleNameMap[tempSelectedRole.value]}`,
      status: 'info',
      ip: '192.168.1.108'
    })
  }
  roleDialogVisible.value = false
}
</script>

<style scoped>
.filter-form {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 12px;
}

.user-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-info {
  display: flex;
  flex-direction: column;
  line-height: 1.25;
}

.user-realname {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-main);
}

.user-subname {
  font-size: 11px;
  color: #94a3b8;
  font-family: monospace;
}

.time-cell {
  display: flex;
  flex-direction: column;
  font-size: 12px;
  line-height: 1.3;
}

.ip-sub {
  font-size: 11px;
  color: #94a3b8;
  font-family: monospace;
}

.pagination-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid var(--border-light);
  flex-wrap: wrap;
  gap: 12px;
}

.page-total-text {
  font-size: 12px;
  color: #64748b;
}

/* Role Assign Modal Styling */
.role-modal-body {
  padding: 4px;
}

.role-target-text {
  font-size: 13px;
  color: #475569;
  margin-bottom: 14px;
}

.role-radio-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: 100%;
}

.role-card-option {
  border: 1px solid var(--border-color);
  border-radius: 10px;
  padding: 10px 14px;
  transition: all 0.2s;
  cursor: pointer;
  background-color: var(--card-bg);
}

.role-card-option:hover {
  background-color: var(--menu-hover-bg, #f1f5f9);
}

.role-card-option.selected {
  border-color: var(--primary-color);
  background-color: var(--menu-active-bg, #eff6ff);
}

.role-desc-inner {
  display: flex;
  flex-direction: column;
  margin-left: 8px;
}

.role-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-main);
}

.role-sub {
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
