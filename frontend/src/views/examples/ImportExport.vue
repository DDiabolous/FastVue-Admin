<template>
  <PageContainer
    class="business-page example-page"
    title="导入与导出"
    description="演示 CSV 校验、异常行定位、重复处理与筛选导出。"
  >
    <template #actions>
      <ExampleGuide
        source="ImportExport.vue"
        scope="CSV 在浏览器中解析和校验，导入数据仅用于本页演示，不提交到后端。"
      />
    </template>
    <el-card shadow="never" class="data-card business-data-card">
      <FilterPanel :model="filters" @search="handleFilter">
        <el-form-item label="人员姓名">
          <el-input
            v-model="filters.name"
            placeholder="搜索姓名"
            clearable
            @keyup.enter="handleFilter"
          />
        </el-form-item>
        <el-form-item label="所属部门">
          <el-select
            v-model="filters.department"
            placeholder="全部部门"
            clearable
            style="width: 140px"
          >
            <el-option label="技术研发部" value="技术研发部" />
            <el-option label="产品设计部" value="产品设计部" />
            <el-option label="市场运营部" value="市场运营部" />
          </el-select>
        </el-form-item>
        <template #actions>
          <el-form-item class="form-btn-item">
            <el-button type="primary" icon="Search" native-type="submit">查询</el-button>
            <el-button icon="Refresh" @click="resetFilter">重置</el-button>
          </el-form-item>
        </template>
      </FilterPanel>

      <TableToolbar
        :total="filteredData.length"
        :selected="selectedRows.length"
      >
        <el-button type="primary" icon="Upload" @click="openImportDialog">导入</el-button>
        <el-button icon="Download" @click="handleDownloadTemplate">下载模板</el-button>
        <el-button
          icon="DocumentCopy"
          :disabled="!selectedRows.length"
          @click="handleExportSelected"
        >
          导出已选
        </el-button>
        <el-button icon="Download" :disabled="!filteredData.length" @click="handleExportAll">
          导出筛选结果
        </el-button>
      </TableToolbar>
      <!-- 数据表格 -->
      <el-table
        ref="dataTable"
        :data="filteredData"
        stripe
        row-key="id"
        @selection-change="handleSelectionChange"
        border
        style="width: 100%"
      >
        <el-table-column type="selection" width="50" align="center" />
        <el-table-column prop="id" label="工号" width="100" align="center" />
        <el-table-column prop="name" label="姓名" min-width="120" />
        <el-table-column prop="department" label="部门" min-width="140" />
        <el-table-column prop="email" label="邮箱" min-width="180" />
        <el-table-column prop="phone" label="手机号码" min-width="140" align="center" />
        <el-table-column prop="address" label="通讯地址" min-width="180" show-overflow-tooltip />
        <el-table-column label="在职状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === '在职' ? 'success' : 'info'" effect="light">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 批量导入模态弹窗 -->
    <el-dialog
      class="business-overlay"
      v-model="importDialogVisible"
      title="批量导入人员数据"
      width="680px"
      destroy-on-close
    >
      <div class="import-dialog-body">
        <el-alert
          title="导入规则说明"
          type="info"
          show-icon
          :closable="false"
          description="系统支持标准 RFC 4180 CSV 格式（支持包含逗号与转义引号的文本）。单次支持导入至多 1,000 条记录。"
          style="margin-bottom: 16px"
        />

        <!-- 文件上传/选择区 -->
        <el-upload
          drag
          action="#"
          :auto-upload="false"
          accept=".csv,text/csv"
          :show-file-list="false"
          :on-change="handleFileSelected"
        >
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">
            将 CSV 文件拖到此处，或
            <em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">
              推荐先
              <el-link type="primary" :underline="false" @click="handleDownloadTemplate">
                下载标准模板
              </el-link>
              填写后上传。
            </div>
          </template>
        </el-upload>

        <!-- 校验结果汇总与失败明细 -->
        <div v-if="parseResult" class="validate-result-box">
          <el-divider content-position="left">数据校验结果</el-divider>
          <p>
            重复邮箱处理：
            <el-radio-group v-model="duplicateMode">
              <el-radio value="skip">跳过重复</el-radio>
              <el-radio value="update">更新已有</el-radio>
            </el-radio-group>
          </p>
          <el-alert
            title="邮箱作为唯一标识，同时检查现有数据与本次文件中的重复项。"
            type="info"
            :closable="false"
          />

          <el-row :gutter="16" class="stat-row">
            <el-col :span="8">
              <div class="stat-card">
                <span class="label">解析数据总数</span>
                <span class="val">
                  {{ parseResult.validRows.length + parseResult.failedRows.length }}
                </span>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="stat-card success">
                <span class="label">校验通过</span>
                <span class="val">{{ parseResult.validRows.length }}</span>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="stat-card danger">
                <span class="label">校验异常</span>
                <span class="val">{{ parseResult.failedRows.length }}</span>
              </div>
            </el-col>
          </el-row>

          <!-- 失败行列表展示 -->
          <div v-if="parseResult.failedRows.length" class="failed-list-box">
            <div class="failed-header">
              <span class="title">
                ❌ 异常数据明细（共 {{ parseResult.failedRows.length }} 行）
              </span>
              <el-button size="small" type="danger" link @click="exportFailedRows">
                导出失败数据
              </el-button>
            </div>
            <el-table :data="parseResult.failedRows" max-height="200" size="small" stripe border>
              <el-table-column prop="rowNum" label="行号" width="70" align="center" />
              <el-table-column label="错误原因" min-width="240">
                <template #default="{ row }">
                  <span class="error-text">{{ row.errors.join('； ') }}</span>
                </template>
              </el-table-column>
              <el-table-column label="原始数据摘要" min-width="180">
                <template #default="{ row }">
                  <span class="raw-text">{{ row.raw.name }} | {{ row.raw.phone }}</span>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </div>

      <template #footer>
        <el-button @click="importDialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          :disabled="!parseResult || !parseResult.validRows.length"
          :loading="importing"
          @click="confirmImport"
        >
          确定导入有效数据 ({{ parseResult?.validRows?.length || 0 }}条)
        </el-button>
      </template>
    </el-dialog>
  </PageContainer>
</template>

<script setup>
import ExampleGuide from '@/components/examples/ExampleGuide.vue'
import { ref, reactive, computed, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import PageContainer from '@/components/admin/PageContainer.vue'
import FilterPanel from '@/components/admin/FilterPanel.vue'
import TableToolbar from '@/components/admin/TableToolbar.vue'
import { exportToCsv, parseAndValidateCsv } from '@/composables/useImportExport'

// 初始模拟业务数据
const tableList = ref([
  {
    id: 'E1001',
    name: '张伟',
    department: '技术研发部',
    email: 'zhangwei@example.com',
    phone: '13800138001',
    address: '北京市, 朝阳区, 望京SOHO',
    status: '在职',
  },
  {
    id: 'E1002',
    name: '李静',
    department: '产品设计部',
    email: 'lijing@example.com',
    phone: '13900139002',
    address: '上海市, 浦东新区',
    status: '在职',
  },
  {
    id: 'E1003',
    name: '王敏',
    department: '市场运营部',
    email: 'wangmin@example.com',
    phone: '13700137003',
    address: '广州市, 天河区',
    status: '在职',
  },
  {
    id: 'E1004',
    name: '刘超',
    department: '技术研发部',
    email: 'liuchao@example.com',
    phone: '13600136004',
    address: '深圳市, 南山区',
    status: '离职',
  },
])

const filters = reactive({ name: '', department: '' })
const selectedRows = ref([]),
  dataTable = ref()
const applied = reactive({ name: '', department: '' })

const filteredData = computed(() => {
  return tableList.value.filter((item) => {
    const matchName = !applied.name || item.name.includes(applied.name)
    const matchDept = !applied.department || item.department === applied.department
    return matchName && matchDept
  })
})

function handleFilter() {
  Object.assign(applied, filters)
}
watch(filteredData, () => {
  selectedRows.value = []
  dataTable.value?.clearSelection()
})
function resetFilter() {
  filters.name = ''
  filters.department = ''
  handleFilter()
}
function handleSelectionChange(val) {
  selectedRows.value = val
}

// 列定义
const columnsSchema = [
  { key: 'name', title: '姓名', validator: (v) => (!v ? '姓名不能为空' : null) },
  {
    key: 'department',
    title: '部门',
    validator: (v) =>
      !['技术研发部', '产品设计部', '市场运营部'].includes(v) ? '部门不存在' : null,
  },
  {
    key: 'email',
    title: '邮箱',
    validator: (v) => (!v || !v.includes('@') ? '邮箱格式无效' : null),
  },
  {
    key: 'phone',
    title: '手机号码',
    validator: (v) => (!/^\d{11}$/.test(v) ? '手机号必须为11位数字' : null),
  },
  {
    key: 'address',
    title: '通讯地址',
    validator: (v) => (!v ? '地址不能为空' : null),
  },
  {
    key: 'status',
    title: '在职状态',
    validator: (v) => (!['在职', '离职'].includes(v) ? '状态必须为在职或离职' : null),
  },
]

// 导出功能
function handleDownloadTemplate() {
  const templateData = [
    {
      name: '示例张三',
      department: '技术研发部',
      email: 'zhangsan@example.com',
      phone: '13812345678',
      address: '北京市, 海淀区, 中关村',
      status: '在职',
    },
  ]
  exportToCsv(templateData, columnsSchema, '人员导入标准模板')
  ElMessage.success('模板已开始下载')
}

function handleExportSelected() {
  if (!selectedRows.value.length) return
  exportToCsv(selectedRows.value, columnsSchema, '已选人员数据')
  ElMessage.success(`成功导出 ${selectedRows.value.length} 条记录`)
}

function handleExportAll() {
  if (!filteredData.value.length) return
  exportToCsv(filteredData.value, columnsSchema, '筛选人员数据')
  ElMessage.success(`成功导出 ${filteredData.value.length} 条记录`)
}

// 导入功能与校验
const importDialogVisible = ref(false)
const parseResult = ref(null)
const importing = ref(false),
  duplicateMode = ref('skip')

function openImportDialog() {
  parseResult.value = null
  importDialogVisible.value = true
}

function handleFileSelected(uploadFile) {
  const file = uploadFile.raw
  if (!file) return

  const reader = new FileReader()
  reader.onload = (e) => {
    try {
      const text = e.target.result
      parseResult.value = parseAndValidateCsv(text, columnsSchema)
      if (parseResult.value.failedRows.length > 0) {
        ElMessage.warning(`检测到 ${parseResult.value.failedRows.length} 条校验异常记录，请核对`)
      } else {
        ElMessage.success('校验全部通过！')
      }
    } catch (err) {
      ElMessage.error(err.message || '文件解析失败')
    }
  }
  reader.readAsText(file, 'utf-8')
}

function exportFailedRows() {
  if (!parseResult.value?.failedRows?.length) return
  const data = parseResult.value.failedRows.map((r) => ({
    ...r.raw,
    errorReason: r.errors.join('; '),
  }))
  exportToCsv(
    data,
    [...columnsSchema, { key: 'errorReason', title: '异常原因' }],
    '导入校验失败记录',
  )
}

async function confirmImport() {
  if (!parseResult.value?.validRows?.length || importing.value) return
  importing.value = true
  const incoming = parseResult.value.validRows.map((row) => ({ ...row }))
  try {
    await nextTick()
    const byEmail = new Map(tableList.value.map((row) => [row.email.toLowerCase(), row]))
    let added = 0,
      updated = 0,
      skipped = 0
    for (const row of incoming) {
      const email = row.email.toLowerCase()
      const existing = byEmail.get(email)
      if (existing) {
        if (duplicateMode.value === 'update') {
          Object.assign(existing, row)
          updated++
        } else skipped++
      } else {
        const item = { ...row, id: crypto.randomUUID() }
        tableList.value.unshift(item)
        byEmail.set(email, item)
        added++
      }
    }
    importDialogVisible.value = false
    ElMessage.success(`导入完成：新增 ${added} 条，更新 ${updated} 条，跳过 ${skipped} 条`)
  } finally {
    importing.value = false
  }
}
</script>

<style scoped>
.main-card {
  margin-top: 16px;
}
.table-actions-bar {
  flex-wrap: wrap;
  gap: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.stat-row {
  margin-top: 12px;
}
.stat-card {
  background: var(--el-fill-color-light);
  border-radius: 6px;
  padding: 12px;
  text-align: center;
  display: flex;
  flex-direction: column;
}
.stat-card .label {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}
.stat-card .val {
  font-size: 20px;
  font-weight: bold;
  margin-top: 4px;
}
.stat-card.success .val {
  color: var(--el-color-success);
}
.stat-card.danger .val {
  color: var(--el-color-danger);
}
.failed-list-box {
  margin-top: 16px;
}
.failed-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.failed-header .title {
  font-size: 13px;
  font-weight: 500;
  color: var(--el-color-danger);
}
.error-text {
  color: var(--el-color-danger);
}
.raw-text {
  color: var(--el-text-color-secondary);
}
</style>
