<template>
  <PageContainer
    :title="category === 'login' ? '登录日志' : '操作日志'"
    description="演示模式只记录当前浏览器产生的事件；接入后端后由服务端记录真实审计信息。"
  >
    <el-card shadow="never" class="data-card">
      <el-form inline class="filter-panel" @submit.prevent="search">
        <el-form-item label="关键词">
          <el-input v-model="keyword" clearable placeholder="操作人、动作或目标" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" native-type="submit">查询</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
      <TableToolbar
        :loading="loading"
        :total="total"
        :columns="columns"
        v-model:visible-columns="visibleColumns"
        @reset-columns="table.resetColumns"
        @refresh="load"
      />
      <el-alert v-if="error" :title="error" type="error" :closable="false" />
      <el-table border v-loading="loading" :data="rows" stripe @header-dragend="table.resize">
        <el-table-column
          v-for="column in table.visibleColumns.value"
          :key="column.prop"
          v-bind="column"
          :min-width="column.minWidth || 150"
          show-overflow-tooltip
        />
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
        :total="total"
        :page-size="10"
        layout="total, prev, pager, next"
        class="starter-pagination"
        @current-change="load"
      />
    </el-card>
  </PageContainer>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { resourceApi } from '@/api/admin'
import PageContainer from '@/components/admin/PageContainer.vue'
import { useTablePreferences } from '@/composables/useTablePreferences'
import TableEmpty from '@/components/admin/TableEmpty.vue'
import TableToolbar from '@/components/admin/TableToolbar.vue'
const props = defineProps({ category: String })
const columns = [
  { prop: 'time', label: '时间', minWidth: 185 },
  { prop: 'operator', label: '操作人' },
  { prop: 'action', label: '动作' },
  { prop: 'target', label: '目标' },
  { prop: 'ip', label: 'IP' },
]
const table = useTablePreferences(`logs-${props.category}`, columns)
const { keyword, appliedKeyword, page, visible: visibleColumns } = table
const rows = ref([]),
  total = ref(0),
  loading = ref(false),
  error = ref('')
async function load() {
  loading.value = true
  error.value = ''
  try {
    const data = await resourceApi('logs').list({
      category: props.category,
      keyword: appliedKeyword.value,
      page: page.value,
      pageSize: 10,
    })
    rows.value = data.list
    total.value = data.total
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}
function resetSearch() {
  keyword.value = ''
  search()
}
function search() {
  appliedKeyword.value = keyword.value.trim()
  page.value = 1
  load()
}
onMounted(load)
</script>
