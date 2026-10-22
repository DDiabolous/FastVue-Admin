<template>
  <PageContainer
    class="business-page example-page"
    title="表单与详情"
    description="通过分步表单创建项目，演示字段联动、唯一性校验与未保存提醒。"
  >
    <template #actions>
      <ExampleGuide
        source="Form.vue"
        :features="[
          '分步表单与分组布局',
          '分类与负责人联动、编号唯一性校验',
          '日期范围、预算、进度与多行说明',
          'useUnsavedChanges：离开前确认',
          '提交后关联列表、卡片与完整详情',
        ]"
      />
    </template>
    <el-card shadow="never" class="project-form-card">
      <el-result
        v-if="savedId"
        icon="success"
        title="项目已保存"
        sub-title="可在列表、卡片和详情中查看本次修改。刷新页面后，示例数据恢复初始状态。"
      >
        <template #extra>
          <el-button @click="router.push('/examples/list')">返回列表</el-button>
          <el-button
            type="primary"
            @click="router.push({ path: '/examples/details', query: { id: savedId } })"
          >
            查看详情
          </el-button>
        </template>
      </el-result>
      <el-empty v-else-if="missing" description="项目不存在或已删除">
        <el-button @click="router.push('/examples/list')">返回列表</el-button>
      </el-empty>
      <template v-else>
        <el-steps :active="step" finish-status="success" simple>
          <el-step title="基本信息" />
          <el-step title="计划安排" />
          <el-step title="确认提交" />
        </el-steps>
        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          label-position="top"
          :disabled="submitting"
          class="project-form"
          @submit.prevent="step < 2 ? next() : submit()"
        >
          <section v-show="step === 0">
            <h2>基本信息</h2>
            <p>填写名称、编号并选择负责团队。</p>
            <div class="form-grid">
              <el-form-item label="项目名称" prop="name">
                <el-input v-model="form.name" maxlength="80" placeholder="请输入项目名称" />
              </el-form-item>
              <el-form-item label="项目编号" prop="code">
                <el-input v-model="form.code" maxlength="32" placeholder="如 PRJ-013" />
                <span class="field-help">编号须唯一，支持字母、数字和连字符。</span>
              </el-form-item>
              <el-form-item label="分类" prop="category">
                <el-select v-model="form.category" @change="categoryChanged">
                  <el-option v-for="type in projectTypes" :key="type" :label="type" :value="type" />
                </el-select>
              </el-form-item>
              <el-form-item label="负责人" prop="owner">
                <el-select v-model="form.owner" :disabled="!form.category" placeholder="先选择分类">
                  <el-option v-for="owner in owners" :key="owner" :label="owner" :value="owner" />
                </el-select>
              </el-form-item>
            </div>
            <el-form-item label="项目说明" prop="description">
              <el-input
                v-model="form.description"
                type="textarea"
                :rows="4"
                maxlength="500"
                show-word-limit
                placeholder="目标、交付内容与协作安排"
              />
            </el-form-item>
          </section>
          <section v-show="step === 1">
            <h2>计划安排</h2>
            <p>设置项目周期、预算和当前进度。</p>
            <div class="form-grid">
              <el-form-item label="计划周期" prop="dates" class="wide">
                <el-date-picker
                  v-model="form.dates"
                  type="daterange"
                  value-format="YYYY-MM-DD"
                  start-placeholder="开始日期"
                  end-placeholder="结束日期"
                  range-separator="至"
                />
              </el-form-item>
              <el-form-item label="预算（元）" prop="budget">
                <el-input-number
                  v-model="form.budget"
                  :min="0"
                  :max="100000000"
                  :precision="2"
                  controls-position="right"
                />
              </el-form-item>
              <el-form-item label="状态" prop="status">
                <el-select v-model="form.status" @change="statusChanged">
                  <el-option
                    v-for="(item, key) in projectStates"
                    :key="key"
                    :label="item.label"
                    :value="key"
                  />
                </el-select>
              </el-form-item>
              <el-form-item label="进度" class="wide">
                <el-slider
                  v-model="form.progress"
                  :disabled="form.status !== 'active'"
                  show-input
                  :min="0"
                  :max="100"
                  @change="form.progress === 100 && (form.status = 'completed')"
                />
              </el-form-item>
            </div>
            <el-alert
              title="待启动项目进度为 0%，已完成项目进度为 100%。"
              type="info"
              :closable="false"
            />
          </section>
          <section v-if="step === 2">
            <h2>确认信息</h2>
            <p>检查填写内容，提交后可继续编辑。</p>
            <el-descriptions :column="1" border>
              <el-descriptions-item label="项目">
                {{ form.name }} · {{ form.code }}
              </el-descriptions-item>
              <el-descriptions-item label="分类 / 负责人">
                {{ form.category }} / {{ form.owner }}
              </el-descriptions-item>
              <el-descriptions-item label="计划周期">
                {{ form.dates?.join(' 至 ') }}
              </el-descriptions-item>
              <el-descriptions-item label="预算">
                ¥ {{ form.budget?.toLocaleString() }}
              </el-descriptions-item>
              <el-descriptions-item label="状态">
                {{ projectStates[form.status].label }} · {{ form.progress }}%
              </el-descriptions-item>
              <el-descriptions-item label="说明">
                {{ form.description || '未填写' }}
              </el-descriptions-item>
            </el-descriptions>
          </section>
          <div class="project-form-footer">
            <el-button @click="reset">重置</el-button>
            <div>
              <el-button v-if="step > 0" @click="step--">上一步</el-button>
              <el-button v-if="step < 2" type="primary" native-type="submit">下一步</el-button>
              <el-button v-else type="primary" native-type="submit" :loading="submitting">
                保存项目
              </el-button>
            </div>
          </div>
        </el-form>
      </template>
    </el-card>
  </PageContainer>
</template>
<script setup>
import { computed, reactive, ref, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import PageContainer from '@/components/admin/PageContainer.vue'
import ExampleGuide from '@/components/examples/ExampleGuide.vue'
import { useUnsavedChanges } from '@/composables/useUnsavedChanges'
import {
  useExampleProjects,
  projectStates,
  projectTypes,
  projectTeams,
} from '@/stores/exampleProjects'
const route = useRoute(),
  router = useRouter(),
  store = useExampleProjects()
const existing = store.projects.find((p) => p.id === route.query.id)
const missing = !!route.query.id && !existing
const defaults = {
  id: existing?.id || '',
  name: existing?.name || '',
  code: existing?.code || '',
  category: existing?.category || '',
  owner: existing?.owner || '',
  dates: [...(existing?.dates || [])],
  budget: existing?.budget || 0,
  status: existing?.status || 'planned',
  progress: existing?.progress || 0,
  description: existing?.description || '',
}
const form = reactive({ ...defaults, dates: [...defaults.dates] }),
  formRef = ref(),
  step = ref(0),
  savedId = ref(''),
  submitting = ref(false)
const baseline = ref(JSON.stringify(form))
const { confirmDiscard } = useUnsavedChanges(
  computed(() => JSON.stringify(form) !== baseline.value),
)
const owners = computed(() => projectTeams[form.category] || [])
const required = (message) => [{ required: true, message, trigger: 'change' }]
const rules = {
  name: [{ required: true, whitespace: true, message: '请输入项目名称', trigger: 'blur' }],
  code: [
    { required: true, message: '请输入编号', trigger: 'blur' },
    { pattern: /^[A-Za-z0-9-]+$/, message: '仅支持字母、数字和连字符', trigger: 'blur' },
    {
      async validator(_, value) {
        await Promise.resolve()
        if (store.projects.some((p) => p.code === value && p.id !== form.id))
          throw new Error('编号已存在，请使用其他编号')
      },
      trigger: 'blur',
    },
  ],
  category: required('请选择分类'),
  owner: required('请选择负责人'),
  dates: [
    { type: 'array', required: true, len: 2, message: '请选择完整的计划周期', trigger: 'change' },
  ],
  budget: [
    {
      type: 'number',
      required: true,
      min: 0,
      max: 100000000,
      message: '请输入有效预算',
      trigger: 'change',
    },
  ],
}
function categoryChanged() {
  if (!owners.value.includes(form.owner)) form.owner = ''
}
function statusChanged() {
  form.progress =
    form.status === 'completed' ? 100 : form.status === 'planned' ? 0 : Math.min(form.progress, 99)
}
async function next() {
  const fields = step.value === 0 ? ['name', 'code', 'category', 'owner'] : ['dates', 'budget']
  if (
    await formRef.value
      .validateField(fields)
      .then(() => true)
      .catch(() => false)
  )
    step.value++
}
async function submit() {
  if (submitting.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) {
    step.value = 0
    return
  }
  submitting.value = true
  try {
    await nextTick()
    const project = store.save({ ...form, name: form.name.trim() })
    baseline.value = JSON.stringify(form)
    savedId.value = project.id
    ElMessage.success('项目已保存')
  } catch (error) {
    ElMessage.error(error.message)
  } finally {
    submitting.value = false
  }
}
async function reset() {
  if (!(await confirmDiscard())) return
  Object.assign(form, defaults, { dates: [...defaults.dates] })
  step.value = 0
  formRef.value?.clearValidate()
}
</script>
<style scoped>
.project-form-card {
  max-width: none;
}
.project-form {
  max-width: 880px;
  margin: 32px auto 0;
}
.project-form h2 {
  font-size: 18px;
  margin: 0 0 8px;
}
.project-form p {
  color: var(--text-muted);
  font-size: 13px;
  margin-bottom: 28px;
}
.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0 24px;
}
.form-grid > * {
  min-width: 0;
}
.form-grid .wide {
  grid-column: 1 / -1;
}
.project-form :deep(.el-select),
.project-form :deep(.el-input-number),
.project-form :deep(.el-date-editor) {
  width: 100%;
  box-sizing: border-box;
}
.field-help {
  font-size: 12px;
  color: var(--text-muted);
  line-height: 1.8;
  margin-top: 4px;
}
.project-form-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid var(--border-color);
}
@media (max-width: 600px) {
  .form-grid {
    grid-template-columns: minmax(0, 1fr);
  }
  .project-form-card :deep(.el-steps--simple) {
    padding: 12px 8px;
  }
  .project-form-card :deep(.el-step__title) {
    font-size: 12px;
  }
}
</style>
