<template>
  <el-sub-menu v-if="item.children" :index="item.title">
    <template #title>
      <el-icon><component :is="item.icon || 'Folder'" /></el-icon>
      <span>{{ item.title }}</span>
    </template>
    <MenuNode v-for="child in item.children" :key="child.path" :item="child" />
  </el-sub-menu>
  <el-menu-item v-else :index="item.path">
    <el-icon><component :is="item.icon" /></el-icon>
    <template #title>{{ item.title }}</template>
  </el-menu-item>
</template>
<script setup>
defineProps({ item: { type: Object, required: true } })
</script>
