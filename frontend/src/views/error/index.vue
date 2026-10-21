<template>
  <div class="starter-error">
    <el-result
      :icon="code === 403 ? 'warning' : 'info'"
      :title="String(code)"
      :sub-title="code === 403 ? '你没有访问此页面的权限' : '页面不存在或当前模块未启用'"
    >
      <template #extra>
        <el-button type="primary" @click="$router.push('/dashboard')">返回工作台</el-button>
      </template>
    </el-result>
  </div>
</template>
<script setup>
defineProps({ code: Number })
</script>
