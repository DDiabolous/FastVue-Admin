<template>
  <PageContainer
    class="business-page example-page example-tree-page"
    title="树形列表"
    description="适用于分类、栏目、目录等层级数据。示例展示树形表格与可过滤目录。"
  >
    <template #actions>
      <ExampleGuide
        source="Tree.vue"
        scope="目录操作保存在当前页面内存中，刷新后恢复初始数据。拖拽排序不调用后端。"
        :features="[
          '目录搜索与节点定位',
          '树与表格共享数据',
          '新增、编辑、父级调整与删除确认',
          '拖拽排序、展开与收起',
        ]"
      />
    </template>
    <el-row :gutter="20">
      <el-col :xs="24" :lg="8">
        <el-card shadow="never" class="tree-card">
          <template #header>
            <div class="card-header flex-between">
              <span class="card-title">项目目录</span>
              <el-button link type="primary" @click="editNode()">新增目录</el-button>
            </div>
          </template>
          <el-input v-model="keyword" placeholder="筛选目录" clearable class="starter-gap" />
          <el-tree
            ref="tree"
            :data="data"
            node-key="id"
            default-expand-all
            draggable
            @node-drop="ElMessage.success('目录顺序已更新')"
            @node-click="selectNode"
            :filter-node-method="filter"
            :props="{ label: 'name' }"
          />
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="16">
        <el-card shadow="never" class="tree-card">
          <template #header>
            <div class="card-header flex-between">
              <span class="card-title">树形表格</span>
              <el-button size="small" :icon="Sort" @click="toggleTableExpand">
                {{ isTableExpanded ? '折叠全部' : '展开全部' }}
              </el-button>
            </div>
          </template>
          <el-table
            border
            ref="treeTableRef"
            :data="data"
            row-key="id"
            :default-expand-all="isTableExpanded"
            stripe
            highlight-current-row
            style="width: 100%"
          >
            <el-table-column prop="name" label="名称" min-width="220">
              <template #default="{ row }">
                <div class="tree-name-cell">
                  <el-icon class="tree-node-icon">
                    <FolderOpened v-if="row.children && row.children.length" />
                    <Document v-else />
                  </el-icon>
                  <span class="tree-title-text">{{ row.name }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="key" label="标识" min-width="150">
              <template #default="{ row }">
                <el-tag size="small" type="info" effect="plain" class="tree-key-tag">
                  {{ row.key }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="状态" width="100" align="center">
              <template #default="{ row }"><StatusTag :value="row.status" /></template>
            </el-table-column>
            <el-table-column label="操作" width="170" fixed="right" align="center">
              <template #default="{ row }">
                <div class="table-op-btns">
                  <el-button link type="primary" size="small" @click="editNode(null, row.id)">新增</el-button>
                  <el-button link type="primary" size="small" @click="editNode(row)">编辑</el-button>
                  <el-button link type="danger" size="small" @click="removeNode(row)">删除</el-button>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
    <el-dialog
      class="business-overlay"
      v-model="editorVisible"
      :title="editor.id ? '编辑目录' : '新增目录'"
      width="min(480px, 94vw)"
    >
      <el-form ref="editorRef" :model="editor" label-position="top" @submit.prevent="saveNode">
        <el-form-item
          label="名称"
          prop="name"
          :rules="[{ required: true, whitespace: true, message: '请输入名称' }]"
        >
          <el-input v-model="editor.name" maxlength="80" />
        </el-form-item>
        <el-form-item
          label="标识"
          prop="key"
          :rules="[
            { required: true, message: '请输入唯一标识' },
            { pattern: /^[A-Za-z0-9_-]+$/, message: '仅支持字母、数字、下划线与连字符' },
          ]"
        >
          <el-input v-model="editor.key" maxlength="50" />
        </el-form-item>
        <el-form-item label="父级目录">
          <el-tree-select
            v-model="editor.parentId"
            :data="parentOptions"
            :props="{ label: 'name', value: 'id' }"
            check-strictly
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="editor.status" :active-value="1" :inactive-value="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editorVisible = false">取消</el-button>
        <el-button type="primary" @click="saveNode">保存</el-button>
      </template>
    </el-dialog>
  </PageContainer>
</template>

<script setup>
import { ref, watch, reactive, computed, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import ExampleGuide from '@/components/examples/ExampleGuide.vue'
import { FolderOpened, Document, Sort } from '@element-plus/icons-vue'
import PageContainer from '@/components/admin/PageContainer.vue'
import StatusTag from '@/components/admin/StatusTag.vue'

const keyword = ref('')
const tree = ref()
const treeTableRef = ref(null)
const isTableExpanded = ref(true)

const toggleRowExpansionAll = (nodes, expanded) => {
  if (!treeTableRef.value || !nodes) return
  nodes.forEach((node) => {
    treeTableRef.value.toggleRowExpansion(node, expanded)
    if (node.children && node.children.length > 0) {
      toggleRowExpansionAll(node.children, expanded)
    }
  })
}

const toggleTableExpand = () => {
  isTableExpanded.value = !isTableExpanded.value
  toggleRowExpansionAll(data, isTableExpanded.value)
}

const data = reactive([
  {
    id: 1,
    name: '示例目录',
    key: 'root',
    status: 1,
    children: [
      {
        id: 2,
        name: '基础分类',
        key: 'basic',
        status: 1,
        children: [{ id: 3, name: '子分类', key: 'child', status: 1 }],
      },
      { id: 4, name: '归档分类', key: 'archive', status: 0 },
    ],
  },
])
const filter = (value, node) => !value || node.name.includes(value)
watch(keyword, (value) => tree.value?.filter(value))

const editorVisible = ref(false),
  editorRef = ref()
const editor = reactive({ id: null, name: '', key: '', status: 1, parentId: 0 })
function findNode(id, nodes = data, parentId = 0) {
  for (const node of nodes) {
    if (node.id === id) return { node, siblings: nodes, parentId }
    const found = findNode(id, node.children || [], node.id)
    if (found) return found
  }
}
function descendants(node) {
  return [node.id, ...(node.children || []).flatMap(descendants)]
}
const parentOptions = computed(() => {
  const current = editor.id ? findNode(editor.id)?.node : null
  const excluded = new Set(current ? descendants(current) : [])
  const copy = (nodes) =>
    nodes.map((node) => ({
      id: node.id,
      name: node.name,
      disabled: excluded.has(node.id),
      children: copy(node.children || []),
    }))
  return [{ id: 0, name: '根目录', children: copy(data) }]
})
function editNode(row, parentId = 0) {
  Object.assign(
    editor,
    { id: null, name: '', key: '', status: 1, parentId },
    row
      ? {
          id: row.id,
          name: row.name,
          key: row.key,
          status: row.status,
          parentId: findNode(row.id).parentId,
        }
      : {},
  )
  editorVisible.value = true
  nextTick(() => editorRef.value?.clearValidate())
}
function selectNode(row) {
  treeTableRef.value?.setCurrentRow(row)
}
async function saveNode() {
  if (!(await editorRef.value.validate().catch(() => false))) return
  const flatten = (nodes) => nodes.flatMap((node) => [node, ...flatten(node.children || [])])
  if (flatten(data).some((node) => node.key === editor.key && node.id !== editor.id)) {
    ElMessage.error('标识已存在')
    return
  }
  const current = editor.id ? findNode(editor.id) : null
  if (current && descendants(current.node).includes(editor.parentId)) {
    ElMessage.error('父级不能是当前目录或其子目录')
    return
  }
  const parent = editor.parentId ? findNode(editor.parentId)?.node : null
  if (editor.parentId && !parent) {
    ElMessage.error('父级目录不存在')
    return
  }
  const node = current?.node || { id: crypto.randomUUID() }
  if (current) current.siblings.splice(current.siblings.indexOf(node), 1)
  Object.assign(node, { name: editor.name.trim(), key: editor.key, status: editor.status })
  if (parent) (parent.children ||= []).push(node)
  else data.push(node)
  editorVisible.value = false
  await nextTick()
  tree.value?.filter(keyword.value)
  ElMessage.success('目录已保存')
}
async function removeNode(row) {
  try {
    await ElMessageBox.confirm(
      `确认删除“${row.name}”及其 ${descendants(row).length - 1} 个子目录？`,
      '删除目录',
      { type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消' },
    )
  } catch {
    return
  }
  const found = findNode(row.id)
  found.siblings.splice(found.siblings.indexOf(found.node), 1)
  ElMessage.success('目录已删除')
}
</script>

<style scoped>
.example-tree-page {
  --tree-line-color: #cbd5e1;
  --tree-expand-bg: rgba(0, 0, 0, 0.04);
  --tree-expand-border: rgba(0, 0, 0, 0.06);
}

:global(html.dark .example-tree-page) {
  --tree-line-color: #334155;
  --tree-expand-bg: rgba(255, 255, 255, 0.08);
  --tree-expand-border: rgba(255, 255, 255, 0.12);
}

.tree-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
}

.flex-between {
  justify-content: space-between;
}

.card-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-main);
}

/* 树形表格首列 flex 居中单行对齐，彻底消除换行与多余高度 */
:deep(.el-table .el-table__body td:first-child .cell) {
  display: flex !important;
  align-items: center !important;
  overflow: visible !important;
  white-space: nowrap !important;
  position: relative;
}

/* 缩进容器 */
:deep(.el-table__indent) {
  display: inline-flex !important;
  align-items: center;
  position: relative;
  flex-shrink: 0;
  order: 1;
  height: 100%;
}

/* 阶梯缩进 */
:deep(tr.el-table__row--level-1 .el-table__indent) {
  padding-left: 24px !important;
}
:deep(tr.el-table__row--level-2 .el-table__indent) {
  padding-left: 48px !important;
}

/* Level 1 树形连接分支线（L-shape 折线） */
:deep(tr.el-table__row--level-1 .el-table__indent::before) {
  content: '';
  position: absolute;
  left: 10px;
  top: -24px;
  bottom: 50%;
  width: 1px;
  border-left: 1.5px dashed var(--tree-line-color);
}
:deep(tr.el-table__row--level-1 .el-table__indent::after) {
  content: '';
  position: absolute;
  left: 10px;
  top: 50%;
  width: 12px;
  height: 1px;
  border-bottom: 1.5px dashed var(--tree-line-color);
}

/* Level 2 树形连接线（祖父级垂直贯通虚线 + 本级分支折线） */
:deep(tr.el-table__row--level-2 .el-table__indent) {
  background-image: linear-gradient(to bottom, var(--tree-line-color) 50%, transparent 50%);
  background-size: 1.5px 6px;
  background-repeat: repeat-y;
  background-position: 10px 0;
}
:deep(tr.el-table__row--level-2 .el-table__indent::before) {
  content: '';
  position: absolute;
  left: 34px;
  top: -24px;
  bottom: 50%;
  width: 1px;
  border-left: 1.5px dashed var(--tree-line-color);
}
:deep(tr.el-table__row--level-2 .el-table__indent::after) {
  content: '';
  position: absolute;
  left: 34px;
  top: 50%;
  width: 12px;
  height: 1px;
  border-bottom: 1.5px dashed var(--tree-line-color);
}

/* 将 tree-name-cell 内部子元素解包至外部 flex 流参与 order 排序 */
.tree-name-cell {
  display: contents !important;
}

.tree-name-cell :deep(.el-icon),
.tree-name-cell > .el-icon {
  order: 2 !important;
  margin-right: 7px !important;
  flex-shrink: 0;
}

.tree-title-text {
  order: 3 !important;
  margin-right: 6px !important;
  flex-shrink: 0;
}

/* 树形子行展开平滑淡入滑下动画（避免收起时 table-row 重排撕裂闪烁） */
@keyframes treeRowEnter {
  0% {
    opacity: 0;
    transform: translateY(-6px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

:deep(tr.el-table__row--level-1:not([style*='display: none'])),
:deep(tr.el-table__row--level-2:not([style*='display: none'])) {
  animation: treeRowEnter 0.22s cubic-bezier(0.16, 1, 0.3, 1) both;
}

/* 展开箭头紧随标题右侧 */
:deep(.el-table__expand-icon) {
  order: 4 !important;
  margin: 0 8px 0 0 !important;
  padding: 0 !important;
  width: 18px !important;
  height: 18px !important;
  min-width: 18px !important;
  display: inline-flex !important;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  color: var(--text-muted, #94a3b8);
  background: var(--tree-expand-bg);
  border: 1px solid var(--tree-expand-border);
  cursor: pointer;
  transition:
    transform 0.24s cubic-bezier(0.34, 1.56, 0.64, 1),
    background-color 0.2s ease,
    border-color 0.2s ease,
    color 0.2s ease !important;
}
:deep(.el-table__expand-icon--expanded) {
  transform: rotate(90deg) !important;
}
:deep(.el-table__expand-icon:hover) {
  color: var(--primary-color, #2563eb);
  background: rgba(37, 99, 235, 0.12);
  border-color: rgba(37, 99, 235, 0.25);
}
:deep(.el-table__expand-icon .el-icon) {
  font-size: 11px !important;
}

/* 无子级占位符隐藏，不占用标题右侧空间 */
:deep(.el-table__placeholder) {
  display: none !important;
}

.tree-key-tag {
  font-size: 10px;
  height: 20px;
  line-height: 18px;
}

/* 层级差异化字体与图标 */
:deep(tr.el-table__row--level-0 .tree-title-text) {
  font-size: 13.5px !important;
  font-weight: 600 !important;
  color: var(--text-main) !important;
}
:deep(tr.el-table__row--level-0 .tree-name-cell .el-icon) {
  font-size: 16px;
  color: var(--primary-color) !important;
}

:deep(tr.el-table__row--level-1 .tree-title-text) {
  font-size: 13px !important;
  font-weight: 500 !important;
  color: var(--text-main) !important;
}
:deep(tr.el-table__row--level-1 .tree-name-cell .el-icon) {
  font-size: 14.5px;
  color: #0284c7 !important;
}

:deep(tr.el-table__row--level-2 .tree-title-text) {
  font-size: 12.5px !important;
  font-weight: 450 !important;
  color: var(--text-regular) !important;
}
:deep(tr.el-table__row--level-2 .tree-name-cell .el-icon) {
  font-size: 13.5px;
  color: #64748b !important;
}

:global(html.dark .example-tree-page tr.el-table__row--level-0 .tree-title-text) {
  color: #f1f5f9 !important;
}
:global(html.dark .example-tree-page tr.el-table__row--level-0 .tree-name-cell .el-icon) {
  color: #60a5fa !important;
}
:global(html.dark .example-tree-page tr.el-table__row--level-1 .tree-title-text) {
  color: #e2e8f0 !important;
}
:global(html.dark .example-tree-page tr.el-table__row--level-1 .tree-name-cell .el-icon) {
  color: #38bdf8 !important;
}
:global(html.dark .example-tree-page tr.el-table__row--level-2 .tree-title-text) {
  color: #94a3b8 !important;
}
:global(html.dark .example-tree-page tr.el-table__row--level-2 .tree-name-cell .el-icon) {
  color: #64748b !important;
}
:global(html.dark .example-tree-page .el-table__expand-icon:hover) {
  color: #60a5fa;
  background: rgba(96, 165, 250, 0.15);
  border-color: rgba(96, 165, 250, 0.3);
}
</style>
