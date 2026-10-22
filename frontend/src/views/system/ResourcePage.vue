<template>
  <PageContainer :title="schema.title" :description="schema.description">
    <el-card shadow="never" class="data-card">
      <el-form inline class="filter-panel" @submit.prevent="search">
        <el-form-item label="关键词">
          <el-input v-model="keyword" placeholder="输入关键词" clearable @clear="search" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" native-type="submit">查询</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
      <TableToolbar
        :loading="loading"
        :total="total"
        :columns="schema.columns"
        v-model:visible-columns="visibleColumns"
        @reset-columns="table.resetColumns"
        @refresh="load"
      >
        <el-button v-auth="permission('create')" type="primary" @click="openEditor()">
          <el-icon><Plus /></el-icon>
          新增
        </el-button>
      </TableToolbar>
      <el-alert
        v-if="error"
        :title="error"
        type="error"
        show-icon
        :closable="false"
        class="starter-gap"
      />
      <el-table
        border
        v-loading="loading"
        :data="rows"
        row-key="id"
        stripe
        @header-dragend="table.resize"
      >
        <el-table-column
          v-for="column in table.visibleColumns.value"
          :key="column.prop"
          v-bind="column"
          min-width="150"
          show-overflow-tooltip
        />
        <el-table-column label="状态" width="90">
          <template #default="{ row }"><StatusTag :value="row.status" /></template>
        </el-table-column>
        <el-table-column
          v-if="user.can(permission('update')) || user.can(permission('delete'))"
          label="操作"
          width="135"
          fixed="right"
        >
          <template #default="{ row }">
            <span v-if="isBuiltin(row)" class="starter-muted">内置</span>
            <template v-else>
              <el-button v-auth="permission('update')" link type="primary" @click="openEditor(row)">
                编辑
              </el-button>
              <el-button v-auth="permission('delete')" link type="danger" @click="remove(row)">
                删除
              </el-button>
            </template>
          </template>
        </el-table-column>
        <template #empty>
          <TableEmpty
            :loading="loading"
            :error="error"
            :filtered="!!appliedKeyword"
            @retry="load"
            @reset="resetSearch"
          />
        </template>
      </el-table>
      <el-pagination
        v-model:current-page="page"
        :page-size="10"
        :total="total"
        layout="total, prev, pager, next"
        class="starter-pagination"
        @current-change="load"
      />
    </el-card>
    <el-dialog
      v-model="visible"
      :title="`${editingId ? '编辑' : '新增'}${schema.title.replace('管理', '')}`"
      width="min(600px, 94vw)"
      destroy-on-close
      :before-close="beforeClose"
      :close-on-click-modal="false"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="96px" @submit.prevent="save">
        <el-form-item
          v-for="field in schema.fields"
          :key="field.prop"
          :label="field.label"
          :prop="field.prop"
        >
          <el-select v-if="field.type === 'role'" v-model="form[field.prop]" style="width: 100%">
            <el-option
              v-for="role in roles"
              :key="role.roleKey"
              :label="role.roleName"
              :value="role.roleKey"
            />
          </el-select>
          <el-select
            v-else-if="field.type === 'permissions'"
            v-model="form[field.prop]"
            multiple
            filterable
            collapse-tags
            style="width: 100%"
            placeholder="选择功能权限"
          >
            <el-option label="全部权限（管理员）" value="*" />
            <el-option v-for="option in permissionOptions" :key="option.value" v-bind="option" />
          </el-select>
          <el-input-number
            v-else-if="field.type === 'number'"
            v-model="form[field.prop]"
            :min="0"
          />
          <el-input
            v-else
            v-model="form[field.prop]"
            :type="field.type === 'email' ? 'text' : field.type || 'text'"
            :show-password="field.type === 'password'"
            :placeholder="
              field.type === 'password' && editingId ? '留空保留原密码' : `请输入${field.label}`
            "
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="form.status" :active-value="1" :inactive-value="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button :disabled="saving" @click="closeEditor">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </PageContainer>
</template>
<script setup>
import { computed, reactive, ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { resourceApi } from '@/api/system'
import { request } from '@/api/request'
import { resources } from '@/config/resources'
import { permissionOptions } from '@/config/permissions'
import { useUserStore } from '@/stores/user'
import PageContainer from '@/components/admin/PageContainer.vue'
import { useTablePreferences } from '@/composables/useTablePreferences'
import { useUnsavedChanges } from '@/composables/useUnsavedChanges'
import TableEmpty from '@/components/admin/TableEmpty.vue'
import TableToolbar from '@/components/admin/TableToolbar.vue'
import StatusTag from '@/components/admin/StatusTag.vue'
const props = defineProps({ resource: { type: String, required: true } })
const schema = resources[props.resource]
const api = resourceApi(props.resource)
const user = useUserStore()
const table = useTablePreferences(props.resource, schema.columns)
const { keyword, appliedKeyword, page, visible: visibleColumns } = table
const total = ref(0),
  rows = ref([]),
  roles = ref([])
const loading = ref(false),
  saving = ref(false),
  error = ref(''),
  visible = ref(false),
  editingId = ref(''),
  formRef = ref()
const form = reactive({})
const initialForm = ref('')
const dirty = computed(() => visible.value && JSON.stringify(form) !== initialForm.value)
const { confirmDiscard } = useUnsavedChanges(dirty)
async function closeEditor() {
  if (!saving.value && (await confirmDiscard())) visible.value = false
}
async function beforeClose(done) {
  if (!saving.value && (await confirmDiscard())) done()
}
const permission = (action) => `system:${props.resource}:${action}`
const isBuiltin = (row) =>
  (props.resource === 'users' && row.username === 'admin') ||
  (props.resource === 'roles' && row.roleKey === 'admin')
const rules = computed(() =>
  Object.fromEntries(
    schema.fields.map((field) => [
      field.prop,
      field.type === 'password'
        ? [
            {
              validator: (_, value, callback) =>
                callback(
                  (!editingId.value || value) && (!value || value.length < 8)
                    ? new Error('密码至少 8 位')
                    : undefined,
                ),
              trigger: 'blur',
            },
          ]
        : field.type === 'email'
          ? [{ type: 'email', message: '请输入有效邮箱', trigger: 'blur' }]
          : field.required
            ? [{ required: true, message: `请输入${field.label}`, trigger: 'blur' }]
            : [],
    ]),
  ),
)
async function load() {
  loading.value = true
  error.value = ''
  try {
    const result = await api.list({ keyword: appliedKeyword.value, page: page.value, pageSize: 10 })
    rows.value = result.list
    total.value = result.total
    if (!rows.value.length && page.value > 1) {
      page.value = Math.max(1, Math.ceil(result.total / 10))
      await load()
    }
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}
function search() {
  appliedKeyword.value = keyword.value.trim()
  page.value = 1
  load()
}
function resetSearch() {
  keyword.value = ''
  search()
}
async function openEditor(row) {
  if (props.resource === 'users') {
    try {
      // Assignable roles have a separate read contract; editors need no role-management permission.
      roles.value = await request('/auth/roles')
    } catch (err) {
      ElMessage.error(err.message)
      return
    }
  }
  editingId.value = row?.id || ''
  Object.keys(form).forEach((key) => delete form[key])
  Object.assign(
    form,
    structuredClone(schema.defaults),
    row ? JSON.parse(JSON.stringify(row)) : {},
    { password: '' },
  )
  initialForm.value = JSON.stringify(form)
  visible.value = true
}
async function save() {
  if (!(await formRef.value.validate().catch(() => false))) {
    document.querySelector('.el-dialog .is-error input')?.focus()
    return
  }
  saving.value = true
  try {
    const writable = [...schema.fields.map((field) => field.prop), 'status']
    const body = Object.fromEntries(writable.map((key) => [key, form[key]]))
    if (editingId.value && !body.password) delete body.password
    if (editingId.value) await api.update(editingId.value, body)
    else await api.create(body)
    initialForm.value = JSON.stringify(form)
    visible.value = false
    ElMessage.success('保存成功')
    await load()
    await user.fetchUser()
  } catch (err) {
    ElMessage.error(err.message)
  } finally {
    saving.value = false
  }
}
async function remove(row) {
  try {
    await ElMessageBox.confirm('删除后不可恢复，确定继续吗？', '删除记录', { type: 'warning' })
  } catch {
    return
  }
  try {
    await api.remove(row.id)
    ElMessage.success('删除成功')
    await load()
  } catch (err) {
    ElMessage.error(err.message)
  }
}
onMounted(load)
</script>
