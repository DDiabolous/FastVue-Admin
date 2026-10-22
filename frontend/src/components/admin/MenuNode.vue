<template>
  <el-sub-menu v-if="item.children" :index="item.title">
    <template #title>
      <el-icon v-if="depth === 0" class="menu-primary-icon"><component :is="item.icon || 'Grid'" /></el-icon>
      <span>{{ item.title }}</span>
    </template>
    <MenuNode v-for="child in item.children" :key="child.path || child.title" :item="child" :depth="depth + 1" />
  </el-sub-menu>
  <el-menu-item v-else :index="item.path">
    <el-icon v-if="depth === 0 && item.icon" class="menu-primary-icon"><component :is="item.icon" /></el-icon>
    <template #title>{{ item.title }}</template>
  </el-menu-item>
</template>
<script setup>
defineProps({
  item: { type: Object, required: true },
  depth: { type: Number, default: 0 },
})
</script>
