<template>
  <PageContainer
    title="系统配置"
    description="维护应用的公开基础资料。构建时品牌、模块开关和 API 地址在环境变量中配置。"
  >
    <el-card v-loading="loading" shadow="never">
      <el-alert
        v-if="error"
        :title="error"
        type="error"
        show-icon
        :closable="false"
        class="starter-gap"
      />
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
        class="starter-form"
        @submit.prevent="save"
      >
        <el-form-item label="应用名称" prop="siteName">
          <el-input v-model="form.siteName" />
        </el-form-item>
        <el-form-item label="应用介绍">
          <el-input v-model="form.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="联系邮箱" prop="contactEmail">
          <el-input v-model="form.contactEmail" placeholder="可选" />
        </el-form-item>
        <el-form-item label="备案信息">
          <el-input v-model="form.registration" placeholder="可选" />
        </el-form-item>
        <el-form-item>
          <el-button
            v-auth="'system:settings:update'"
            type="primary"
            native-type="submit"
            :loading="saving"
            :disabled="!!error"
          >
            保存配置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </PageContainer>
</template>
<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { settingsApi } from '@/api/system'
import { useUnsavedChanges } from '@/composables/useUnsavedChanges'
import PageContainer from '@/components/admin/PageContainer.vue'
const form = reactive({ siteName: '', description: '', contactEmail: '', registration: '' })
const formRef = ref(),
  loading = ref(true),
  saving = ref(false),
  error = ref('')
const initialForm = ref('')
useUnsavedChanges(computed(() => !!initialForm.value && JSON.stringify(form) !== initialForm.value))
const rules = {
  siteName: [{ required: true, message: '请输入应用名称', trigger: 'blur' }],
  contactEmail: [{ type: 'email', message: '请输入有效邮箱', trigger: 'blur' }],
}
async function save() {
  if (!(await formRef.value.validate().catch(() => false))) return
  saving.value = true
  try {
    await settingsApi.save({ ...form })
    initialForm.value = JSON.stringify(form)
    ElMessage.success('配置已保存')
  } catch (err) {
    ElMessage.error(err.message)
  } finally {
    saving.value = false
  }
}
onMounted(async () => {
  try {
    Object.assign(form, await settingsApi.get())
    initialForm.value = JSON.stringify(form)
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
})
</script>
