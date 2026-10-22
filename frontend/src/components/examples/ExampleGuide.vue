<template>
  <el-button :icon="QuestionFilled" @click="visible = true">页面用法</el-button>
  <el-drawer class="business-overlay" v-model="visible" title="页面用法" size="min(440px, 100vw)">
    <h3>{{ route.meta.title }}</h3>
    <p class="guide-copy">{{ purpose }}</p>
    <el-alert :title="scope" type="info" :closable="false" show-icon />
    <h4>可复用内容</h4>
    <ul class="guide-list">
      <li v-for="item in features" :key="item">{{ item }}</li>
    </ul>
    <h4>源码位置</h4>
    <code class="guide-source">frontend/src/views/examples/{{ source }}</code>
    <p class="guide-copy">
      接入真实业务时，将示例数据操作替换为 API 请求，保留校验、加载、错误处理与未保存提醒。
    </p>
  </el-drawer>
</template>
<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { QuestionFilled } from '@element-plus/icons-vue'
const route = useRoute()
const visible = ref(false)
defineProps({
  source: { type: String, required: true },
  purpose: { type: String, default: '可复制到业务模块的页面结构与交互范例。' },
  scope: {
    type: String,
    default: '演示数据在列表、卡片、表单与详情间共享，刷新页面后恢复初始数据，不提交到后端。',
  },
  features: {
    type: Array,
    default: () => ['PageContainer：页面标题与操作入口', '统一主题、暗色与手机布局'],
  },
})
</script>
<style scoped>
.guide-copy,
.guide-list {
  color: var(--text-regular);
  font-size: 14px;
  line-height: 1.9;
}
.guide-list {
  padding-left: 20px;
}
.guide-source {
  display: block;
  padding: 14px;
  background: var(--surface-muted);
  border-radius: 8px;
  overflow-wrap: anywhere;
  font-size: 12px;
}
h4 {
  margin-top: 28px;
}
</style>
