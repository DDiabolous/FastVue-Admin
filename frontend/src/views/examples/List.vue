<template>
  <PageContainer
    class="business-page example-page"
    title="基础列表"
    description="以项目管理为例，演示筛选、多视图、批量操作与详情联动。"
  >
    <template #actions>
      <ExampleGuide
        source="List.vue"
        :features="[
          'FilterPanel：多条件查询与重置',
          'TableToolbar / useTablePreferences：列显隐、密度、列宽',
          '项目列表与卡片共享数据，支持排序与分页',
          '状态预览：加载、空数据、错误与重试',
          'ProjectDetails：抽屉详情与操作记录',
        ]"
      />
    </template>
    <el-card shadow="never" class="data-card business-data-card">
      <FilterPanel :model="filters" @search="search">
        <el-form-item label="项目">
          <el-input v-model="filters.keyword" clearable placeholder="名称、编号或负责人" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filters.status" clearable placeholder="全部状态" style="width: 140px">
            <el-option
              v-for="(item, key) in projectStates"
              :key="key"
              :label="item.label"
              :value="key"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="分类">
          <el-select
            v-model="filters.category"
            clearable
            placeholder="全部分类"
            style="width: 140px"
          >
            <el-option v-for="item in projectTypes" :key="item" :value="item" :label="item" />
          </el-select>
        </el-form-item>
        <template #actions>
          <el-form-item class="form-btn-item">
            <el-button type="primary" native-type="submit" :icon="Search">查询</el-button>
            <el-button :icon="Refresh" @click="resetSearch">重置</el-button>
          </el-form-item>
        </template>
      </FilterPanel>
      <TableToolbar
        :selected="selected.length"
        :total="filtered.length"
        :columns="columns"
        v-model:visible-columns="visibleColumns"
        @reset-columns="table.resetColumns"
      >
        <el-button type="primary" :icon="Plus" @click="router.push('/examples/form')">
          新增项目
        </el-button>
        <el-button
          v-if="view === 'list'"
          type="danger"
          :icon="Delete"
          plain
          :disabled="!selected.length"
          @click="removeSelected"
        >
          删除
        </el-button>
        <template #tools>
          <el-dropdown trigger="click" @command="preview = $event">
            <el-tooltip content="状态预览" placement="top">
              <el-button circle :icon="View" aria-label="状态预览" />
            </el-tooltip>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="normal">正常</el-dropdown-item>
                <el-dropdown-item command="loading">加载中</el-dropdown-item>
                <el-dropdown-item command="empty">空数据</el-dropdown-item>
                <el-dropdown-item command="error">请求失败</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
          <el-radio-group v-model="view" aria-label="显示方式" class="view-mode-group">
            <el-radio-button value="list" aria-label="列表视图" title="列表视图">
              <el-icon><List /></el-icon>
            </el-radio-button>
            <el-radio-button value="cards" aria-label="卡片视图" title="卡片视图">
              <el-icon><Grid /></el-icon>
            </el-radio-button>
          </el-radio-group>
        </template>
      </TableToolbar>
      <TableEmpty
        v-if="preview !== 'normal'"
        :loading="preview === 'loading'"
        :error="preview === 'error' ? '演示错误' : ''"
        @retry="refresh"
      />
      <template v-else>
        <el-table
          v-if="view === 'list'"
          ref="tableRef"
          :data="pageRows"
          row-key="id"
          border
          @selection-change="selected = $event"
          @sort-change="sort = $event"
          @header-dragend="table.resize"
        >
          <el-table-column type="selection" width="48" align="center" />
          <el-table-column
            v-for="column in table.visibleColumns.value"
            :key="column.prop"
            v-bind="column"
            :sortable="column.prop === 'name' || column.prop === 'progress' ? 'custom' : false"
            show-overflow-tooltip
          >
            <template #default="{ row }">
              <el-progress v-if="column.prop === 'progress'" :percentage="row.progress" />
              <el-tag v-else-if="column.prop === 'status'" :type="projectStates[row.status].type">
                {{ projectStates[row.status].label }}
              </el-tag>
              <el-button
                v-else-if="column.prop === 'name'"
                link
                type="primary"
                @click="detailId = row.id"
              >
                {{ row.name }}
              </el-button>
              <span v-else>{{ row[column.prop] }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="130" fixed="right" align="center">
            <template #default="{ row }">
              <div class="table-op-btns">
                <el-button link type="primary" size="small" @click="detailId = row.id">详情</el-button>
                <el-button link type="primary" size="small" @click="edit(row)">编辑</el-button>
              </div>
            </template>
          </el-table-column>
          <template #empty><TableEmpty :filtered="hasFilters" @reset="resetSearch" /></template>
        </el-table>
        <div v-else-if="pageRows.length" class="entity-card-grid">
          <el-card
            v-for="project in pageRows"
            :key="project.id"
            shadow="never"
            class="entity-card project-card"
          >
            <div class="project-card-heading">
              <button class="project-name" :title="project.name" @click="detailId = project.id">
                {{ project.name }}
              </button>
              <el-tag v-if="visibleColumns.includes('status')" :type="projectStates[project.status].type">
                {{ projectStates[project.status].label }}
              </el-tag>
            </div>
            <div class="project-card-body">
              <dl>
                <div v-if="visibleColumns.includes('code')">
                  <dt>项目编号</dt>
                  <dd>{{ project.code }}</dd>
                </div>
                <div v-if="visibleColumns.includes('owner')">
                  <dt>负责人</dt>
                  <dd>{{ project.owner }}</dd>
                </div>
                <div v-if="visibleColumns.includes('category')">
                  <dt>分类</dt>
                  <dd>{{ project.category }}</dd>
                </div>
                <div>
                  <dt>计划结束</dt>
                  <dd>{{ project.dates[1] }}</dd>
                </div>
              </dl>
              <p class="project-summary" :title="project.description">
                {{ project.description || '未填写项目说明' }}
              </p>
              <el-progress v-if="visibleColumns.includes('progress')" :percentage="project.progress" />
            </div>
            <div class="project-card-footer">
              <el-button
                size="small"
                type="primary"
                plain
                :icon="View"
                @click="detailId = project.id"
              >
                详情
              </el-button>
              <el-button size="small" :icon="Edit" @click="edit(project)">编辑</el-button>
            </div>
          </el-card>
        </div>
        <TableEmpty v-else :filtered="hasFilters" @reset="resetSearch" />
        <el-pagination
          v-model:current-page="page"
          :total="filtered.length"
          :page-size="pageSize"
          layout="total, prev, pager, next"
          class="starter-pagination business-pagination"
        />
      </template>
    </el-card>
    <el-drawer
      class="business-overlay"
      :model-value="!!detailId"
      title="项目详情"
      size="min(560px, 100vw)"
      @update:model-value="!$event && (detailId = '')"
    >
      <ProjectDetails :project="currentProject" />
      <template #footer>
        <el-button @click="detailId = ''">关闭</el-button>
        <el-button
          type="primary"
          @click="router.push({ path: '/examples/details', query: { id: detailId } })"
        >
          完整详情
        </el-button>
      </template>
    </el-drawer>
  </PageContainer>
</template>
<script setup>
import { computed, ref, reactive, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search,
  Refresh,
  Plus,
  View,
  Edit,
  Delete,
  List,
  Grid,
} from '@element-plus/icons-vue'
import PageContainer from '@/components/admin/PageContainer.vue'
import FilterPanel from '@/components/admin/FilterPanel.vue'
import TableToolbar from '@/components/admin/TableToolbar.vue'
import TableEmpty from '@/components/admin/TableEmpty.vue'
import ExampleGuide from '@/components/examples/ExampleGuide.vue'
import ProjectDetails from '@/components/examples/ProjectDetails.vue'
import { useTablePreferences } from '@/composables/useTablePreferences'
import { useExampleProjects, projectTypes, projectStates } from '@/stores/exampleProjects'
const router = useRouter(),
  store = useExampleProjects()
const view = ref('list'),
  preview = ref('normal'),
  selected = ref([]),
  tableRef = ref(),
  detailId = ref('')
const sort = ref({}),
  pageSize = 6
const columns = [
  { prop: 'name', label: '项目名称', minWidth: 190, locked: true },
  { prop: 'code', label: '编号', minWidth: 120 },
  { prop: 'category', label: '分类', minWidth: 120 },
  { prop: 'owner', label: '负责人', minWidth: 100 },
  { prop: 'progress', label: '进度', minWidth: 150 },
  { prop: 'status', label: '状态', minWidth: 100, align: 'center' },
]
const table = useTablePreferences('example-projects', columns)
const { page, visible: visibleColumns } = table
const filters = reactive({ keyword: table.keyword.value, status: '', category: '' })
const applied = reactive({ ...filters, keyword: table.appliedKeyword.value })
const filtered = computed(() => {
  const keyword = applied.keyword.trim().toLowerCase()
  const result = store.projects.filter(
    (p) =>
      `${p.name} ${p.code} ${p.owner}`.toLowerCase().includes(keyword) &&
      (!applied.status || p.status === applied.status) &&
      (!applied.category || p.category === applied.category),
  )
  if (sort.value.order)
    result.sort((a, b) => {
      const key = sort.value.prop
      const comparison =
        key === 'progress' ? a.progress - b.progress : a.name.localeCompare(b.name, 'zh-CN')
      return sort.value.order === 'ascending' ? comparison : -comparison
    })
  return result
})
const pageRows = computed(() =>
  filtered.value.slice((page.value - 1) * pageSize, page.value * pageSize),
)
const hasFilters = computed(() => Object.values(applied).some(Boolean))
const currentProject = computed(() => store.projects.find((p) => p.id === detailId.value))
watch(
  () => filtered.value.length,
  (total) => {
    page.value = Math.min(page.value, Math.max(1, Math.ceil(total / pageSize)))
  },
  { immediate: true },
)
watch([pageRows, view, preview], async () => {
  selected.value = []
  await nextTick()
  tableRef.value?.clearSelection()
})
function search() {
  table.keyword.value = filters.keyword
  table.appliedKeyword.value = filters.keyword
  Object.assign(applied, filters)
  page.value = 1
  preview.value = 'normal'
}
function resetSearch() {
  Object.assign(filters, { keyword: '', status: '', category: '' })
  search()
}
function refresh() {
  preview.value = 'normal'
  selected.value = []
  tableRef.value?.clearSelection()
  ElMessage.success('示例数据已重新读取')
}
function edit(project) {
  router.push({ path: '/examples/form', query: { id: project.id } })
}
async function removeSelected() {
  const ids = selected.value.map((p) => p.id)
  try {
    await ElMessageBox.confirm(`确认删除 ${ids.length} 个项目？`, '删除项目', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
    })
  } catch {
    return
  }
  store.remove(ids)
  selected.value = []
  ElMessage.success('项目已删除')
}
</script>
<style scoped>
.project-card-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--border-light);
}
.project-card-heading .el-tag {
  flex-shrink: 0;
}
.project-name {
  min-width: 0;
  padding: 0;
  border: 0;
  background: none;
  color: var(--text-main);
  font-size: 14px;
  font-weight: 600;
  text-align: left;
  cursor: pointer;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}
.project-name:hover {
  color: var(--accent-foreground, var(--primary-color));
}
.project-card-body {
  flex: 1;
  padding: 12px 0 18px;
}
.project-summary {
  margin: 12px 0;
  color: var(--text-muted);
  font-size: 12px;
  line-height: 1.7;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  min-height: 40px;
}
dl {
  margin: 0;
}
dl > div {
  display: grid;
  grid-template-columns: 72px minmax(0, 1fr);
  gap: 8px;
  margin-top: 6px;
  line-height: 1.7;
  font-size: 12px;
}
dt {
  color: var(--text-regular);
}
dd {
  margin: 0;
  text-align: right;
  overflow-wrap: anywhere;
  color: var(--text-main);
  font-weight: 500;
}
.project-card-footer {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding-top: 10px;
  border-top: 1px solid var(--border-light);
}
.project-card-footer .el-button + .el-button {
  margin-left: 0;
}
</style>
