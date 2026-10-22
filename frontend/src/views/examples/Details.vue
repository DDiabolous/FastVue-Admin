<template>
  <PageContainer
    class="business-page example-page"
    title="复杂详情"
    description="以项目档案展示状态、描述列表、关联任务和操作记录。"
  >
    <template #actions>
      <ExampleGuide
        source="Details.vue"
        :features="[
          '详情页 / 抽屉共享 ProjectDetails',
          '关联数据表格与时间线',
          '实体不存在时的空状态与导航',
        ]"
      />
    </template>
    <el-card shadow="never">
      <div class="detail-toolbar">
        <el-select v-model="projectId" placeholder="选择项目" aria-label="选择项目">
          <el-option
            v-for="item in store.projects"
            :key="item.id"
            :label="item.name"
            :value="item.id"
          />
        </el-select>
        <el-button
          v-if="project"
          type="primary"
          @click="router.push({ path: '/examples/form', query: { id: project.id } })"
        >
          编辑项目
        </el-button>
      </div>
      <template v-if="project">
        <ProjectDetails :project="project" />
        <h3>交付阶段</h3>
        <el-table :data="stages" border>
          <el-table-column prop="name" label="阶段" min-width="160" />
          <el-table-column prop="owner" label="负责人" min-width="100" />
          <el-table-column label="状态" min-width="120">
            <template #default="{ row }">
              <el-tag :type="row.done ? 'success' : 'info'">
                {{ row.done ? '已完成' : '待完成' }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </template>
      <el-empty v-else description="项目不存在或已删除">
        <el-button @click="router.push('/examples/list')">返回列表</el-button>
      </el-empty>
    </el-card>
  </PageContainer>
</template>
<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import PageContainer from '@/components/admin/PageContainer.vue'
import ExampleGuide from '@/components/examples/ExampleGuide.vue'
import ProjectDetails from '@/components/examples/ProjectDetails.vue'
import { useExampleProjects } from '@/stores/exampleProjects'
const route = useRoute(),
  router = useRouter(),
  store = useExampleProjects()
const projectId = ref(route.query.id || store.projects[0]?.id || '')
watch(
  () => route.query.id,
  (id) => {
    if (id) projectId.value = id
  },
)
const project = computed(() => store.projects.find((p) => p.id === projectId.value))
const stages = computed(() =>
  ['需求确认', '方案实施', '验收交付'].map((name, index) => ({
    name,
    owner: project.value?.owner,
    done: (project.value?.progress || 0) >= [20, 70, 100][index],
  })),
)
</script>
<style scoped>
.detail-toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  justify-content: space-between;
  margin-bottom: 28px;
}
.detail-toolbar .el-select {
  width: min(100%, 300px);
}
h3 {
  font-size: 15px;
  margin: 28px 0 20px;
}
</style>
