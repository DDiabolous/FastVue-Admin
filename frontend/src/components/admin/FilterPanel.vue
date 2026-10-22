<template>
  <el-form
    :model="model"
    inline
    class="filter-panel business-filter"
    @submit.prevent="$emit('search')"
  >
    <div class="filter-panel-left">
      <slot />
    </div>
    <div v-if="$slots.actions" class="filter-panel-right">
      <slot name="actions" />
    </div>
  </el-form>
</template>
<script setup>
defineProps({ model: { type: Object, required: true } })
defineEmits(['search'])
</script>
