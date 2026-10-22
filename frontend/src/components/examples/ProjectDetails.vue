<template>
  <div v-if="project" class="project-details">
    <div class="project-detail-title">
      <div>
        <span>{{ project.code }}</span>
        <h2>{{ project.name }}</h2>
      </div>
      <el-tag :type="projectStates[project.status].type">
        {{ projectStates[project.status].label }}
      </el-tag>
    </div>
    <el-descriptions :column="1" border>
      <el-descriptions-item label="分类">{{ project.category }}</el-descriptions-item>
      <el-descriptions-item label="负责人">{{ project.owner }}</el-descriptions-item>
      <el-descriptions-item label="计划周期">{{ project.dates.join(' 至 ') }}</el-descriptions-item>
      <el-descriptions-item label="预算">
        ¥ {{ Number(project.budget).toLocaleString() }}
      </el-descriptions-item>
      <el-descriptions-item label="进度">
        <el-progress :percentage="project.progress" />
      </el-descriptions-item>
      <el-descriptions-item label="说明">
        <span class="project-description">{{ project.description || '未填写' }}</span>
      </el-descriptions-item>
    </el-descriptions>
    <h3>操作记录</h3>
    <el-timeline>
      <el-timeline-item
        v-for="(event, index) in project.events"
        :key="index"
        :timestamp="event.time"
        placement="top"
      >
        {{ event.text }}
      </el-timeline-item>
    </el-timeline>
  </div>
</template>
<script setup>
import { projectStates } from '@/stores/exampleProjects'
defineProps({ project: Object })
</script>
<style scoped>
.project-detail-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 24px;
  padding: 20px;
  background: var(--surface-muted);
  border: 1px solid var(--border-light);
  border-radius: 10px;
}
.project-detail-title span {
  color: var(--text-muted);
  font-size: 12px;
}
.project-detail-title h2 {
  margin: 8px 0 0;
  font-size: 17px;
  overflow-wrap: anywhere;
}
.project-description {
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}
h3 {
  font-size: 15px;
  margin: 28px 0 20px;
}
</style>
