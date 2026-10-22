<template>
  <div class="page-container dict-page">
    <el-row :gutter="16" class="dict-split-row">
      <!-- Left Panel: Dictionary Types -->
      <el-col :xs="24" :md="9" :lg="8">
        <el-card shadow="never" class="type-card">
          <template #header>
            <div class="card-header-flex">
              <span class="card-title">
                <el-icon color="#2563eb"><Notebook /></el-icon> 字典类型目录
              </span>
              <el-button type="primary" size="small" :icon="Plus" @click="openCreateTypeModal">
                新建类型
              </el-button>
            </div>
          </template>

          <el-input
            v-model="typeSearchKeyword"
            placeholder="搜索字典名称或标识..."
            :prefix-icon="Search"
            clearable
            size="small"
            style="margin-bottom: 12px;"
          />

          <div class="type-list-wrapper">
            <div
              v-for="item in filteredDictTypes"
              :key="item.id"
              class="dict-type-item"
              :class="{ active: currentSelectedType?.dictType === item.dictType }"
              @click="selectDictType(item)"
            >
              <div class="type-info">
                <div class="type-header-row">
                  <span class="type-name">{{ item.dictName }}</span>
                  <el-tag size="small" :type="item.status === 1 ? 'success' : 'info'">
                    {{ item.status === 1 ? '启用' : '停用' }}
                  </el-tag>
                </div>
                <span class="type-code mono">{{ item.dictType }}</span>
                <span class="type-remark" v-if="item.remark">{{ item.remark }}</span>
              </div>
              <div class="type-actions" @click.stop>
                <el-tooltip content="编辑字典类型" placement="top">
                  <el-button link type="primary" :icon="Edit" size="small" aria-label="编辑字典类型" @click="openEditTypeModal(item)" />
                </el-tooltip>
                <el-popconfirm
                  title="确定删除该字典类型吗？"
                  confirm-button-text="删除"
                  cancel-button-text="取消"
                  confirm-button-type="danger"
                  width="auto"
                  @confirm="handleDeleteType(item)"
                >
                  <template #reference>
                    <el-tooltip content="删除字典类型" placement="top">
                      <el-button link type="danger" :icon="Delete" size="small" aria-label="删除字典类型" />
                    </el-tooltip>
                  </template>
                </el-popconfirm>
              </div>
            </div>

            <div v-if="filteredDictTypes.length === 0" class="empty-state">
              暂无匹配的字典类型
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- Right Panel: Dictionary Data Items -->
      <el-col :xs="24" :md="15" :lg="16">
        <el-card shadow="never" class="items-card">
          <template #header>
            <div class="card-header-flex">
              <div>
                <span class="card-title">
                  <el-icon color="#10b981"><Tickets /></el-icon>
                  字典键值数据项：<strong>{{ currentSelectedType?.dictName || '请选择类型' }}</strong>
                </span>
                <span class="type-indicator mono" v-if="currentSelectedType">
                  ({{ currentSelectedType.dictType }})
                </span>
              </div>
              <div class="header-right-btns">
                <el-button
                  type="primary"
                  size="small"
                  :icon="Plus"
                  :disabled="!currentSelectedType"
                  @click="openCreateDataModal"
                >
                  新增字典键值
                </el-button>
              </div>
            </div>
          </template>

          <el-table
            :data="currentTypeDataItems"
            stripe
            style="width: 100%"
            empty-text="当前字典类型下暂无数据项，请点击上方按钮添加"
          >
            <el-table-column prop="orderNum" label="排序" width="70" align="center" />
            <el-table-column label="字典标签 (Label)" min-width="150">
              <template #default="{ row }">
                <div class="label-cell">
                  <el-tag size="small" :type="row.listClass || ''" effect="light">
                    {{ row.label }}
                  </el-tag>
                </div>
              </template>
            </el-table-column>

            <el-table-column prop="value" label="数据键值 (Value)" min-width="140">
              <template #default="{ row }">
                <span class="mono">{{ row.value }}</span>
              </template>
            </el-table-column>

            <el-table-column label="渲染色彩样式" width="120" align="center">
              <template #default="{ row }">
                <el-tag size="small" :type="row.listClass || 'info'">
                  {{ row.listClass || '默认' }}
                </el-tag>
              </template>
            </el-table-column>

            <el-table-column label="默认选中" width="100" align="center">
              <template #default="{ row }">
                <el-tag size="small" :type="row.isDefault ? 'success' : 'info'" effect="plain">
                  {{ row.isDefault ? '是' : '否' }}
                </el-tag>
              </template>
            </el-table-column>

            <el-table-column label="操作" width="144" align="center">
              <template #default="{ row }">
                <div class="table-op-btns">
                  <el-button link type="primary" size="small" :icon="Edit" @click="openEditDataModal(row)">
                    编辑
                  </el-button>
                  <el-popconfirm
                    title="确定删除该键值项吗？"
                    confirm-button-text="删除"
                    cancel-button-text="取消"
                    confirm-button-type="danger"
                    width="auto"
                    @confirm="handleDeleteData(row)"
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
      </el-col>
    </el-row>

    <!-- Modal: Dict Type Create/Edit -->
    <el-dialog
      v-model="typeDialogVisible"
      :title="isEditType ? '编辑字典类型' : '新建字典类型'"
      width="460px"
      destroy-on-close
    >
      <el-form ref="typeFormRef" :model="typeFormData" :rules="typeFormRules" label-width="90px">
        <el-form-item label="字典名称" prop="dictName">
          <el-input v-model="typeFormData.dictName" placeholder="例如: 客户等级" />
        </el-form-item>
        <el-form-item label="字典类型" prop="dictType">
          <el-input v-model="typeFormData.dictType" :disabled="isEditType" placeholder="如: sys_customer_level" />
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="typeFormData.status">
            <el-radio :value="1">正常</el-radio>
            <el-radio :value="0">停用</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="备注说明">
          <el-input v-model="typeFormData.remark" type="textarea" :rows="2" placeholder="填写该字典的应用场景" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="typeDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitTypeForm">保存类型</el-button>
      </template>
    </el-dialog>

    <!-- Modal: Dict Item Create/Edit -->
    <el-dialog
      v-model="dataDialogVisible"
      :title="isEditData ? '编辑字典数据项' : '新增字典数据项'"
      width="480px"
      destroy-on-close
    >
      <el-form ref="dataFormRef" :model="dataFormData" :rules="dataFormRules" label-width="100px">
        <el-form-item label="所属字典">
          <el-input :model-value="currentSelectedType?.dictName" disabled />
        </el-form-item>
        <el-form-item label="数据标签" prop="label">
          <el-input v-model="dataFormData.label" placeholder="例如: 重点VIP客户" />
        </el-form-item>
        <el-form-item label="数据键值" prop="value">
          <el-input v-model="dataFormData.value" placeholder="例如: vip_level_1" />
        </el-form-item>
        <el-form-item label="显示排序" prop="orderNum">
          <el-input-number v-model="dataFormData.orderNum" :min="1" :max="999" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="展示样式">
          <el-select v-model="dataFormData.listClass" style="width: 100%;">
            <el-option label="默认 (灰色)" value="" />
            <el-option label="主要 (蓝色 primary)" value="primary" />
            <el-option label="成功 (绿色 success)" value="success" />
            <el-option label="警告 (黄色 warning)" value="warning" />
            <el-option label="危险 (红色 danger)" value="danger" />
            <el-option label="信息 (深灰 info)" value="info" />
          </el-select>
        </el-form-item>
        <el-form-item label="设为默认">
          <el-switch v-model="dataFormData.isDefault" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dataDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitDataForm">确定提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Notebook,
  Tickets,
  Plus,
  Search,
  Edit,
  Delete
} from '@element-plus/icons-vue'
import {
  getStoredDictTypes,
  saveStoredDictTypes,
  getStoredDictData,
  saveStoredDictData,
  addAuditLog
} from '@/utils/mockData'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

const dictTypes = ref([])
const dictData = ref([])
const currentSelectedType = ref(null)
const typeSearchKeyword = ref('')

const loadAllDictData = () => {
  dictTypes.value = getStoredDictTypes()
  dictData.value = getStoredDictData()
  if (!currentSelectedType.value && dictTypes.value.length > 0) {
    currentSelectedType.value = dictTypes.value[0]
  }
}

onMounted(() => {
  loadAllDictData()
})

const filteredDictTypes = computed(() => {
  if (!typeSearchKeyword.value.trim()) return dictTypes.value
  const kw = typeSearchKeyword.value.toLowerCase().trim()
  return dictTypes.value.filter(
    (t) => t.dictName.toLowerCase().includes(kw) || t.dictType.toLowerCase().includes(kw)
  )
})

const currentTypeDataItems = computed(() => {
  if (!currentSelectedType.value) return []
  return dictData.value.filter((d) => d.dictType === currentSelectedType.value.dictType)
})

const selectDictType = (item) => {
  currentSelectedType.value = item
}

// Dict Type Create/Edit
const typeDialogVisible = ref(false)
const isEditType = ref(false)
const typeFormRef = ref(null)

const typeFormData = reactive({
  id: 0,
  dictName: '',
  dictType: '',
  status: 1,
  remark: ''
})

const typeFormRules = {
  dictName: [{ required: true, message: '请输入字典名称', trigger: 'blur' }],
  dictType: [{ required: true, message: '请输入字典类型标识', trigger: 'blur' }]
}

const openCreateTypeModal = () => {
  isEditType.value = false
  typeFormData.id = Date.now()
  typeFormData.dictName = ''
  typeFormData.dictType = ''
  typeFormData.status = 1
  typeFormData.remark = ''
  typeDialogVisible.value = true
}

const openEditTypeModal = (item) => {
  isEditType.value = true
  typeFormData.id = item.id
  typeFormData.dictName = item.dictName
  typeFormData.dictType = item.dictType
  typeFormData.status = item.status
  typeFormData.remark = item.remark || ''
  typeDialogVisible.value = true
}

const submitTypeForm = async () => {
  if (!typeFormRef.value) return
  await typeFormRef.value.validate((valid) => {
    if (valid) {
      if (isEditType.value) {
        const idx = dictTypes.value.findIndex((t) => t.id === typeFormData.id)
        if (idx > -1) {
          dictTypes.value[idx] = { ...dictTypes.value[idx], ...typeFormData }
        }
        ElMessage.success('字典类型更新成功')
      } else {
        const newType = {
          ...typeFormData,
          createTime: new Date().toISOString().slice(0, 19).replace('T', ' ')
        }
        dictTypes.value.push(newType)
        currentSelectedType.value = newType
        ElMessage.success('新建字典类型成功')
      }
      saveStoredDictTypes(dictTypes.value)
      typeDialogVisible.value = false
    }
  })
}

const handleDeleteType = (item) => {
  dictTypes.value = dictTypes.value.filter((t) => t.id !== item.id)
  dictData.value = dictData.value.filter((d) => d.dictType !== item.dictType)
  saveStoredDictTypes(dictTypes.value)
  saveStoredDictData(dictData.value)
  if (currentSelectedType.value?.id === item.id) {
    currentSelectedType.value = dictTypes.value[0] || null
  }
  ElMessage.success('字典类型及关联键值项已删除')
}

// Dict Data Items Create/Edit
const dataDialogVisible = ref(false)
const isEditData = ref(false)
const dataFormRef = ref(null)

const dataFormData = reactive({
  id: 0,
  dictType: '',
  label: '',
  value: '',
  orderNum: 1,
  listClass: '',
  isDefault: false
})

const dataFormRules = {
  label: [{ required: true, message: '请输入数据标签', trigger: 'blur' }],
  value: [{ required: true, message: '请输入数据键值', trigger: 'blur' }]
}

const openCreateDataModal = () => {
  isEditData.value = false
  dataFormData.id = Date.now()
  dataFormData.dictType = currentSelectedType.value.dictType
  dataFormData.label = ''
  dataFormData.value = ''
  dataFormData.orderNum = currentTypeDataItems.value.length + 1
  dataFormData.listClass = 'primary'
  dataFormData.isDefault = false
  dataDialogVisible.value = true
}

const openEditDataModal = (row) => {
  isEditData.value = true
  dataFormData.id = row.id
  dataFormData.dictType = row.dictType
  dataFormData.label = row.label
  dataFormData.value = row.value
  dataFormData.orderNum = row.orderNum
  dataFormData.listClass = row.listClass || ''
  dataFormData.isDefault = row.isDefault || false
  dataDialogVisible.value = true
}

const submitDataForm = async () => {
  if (!dataFormRef.value) return
  await dataFormRef.value.validate((valid) => {
    if (valid) {
      if (isEditData.value) {
        const idx = dictData.value.findIndex((d) => d.id === dataFormData.id)
        if (idx > -1) {
          dictData.value[idx] = { ...dictData.value[idx], ...dataFormData }
        }
        ElMessage.success('字典键值更新成功')
      } else {
        dictData.value.push({ ...dataFormData })
        ElMessage.success('新增字典键值成功')
      }
      saveStoredDictData(dictData.value)
      dataDialogVisible.value = false
    }
  })
}

const handleDeleteData = (row) => {
  dictData.value = dictData.value.filter((d) => d.id !== row.id)
  saveStoredDictData(dictData.value)
  ElMessage.success('字典键值项已删除')
}
</script>

<style scoped>
.dict-page {
  padding: 16px;
}

.dict-split-row {
  height: calc(100vh - var(--header-height) - var(--tags-height) - 32px);
}

.type-card,
.items-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.type-card :deep(.el-card__body),
.items-card :deep(.el-card__body) {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.card-header-flex {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-main);
  display: flex;
  align-items: center;
  gap: 6px;
}

.type-indicator {
  font-size: 12px;
  color: #64748b;
  margin-left: 6px;
}

.type-list-wrapper {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding-right: 4px;
}

.dict-type-item {
  border: 1px solid var(--border-color);
  border-radius: 10px;
  padding: 10px 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  background-color: var(--card-bg);
  transition: all 0.2s;
}

.dict-type-item:hover {
  background-color: var(--menu-hover-bg, #f1f5f9);
  border-color: var(--border-color);
}

.dict-type-item.active {
  border-color: var(--primary-color);
  background-color: var(--menu-active-bg, #eff6ff);
}

.type-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
  min-width: 0;
}

.type-header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.type-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-main);
}

.type-code {
  font-size: 11px;
  color: #2563eb;
}

.type-remark {
  font-size: 11px;
  color: #94a3b8;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.type-actions {
  display: flex;
  gap: 2px;
}

.mono {
  font-family: monospace;
}

.empty-state {
  text-align: center;
  padding: 40px 0;
  color: #94a3b8;
  font-size: 12px;
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
