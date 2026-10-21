<template>
  <el-dialog
    v-model="app.searchVisible"
    title="搜索页面"
    width="min(580px, 94vw)"
    class="command-dialog"
    :show-close="false"
    @opened="input?.focus()"
    @closed="keyword = ''"
  >
    <el-input
      ref="input"
      v-model="keyword"
      placeholder="输入页面名称、分组或路径…"
      size="large"
      clearable
      aria-label="搜索页面"
      @keydown.down.prevent="move(1)"
      @keydown.up.prevent="move(-1)"
      @keydown.enter.prevent="go(results[active])"
    >
      <template #prefix>
        <el-icon><Search /></el-icon>
      </template>
      <template #suffix><kbd>ESC</kbd></template>
    </el-input>
    <div class="command-results" role="listbox" aria-label="页面搜索结果">
      <button
        v-for="(item, index) in results"
        :key="item.path"
        :ref="
          (el) => {
            if (el && index === active) activeElement = el
          }
        "
        type="button"
        role="option"
        :aria-selected="index === active"
        :class="{ active: index === active }"
        @mouseenter="active = index"
        @click="go(item)"
      >
        <span class="command-icon">
          <el-icon><component :is="item.icon" /></el-icon>
        </span>
        <span>
          <strong>{{ item.title }}</strong>
          <small>{{ item.group || '常用页面' }} · {{ item.path }}</small>
        </span>
        <el-icon class="command-arrow"><Right /></el-icon>
      </button>
      <el-empty
        v-if="!results.length"
        description="没有找到匹配页面，试试其他关键词"
        :image-size="70"
      />
    </div>
    <template #footer>
      <span class="starter-muted">↑ ↓ 选择页面 · Enter 打开 · {{ shortcut }} 搜索</span>
    </template>
  </el-dialog>
</template>
<script setup>
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { modules } from '@/config/modules'
import { useUserStore } from '@/stores/user'
import { useAppStore } from '@/stores/app'
const app = useAppStore(),
  user = useUserStore(),
  router = useRouter()
const keyword = ref(''),
  input = ref(),
  active = ref(0),
  activeElement = ref()
const shortcut = /Mac/i.test(navigator.platform) ? '⌘ K' : 'Ctrl K'
const results = computed(() =>
  modules.filter(
    (item) =>
      user.can(item.permission) &&
      `${item.title} ${item.group || ''} ${item.path}`
        .toLowerCase()
        .includes(keyword.value.trim().toLowerCase()),
  ),
)
watch(keyword, () => {
  active.value = 0
})
function move(direction) {
  if (!results.value.length) return
  active.value = (active.value + direction + results.value.length) % results.value.length
  nextTick(() => activeElement.value?.scrollIntoView({ block: 'nearest' }))
}
function go(item) {
  if (!item) return
  app.searchVisible = false
  app.sidebarCollapsed = window.innerWidth < 768 ? true : app.sidebarCollapsed
  router.push(item.path)
}
function keydown(event) {
  if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') {
    event.preventDefault()
    app.searchVisible = !app.searchVisible
  }
}
onMounted(() => window.addEventListener('keydown', keydown))
onUnmounted(() => window.removeEventListener('keydown', keydown))
</script>
