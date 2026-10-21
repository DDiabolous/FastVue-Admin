<template>
  <PageContainer
    title="基础列表"
    description="演示搜索、分页、选择、批量操作及编辑弹窗。示例数据只在当前页面内存中保存。"
  >
    <el-card shadow="never" class="data-card">
      <el-form inline class="filter-panel" @submit.prevent="search">
        <el-form-item label="关键词">
          <el-input v-model="keyword" clearable placeholder="名称或分类" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" native-type="submit">查询</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
      <TableToolbar
        :selected="selected.length"
        :total="filtered.length"
        :columns="columns"
        v-model:visible-columns="visibleColumns"
        @reset-columns="table.resetColumns"
        @refresh="refresh"
      >
        <el-button type="primary" @click="edit()">新增</el-button>
        <el-button type="danger" plain :disabled="!selected.length" @click="removeSelected">
          批量删除
        </el-button>
      </TableToolbar>
      <el-table
        border
        ref="tableRef"
        :data="pageRows"
        row-key="id"
        @selection-change="selected = $event"
        @header-dragend="table.resize"
      >
        <el-table-column type="selection" width="48" />
        <el-table-column
          v-for="column in table.visibleColumns.value"
          :key="column.prop"
          v-bind="column"
          min-width="180"
        />
        <el-table-column label="状态" width="110">
          <template #default="{ row }"><StatusTag :value="row.status" /></template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button link type="primary" @click="edit(row)">编辑</el-button>
          </template>
        </el-table-column>
        <template #empty><TableEmpty :filtered="!!appliedKeyword" @reset="resetSearch" /></template>
      </el-table>
      <el-pagination
        v-model:current-page="page"
        :total="filtered.length"
        :page-size="5"
        layout="total, prev, pager, next"
        class="starter-pagination"
      />
    </el-card>
    <el-dialog
      v-model="visible"
      :title="form.id ? '编辑记录' : '新增记录'"
      width="min(480px, 94vw)"
    >
      <el-form ref="formRef" :model="form" label-width="70px">
        <el-form-item label="名称" prop="name" :rules="[{ required: true, message: '请输入名称' }]">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="form.category">
            <el-option label="常规" value="常规" />
            <el-option label="演示" value="演示" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="form.status" :active-value="1" :inactive-value="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="visible = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </PageContainer>
</template>
<script setup>
import { computed, ref, reactive } from 'vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import PageContainer from '@/components/admin/PageContainer.vue'
import { useTablePreferences } from '@/composables/useTablePreferences'
import TableEmpty from '@/components/admin/TableEmpty.vue'
import TableToolbar from '@/components/admin/TableToolbar.vue'
import StatusTag from '@/components/admin/StatusTag.vue'
const rows = ref(
  Array.from({ length: 12 }, (_, i) => ({
    id: i + 1,
    name: `示例记录 ${String(i + 1).padStart(2, '0')}`,
    category: i % 2 ? '演示' : '常规',
    status: i % 4 ? 1 : 0,
  })),
)
const columns = [
  { prop: 'name', label: '名称' },
  { prop: 'category', label: '分类' },
]
const table = useTablePreferences('example-list', columns)
const { keyword, appliedKeyword, page, visible: visibleColumns } = table
const selected = ref([]),
  visible = ref(false),
  formRef = ref(),
  tableRef = ref()
const form = reactive({})
const filtered = computed(() =>
  rows.value.filter((row) => `${row.name}${row.category}`.includes(appliedKeyword.value)),
)
const pageRows = computed(() => filtered.value.slice((page.value - 1) * 5, page.value * 5))
function resetSearch() {
  keyword.value = ''
  search()
}
function search() {
  appliedKeyword.value = keyword.value
  page.value = 1
}
function refresh() {
  tableRef.value?.clearSelection()
  ElMessage.success('列表已刷新')
}
function edit(row) {
  Object.assign(form, { id: null, name: '', category: '常规', status: 1 }, row || {})
  visible.value = true
}
async function save() {
  if (!(await formRef.value.validate().catch(() => false))) return
  if (form.id)
    Object.assign(
      rows.value.find((row) => row.id === form.id),
      form,
    )
  else rows.value.unshift({ ...form, id: Date.now() })
  visible.value = false
  search()
}
async function removeSelected() {
  try {
    await ElMessageBox.confirm(`确认删除选中的 ${selected.value.length} 条记录？`, '批量删除', {
      type: 'warning',
    })
  } catch {
    return
  }
  const ids = new Set(selected.value.map((row) => row.id))
  rows.value = rows.value.filter((row) => !ids.has(row.id))
  selected.value = []
  page.value = Math.min(page.value, Math.max(1, Math.ceil(filtered.value.length / 5)))
}
</script>
