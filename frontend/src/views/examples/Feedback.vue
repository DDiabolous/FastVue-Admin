<template>
  <PageContainer
    class="business-page example-page"
    title="交互反馈"
    description="演示高风险操作确认、结果反馈、空状态和错误重试。"
  >
    <template #actions>
      <ExampleGuide
        source="Feedback.vue"
        scope="此页为本地交互演示，错误与权限状态可主动切换，不代表真实后端结果。"
        :features="[
          '二次确认与取消操作',
          '可恢复的失败状态和重试',
          '权限不足、空数据、提交成功的反馈',
        ]"
      />
    </template>
    <el-card shadow="never">
      <div class="feedback-toolbar">
        <el-radio-group v-model="state">
          <el-radio-button value="empty">空数据</el-radio-button>
          <el-radio-button value="error">请求失败</el-radio-button>
          <el-radio-button value="forbidden">无权限</el-radio-button>
          <el-radio-button value="success">成功</el-radio-button>
        </el-radio-group>
        <el-button type="danger" plain @click="confirmDelete">删除确认</el-button>
      </div>
      <TableEmpty v-if="state === 'empty'" />
      <TableEmpty v-else-if="state === 'error'" error="演示错误" @retry="retry" />
      <el-result
        v-else-if="state === 'forbidden'"
        icon="warning"
        title="暂无操作权限"
        sub-title="请联系管理员申请相应权限。"
      >
        <template #extra>
          <el-button @click="router.push('/dashboard')">返回工作台</el-button>
        </template>
      </el-result>
      <el-result v-else icon="success" title="操作成功" :sub-title="message">
        <template #extra>
          <el-button type="primary" @click="router.push('/examples/list')">查看项目列表</el-button>
        </template>
      </el-result>
    </el-card>
  </PageContainer>
</template>
<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import PageContainer from '@/components/admin/PageContainer.vue'
import TableEmpty from '@/components/admin/TableEmpty.vue'
import ExampleGuide from '@/components/examples/ExampleGuide.vue'
const router = useRouter(),
  state = ref('empty'),
  message = ref('本地交互演示已完成。')
function retry() {
  message.value = '重试成功，实际业务中可在此重新请求接口。'
  state.value = 'success'
}
async function confirmDelete() {
  try {
    await ElMessageBox.confirm('删除后无法恢复，是否继续？', '删除示例记录', {
      type: 'warning',
      confirmButtonText: '确认删除',
      cancelButtonText: '取消',
    })
  } catch {
    return
  }
  message.value = '示例记录已删除。此操作不影响项目列表。'
  state.value = 'success'
}
</script>
<style scoped>
.feedback-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
  margin-bottom: 24px;
}
.feedback-toolbar :deep(.el-radio-group) {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}
</style>
