<template>
  <PageContainer
    title="表单与详情"
    description="演示字段校验、选项、日期及提交后的详情展示。数据不提交到服务端。"
  >
    <el-row :gutter="20">
      <el-col :xs="24" :lg="14">
        <el-card shadow="never">
          <el-form
            ref="formRef"
            :model="form"
            :rules="rules"
            label-width="90px"
            @submit.prevent="submit"
          >
            <el-form-item label="名称" prop="name">
              <el-input v-model="form.name" placeholder="请输入名称" />
            </el-form-item>
            <el-form-item label="类型" prop="type">
              <el-select v-model="form.type">
                <el-option label="常规" value="常规" />
                <el-option label="其他" value="其他" />
              </el-select>
            </el-form-item>
            <el-form-item label="开始日期" prop="date">
              <el-date-picker
                v-model="form.date"
                value-format="YYYY-MM-DD"
                placeholder="选择日期"
              />
            </el-form-item>
            <el-form-item label="说明">
              <el-input v-model="form.description" type="textarea" :rows="4" />
            </el-form-item>
            <el-form-item label="启用"><el-switch v-model="form.enabled" /></el-form-item>
            <el-form-item>
              <el-button type="primary" native-type="submit">提交预览</el-button>
              <el-button @click="reset">重置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="10">
        <el-card shadow="never">
          <template #header>详情预览</template>
          <el-descriptions v-if="submitted" :column="1" border>
            <el-descriptions-item v-for="(label, key) in labels" :key="key" :label="label">
              {{ key === 'enabled' ? (submitted[key] ? '启用' : '停用') : submitted[key] || '—' }}
            </el-descriptions-item>
          </el-descriptions>
          <el-empty v-else description="提交表单后显示详情" />
        </el-card>
      </el-col>
    </el-row>
  </PageContainer>
</template>
<script setup>
import { reactive, ref } from 'vue'
import PageContainer from '@/components/admin/PageContainer.vue'
const defaults = { name: '', type: '', date: '', description: '', enabled: true }
const form = reactive({ ...defaults }),
  formRef = ref(),
  submitted = ref(null)
const labels = {
  name: '名称',
  type: '类型',
  date: '开始日期',
  description: '说明',
  enabled: '状态',
}
const rules = Object.fromEntries(
  ['name', 'type', 'date'].map((key) => [
    key,
    [{ required: true, message: `请填写${labels[key]}`, trigger: 'change' }],
  ]),
)
async function submit() {
  if (await formRef.value.validate().catch(() => false)) submitted.value = { ...form }
}
function reset() {
  Object.assign(form, defaults)
  submitted.value = null
  formRef.value.clearValidate()
}
</script>
