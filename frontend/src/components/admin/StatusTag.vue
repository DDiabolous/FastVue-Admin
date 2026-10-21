<template>
  <el-tag :type="Number(value) === 1 ? 'success' : 'info'" effect="light">
    {{ Number(value) === 1 ? '启用' : '停用' }}
  </el-tag>
</template>
<script setup>
defineProps({ value: [Number, String] })
</script>
