<template>
  <div class="starter-toolbar">
    <div class="starter-toolbar-actions">
      <slot />
      <span v-if="selected" class="selection-chip">已选 {{ selected }} 项</span>
    </div>
    <div class="table-tools">
      <span v-if="total !== undefined" class="table-count">
        共
        <strong>{{ total }}</strong>
        条
      </span>
      <slot name="tools" />
      <el-tooltip content="刷新数据">
        <el-button
          :loading="loading"
          :icon="Refresh"
          circle
          aria-label="刷新"
          @click="$emit('refresh')"
        />
      </el-tooltip>
      <el-tooltip content="表格密度" placement="top">
        <el-button ref="densityTriggerRef" circle aria-label="表格密度">
          <el-icon><Operation /></el-icon>
        </el-button>
      </el-tooltip>
      <el-popover
        :virtual-ref="densityTriggerRef"
        virtual-triggering
        placement="bottom-end"
        :width="160"
        trigger="click"
      >
        <div class="popover-heading">表格密度</div>
        <el-radio-group
          class="density-radio-group"
          :model-value="app.density"
          @update:model-value="(value) => app.updateAppearance({ density: value })"
        >
          <el-radio-button value="comfortable">舒适</el-radio-button>
          <el-radio-button value="compact">紧凑</el-radio-button>
        </el-radio-group>
      </el-popover>
      <el-tooltip v-if="columns.length" content="列设置" placement="top">
        <el-button ref="columnTriggerRef" circle aria-label="列设置">
          <el-icon><SetUp /></el-icon>
        </el-button>
      </el-tooltip>
      <el-popover
        v-if="columns.length"
        :virtual-ref="columnTriggerRef"
        virtual-triggering
        placement="bottom-end"
        width="230"
        trigger="click"
      >
        <div class="popover-heading">
          显示列
          <el-button link type="primary" @click="$emit('reset-columns')">重置</el-button>
        </div>
        <div class="column-options">
          <el-checkbox
            v-for="column in columns"
            :key="column.prop"
            :model-value="visibleColumns.includes(column.prop)"
            :disabled="
              column.locked || (visibleColumns.length === 1 && visibleColumns.includes(column.prop))
            "
            @change="(checked) => updateColumn(column.prop, checked)"
          >
            {{ column.label }}
          </el-checkbox>
        </div>
      </el-popover>
    </div>
  </div>
</template>
<script setup>
import { ref } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { useAppStore } from '@/stores/app'
const app = useAppStore()
const densityTriggerRef = ref(null)
const columnTriggerRef = ref(null)
const props = defineProps({
  selected: { type: Number, default: 0 },
  loading: Boolean,
  total: Number,
  columns: { type: Array, default: () => [] },
  visibleColumns: { type: Array, default: () => [] },
})
const emit = defineEmits(['refresh', 'update:visibleColumns', 'reset-columns'])
function updateColumn(prop, checked) {
  emit(
    'update:visibleColumns',
    checked
      ? [...props.visibleColumns, prop]
      : props.visibleColumns.filter((item) => item !== prop),
  )
}
</script>
