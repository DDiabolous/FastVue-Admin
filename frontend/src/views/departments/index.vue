<template>
  <div class="page-container">
    <!-- Search / Filter Card -->
    <el-card shadow="never" class="search-form-card">
      <el-form :inline="true" :model="queryForm" class="filter-form">
        <el-form-item label="部门名称">
          <el-input
            v-model="queryForm.deptName"
            placeholder="请输入部门名称"
            clearable
            @keyup.enter="handleSearch"
          />
        </el-form-item>

        <el-form-item label="部门状态">
          <el-select v-model="queryForm.status" placeholder="全部状态" clearable style="width: 140px;">
            <el-option label="正常启用" :value="1" />
            <el-option label="停用冻结" :value="0" />
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
          <el-button type="primary" :icon="Plus" @click="openCreateModal(null)">
            新增顶级部门
          </el-button>
          <el-button :icon="Sort" @click="toggleExpandAll">
            {{ isExpandAll ? '折叠全部' : '展开全部' }}
          </el-button>
        </div>

        <div class="right-actions">
          <el-tooltip content="刷新组织架构" placement="top">
            <el-button circle :icon="RefreshRight" @click="loadDeptData" />
          </el-tooltip>
        </div>
      </div>

      <!-- Tree Table -->
      <el-table
        v-if="refreshTable"
        v-loading="tableLoading"
        :data="filteredDepts"
        row-key="id"
        :default-expand-all="isExpandAll"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="deptName" label="部门名称" min-width="260">
          <template #default="{ row }">
            <div class="dept-name-cell">
              <el-icon color="#2563eb" style="margin-right: 6px;"><OfficeBuilding /></el-icon>
              <span class="dept-title-text">{{ row.deptName }}</span>
              <el-tag size="small" type="info" effect="plain" class="dept-code-tag">{{ row.deptCode }}</el-tag>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="orderNum" label="排序权重" width="90" align="center" />

        <el-table-column prop="leader" label="部门负责人" width="130">
          <template #default="{ row }">
            <span class="font-medium">{{ row.leader || '-' }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="phone" label="联系电话" width="130" />

        <el-table-column prop="email" label="部门邮箱" min-width="160" show-overflow-tooltip />

        <el-table-column label="部门状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'danger'" size="small">
              {{ row.status === 1 ? '正常' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="createTime" label="创建时间" width="170" />

        <el-table-column label="操作" width="240" fixed="right" align="center">
          <template #default="{ row }">
            <div class="table-op-btns">
              <el-button link type="primary" size="small" :icon="Plus" @click="openCreateModal(row)">
                新增子级
              </el-button>
              <el-button link type="primary" size="small" :icon="Edit" @click="openEditModal(row)">
                编辑
              </el-button>
              <el-popconfirm
                title="确定要删除该部门吗？若存在子部门将一同移除！"
                confirm-button-text="确认删除"
                cancel-button-text="取消"
                confirm-button-type="danger"
                @confirm="handleDeleteDept(row)"
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

    <!-- Create / Edit Department Modal -->
    <el-dialog
      v-model="deptDialogVisible"
      :title="isEditMode ? '编辑部门信息' : '新增组织部门'"
      width="560px"
      destroy-on-close
    >
      <el-form
        ref="deptFormRef"
        :model="deptFormData"
        :rules="deptFormRules"
        label-width="95px"
        style="padding: 10px 10px 0;"
      >
        <el-form-item label="上级部门">
          <el-tree-select
            v-model="deptFormData.parentId"
            :data="deptTreeOptions"
            :props="{ label: 'deptName', value: 'id', children: 'children' }"
            value-key="id"
            placeholder="选择上级部门 (若为空则为顶级部门)"
            check-strictly
            clearable
            style="width: 100%;"
          />
        </el-form-item>

        <el-row :gutter="16">
          <el-col :span="14">
            <el-form-item label="部门名称" prop="deptName">
              <el-input v-model="deptFormData.deptName" placeholder="例如: 智能制造研发中心" />
            </el-form-item>
          </el-col>
          <el-col :span="10">
            <el-form-item label="部门编码" prop="deptCode">
              <el-input v-model="deptFormData.deptCode" placeholder="如: TECH_AI" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="负责人" prop="leader">
              <el-input v-model="deptFormData.leader" placeholder="姓名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="显示排序" prop="orderNum">
              <el-input-number v-model="deptFormData.orderNum" :min="1" :max="999" style="width: 100%;" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="联系电话" prop="phone">
              <el-input v-model="deptFormData.phone" placeholder="手机或办公电话" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="电子邮箱" prop="email">
              <el-input v-model="deptFormData.email" placeholder="dept@cloudhub.com" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="部门状态">
          <el-radio-group v-model="deptFormData.status">
            <el-radio :value="1">正常启用</el-radio>
            <el-radio :value="0">停用注销</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="deptDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="submitDeptForm">
          保存提交
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Search,
  Refresh,
  Plus,
  Sort,
  RefreshRight,
  OfficeBuilding,
  Edit,
  Delete
} from '@element-plus/icons-vue'
import {
  getStoredDepartments,
  saveStoredDepartments,
  addAuditLog
} from '@/utils/mockData'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

const allDepts = ref([])
const tableLoading = ref(false)
const isExpandAll = ref(true)
const refreshTable = ref(true)

const queryForm = reactive({
  deptName: '',
  status: ''
})

const loadDeptData = () => {
  tableLoading.value = true
  setTimeout(() => {
    allDepts.value = getStoredDepartments()
    tableLoading.value = false
  }, 150)
}

onMounted(() => {
  loadDeptData()
})

const toggleExpandAll = () => {
  refreshTable.value = false
  isExpandAll.value = !isExpandAll.value
  nextTick(() => {
    refreshTable.value = true
  })
}

const filterDeptTree = (list) => {
  const result = []
  for (const node of list) {
    const copy = { ...node }
    const matchName = !queryForm.deptName || copy.deptName.toLowerCase().includes(queryForm.deptName.toLowerCase().trim())
    const matchStatus = queryForm.status === '' || copy.status === queryForm.status

    if (copy.children && copy.children.length > 0) {
      copy.children = filterDeptTree(copy.children)
    }

    if (matchName && matchStatus) {
      result.push(copy)
    } else if (copy.children && copy.children.length > 0) {
      result.push(copy)
    }
  }
  return result
}

const filteredDepts = computed(() => {
  if (!queryForm.deptName && queryForm.status === '') {
    return allDepts.value
  }
  return filterDeptTree(allDepts.value)
})

const deptTreeOptions = computed(() => {
  return [
    {
      id: 0,
      deptName: '根目录 (顶级公司)',
      children: allDepts.value
    }
  ]
})

const handleSearch = () => {
  // computed reactive
}

const handleReset = () => {
  queryForm.deptName = ''
  queryForm.status = ''
}

// Modal handling
const deptDialogVisible = ref(false)
const isEditMode = ref(false)
const submitLoading = ref(false)
const deptFormRef = ref(null)

const deptFormData = reactive({
  id: 0,
  parentId: 0,
  deptName: '',
  deptCode: '',
  leader: '',
  phone: '',
  email: '',
  orderNum: 1,
  status: 1
})

const deptFormRules = {
  deptName: [{ required: true, message: '请输入部门名称', trigger: 'blur' }],
  deptCode: [{ required: true, message: '请输入部门编码', trigger: 'blur' }]
}

const openCreateModal = (parentRow) => {
  isEditMode.value = false
  deptFormData.id = Date.now()
  deptFormData.parentId = parentRow ? parentRow.id : 0
  deptFormData.deptName = ''
  deptFormData.deptCode = ''
  deptFormData.leader = ''
  deptFormData.phone = ''
  deptFormData.email = ''
  deptFormData.orderNum = 1
  deptFormData.status = 1
  deptDialogVisible.value = true
}

const openEditModal = (row) => {
  isEditMode.value = true
  deptFormData.id = row.id
  deptFormData.parentId = findParentId(allDepts.value, row.id) || 0
  deptFormData.deptName = row.deptName
  deptFormData.deptCode = row.deptCode
  deptFormData.leader = row.leader || ''
  deptFormData.phone = row.phone || ''
  deptFormData.email = row.email || ''
  deptFormData.orderNum = row.orderNum || 1
  deptFormData.status = row.status
  deptDialogVisible.value = true
}

const findParentId = (nodes, targetId, parentId = 0) => {
  for (const node of nodes) {
    if (node.id === targetId) return parentId
    if (node.children) {
      const found = findParentId(node.children, targetId, node.id)
      if (found !== null) return found
    }
  }
  return null
}

const submitDeptForm = async () => {
  if (!deptFormRef.value) return
  await deptFormRef.value.validate((valid) => {
    if (valid) {
      submitLoading.value = true
      setTimeout(() => {
        const newDept = {
          id: deptFormData.id,
          deptName: deptFormData.deptName,
          deptCode: deptFormData.deptCode,
          leader: deptFormData.leader,
          phone: deptFormData.phone,
          email: deptFormData.email,
          orderNum: deptFormData.orderNum,
          status: deptFormData.status,
          createTime: new Date().toISOString().slice(0, 19).replace('T', ' '),
          children: []
        }

        if (isEditMode.value) {
          updateDeptNode(allDepts.value, deptFormData.id, newDept)
          ElMessage.success('部门信息修改成功')
        } else {
          if (!deptFormData.parentId || deptFormData.parentId === 0) {
            allDepts.value.push(newDept)
          } else {
            insertChildNode(allDepts.value, deptFormData.parentId, newDept)
          }
          ElMessage.success('新组织部门已成功创建')
        }

        saveStoredDepartments(allDepts.value)
        addAuditLog({
          operator: userStore.currentUsername,
          action: isEditMode.value ? '修改组织部门' : '新增组织部门',
          target: deptFormData.deptName,
          detail: `部门编码: ${deptFormData.deptCode}, 负责人: ${deptFormData.leader}`,
          status: 'success',
          ip: '192.168.1.108'
        })

        submitLoading.value = false
        deptDialogVisible.value = false
      }, 300)
    }
  })
}

const updateDeptNode = (nodes, id, updatedData) => {
  for (const node of nodes) {
    if (node.id === id) {
      node.deptName = updatedData.deptName
      node.deptCode = updatedData.deptCode
      node.leader = updatedData.leader
      node.phone = updatedData.phone
      node.email = updatedData.email
      node.orderNum = updatedData.orderNum
      node.status = updatedData.status
      return true
    }
    if (node.children && updateDeptNode(node.children, id, updatedData)) {
      return true
    }
  }
  return false
}

const insertChildNode = (nodes, parentId, childNode) => {
  for (const node of nodes) {
    if (node.id === parentId) {
      if (!node.children) node.children = []
      node.children.push(childNode)
      return true
    }
    if (node.children && insertChildNode(node.children, parentId, childNode)) {
      return true
    }
  }
  return false
}

const handleDeleteDept = (row) => {
  deleteDeptNode(allDepts.value, row.id)
  saveStoredDepartments(allDepts.value)
  ElMessage.success(`部门【${row.deptName}】已移除`)
  addAuditLog({
    operator: userStore.currentUsername,
    action: '删除组织部门',
    target: row.deptName,
    detail: `删除了部门 ID: ${row.id}`,
    status: 'warning',
    ip: '192.168.1.108'
  })
}

const deleteDeptNode = (nodes, id) => {
  const index = nodes.findIndex((n) => n.id === id)
  if (index > -1) {
    nodes.splice(index, 1)
    return true
  }
  for (const node of nodes) {
    if (node.children && deleteDeptNode(node.children, id)) {
      return true
    }
  }
  return false
}
</script>

<style scoped>
.filter-form {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 12px;
}

.dept-name-cell {
  display: flex;
  align-items: center;
}

.dept-title-text {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-main);
  margin-right: 8px;
}

.dept-code-tag {
  font-size: 10px;
  height: 20px;
  line-height: 18px;
}

.font-medium {
  font-weight: 500;
  color: var(--text-main);
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
