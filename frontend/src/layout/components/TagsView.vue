<template>
  <div class="tags-view-container">
    <el-scrollbar class="tags-scrollbar">
      <div class="tags-wrapper">
        <router-link
          v-for="tag in tagsViewStore.visitedViews"
          :key="tag.path"
          :to="{ path: tag.path }"
          class="tag-item"
          :class="{ active: isActive(tag) }"
        >
          <span class="tag-title">{{ tag.title }}</span>
          <el-icon
            v-if="!tag.affix"
            class="close-icon"
            @click.prevent.stop="closeTag(tag)"
          >
            <Close />
          </el-icon>
        </router-link>
      </div>
    </el-scrollbar>

    <!-- Quick Tag Actions -->
    <el-dropdown trigger="click" @command="handleCommand">
      <div class="tag-actions-btn">
        <el-icon><ArrowDown /></el-icon>
      </div>
      <template #dropdown>
        <el-dropdown-menu>
          <el-dropdown-item command="refresh">
            <el-icon><Refresh /></el-icon>刷新当前
          </el-dropdown-item>
          <el-dropdown-item command="closeOthers">
            <el-icon><CircleClose /></el-icon>关闭其他
          </el-dropdown-item>
          <el-dropdown-item command="closeAll">
            <el-icon><FolderDelete /></el-icon>关闭所有
          </el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>
  </div>
</template>

<script setup>
import { watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useTagsViewStore } from '@/stores/tagsView'

const route = useRoute()
const router = useRouter()
const tagsViewStore = useTagsViewStore()

const isActive = (tag) => {
  return tag.path === route.path
}

const addTag = () => {
  if (route.name && route.meta?.title) {
    tagsViewStore.addView(route)
  }
}

const closeTag = (tag) => {
  tagsViewStore.delView(tag)
  if (isActive(tag)) {
    const latestView = tagsViewStore.visitedViews.slice(-1)[0]
    if (latestView) {
      router.push(latestView.path)
    } else {
      router.push('/')
    }
  }
}

const handleCommand = (cmd) => {
  if (cmd === 'refresh') {
    router.replace({ path: '/redirect' + route.fullPath }).catch(() => {
      // simple reload fallback
      window.location.reload()
    })
  } else if (cmd === 'closeOthers') {
    tagsViewStore.delOthersViews(route)
  } else if (cmd === 'closeAll') {
    tagsViewStore.delAllViews()
    router.push('/')
  }
}

watch(
  () => route.path,
  () => {
    addTag()
  },
  { immediate: true }
)
</script>

<style scoped>
.tags-view-container {
  height: var(--tags-height);
  background: var(--header-bg);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  padding: 0 12px;
  gap: 8px;
}

.tags-scrollbar {
  flex: 1;
  white-space: nowrap;
}

.tags-wrapper {
  display: flex;
  align-items: center;
  gap: 6px;
  height: 100%;
  padding: 3px 0;
}

.tag-item {
  display: inline-flex;
  align-items: center;
  height: 28px;
  padding: 0 10px;
  font-size: 12px;
  color: var(--text-regular);
  background-color: var(--tag-sub-bg, #f8fafc);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  text-decoration: none;
  transition: all 0.2s ease;
  user-select: none;
}

.tag-item:hover {
  color: var(--primary-color);
  border-color: var(--border-color);
}

.tag-item.active {
  background-color: var(--menu-active-bg, #eff6ff);
  color: var(--primary-color);
  border-color: var(--primary-color);
  font-weight: 500;
}

.tag-title {
  margin-right: 4px;
}

.close-icon {
  font-size: 12px;
  border-radius: 50%;
  padding: 2px;
  margin-left: 2px;
  transition: all 0.15s;
}

.close-icon:hover {
  background-color: rgba(37, 99, 235, 0.15);
  color: var(--primary-color);
}

.tag-actions-btn {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  color: var(--text-regular);
  background-color: var(--card-bg);
  cursor: pointer;
  border: 1px solid var(--border-color);
  transition: all 0.2s;
}

.tag-actions-btn:hover {
  color: var(--primary-color);
  border-color: var(--primary-color);
}
</style>
