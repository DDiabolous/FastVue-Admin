<template>
  <div v-if="loading" class="table-skeleton" role="status" aria-label="正在加载">
    <el-skeleton :rows="4" animated />
  </div>
  <div v-else class="table-empty">
    <span class="table-empty-icon">
      <el-icon :size="26">
        <component :is="error ? 'Warning' : filtered ? 'Search' : 'Document'" />
      </el-icon>
    </span>
    <h3>{{ error ? '暂时无法加载数据' : filtered ? '没有找到匹配结果' : '这里还没有数据' }}</h3>
    <p>
      {{
        error
          ? '请检查连接后重试。'
          : filtered
            ? '试试其他关键词，或清除当前筛选条件。'
            : '新增记录后，就会显示在这里。'
      }}
    </p>
    <el-button v-if="error || filtered" @click="$emit(error ? 'retry' : 'reset')">
      {{ error ? '重新加载' : '清除筛选' }}
    </el-button>
  </div>
</template>
<script setup>
defineProps({ loading: Boolean, error: String, filtered: Boolean })
defineEmits(['retry', 'reset'])
</script>
