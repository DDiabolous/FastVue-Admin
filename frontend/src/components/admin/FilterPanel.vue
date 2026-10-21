<template>
  <el-form
    :model="model"
    inline
    class="filter-panel business-filter"
    @submit.prevent="$emit('search')"
  >
    <slot />
  </el-form>
</template>
<script setup>
defineProps({ model: { type: Object, required: true } })
defineEmits(['search'])
</script>
