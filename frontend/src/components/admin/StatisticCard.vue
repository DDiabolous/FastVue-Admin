<template>
  <el-card shadow="never" class="business-statistic" :class="`statistic-${tone}`">
    <div class="statistic-heading">
      <span>{{ label }}</span>
      <span class="statistic-icon"><slot name="icon" /></span>
    </div>
    <div class="statistic-value">
      <slot />
      <small v-if="unit">{{ unit }}</small>
    </div>
    <div v-if="$slots.hint" class="statistic-hint"><slot name="hint" /></div>
  </el-card>
</template>
<script setup>
defineProps({ label: String, unit: String, tone: { type: String, default: 'primary' } })
</script>
