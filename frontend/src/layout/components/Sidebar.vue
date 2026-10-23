<template>
  <aside class="sidebar-wrapper" :class="{ 'is-collapsed': appStore.sidebarCollapsed }">
    <!-- Brand / Logo Area -->
    <div class="sidebar-logo-container" @click="goHome">
      <div class="logo-mark-slot">
        <div class="logo-icon-box">
          <el-icon :size="22" color="#ffffff"><Management /></el-icon>
        </div>
      </div>
      <transition name="fade-slide">
        <div v-show="!appStore.sidebarCollapsed" class="logo-text-box">
          <span class="logo-title">{{ appConfig.name }}</span>
          <span class="logo-sub">{{ appConfig.fullDemo ? '完整演示' : 'Admin Starter' }}</span>
        </div>
      </transition>
    </div>

    <!-- Navigation Menu -->
    <el-scrollbar class="menu-scrollbar">
      <el-menu
        :default-active="activeMenu"
        :collapse="appStore.sidebarCollapsed"
        :collapse-transition="false"
        class="sidebar-menu"
        router
      >
        <MenuNode v-for="item in menuItems" :key="item.path || item.title" :item="item" />
      </el-menu>
    </el-scrollbar>

    <!-- Sidebar Bottom Collapse Toggle -->
    <div class="sidebar-footer">
      <el-tooltip
        :content="appStore.sidebarCollapsed ? '展开侧边栏' : '收起侧边栏'"
        placement="right"
        :disabled="!appStore.sidebarCollapsed"
      >
        <div class="collapse-btn" @click="appStore.toggleSidebar">
          <el-icon class="collapse-icon-slot" :size="16">
            <Fold v-if="!appStore.sidebarCollapsed" />
            <Expand v-else />
          </el-icon>
          <span v-if="!appStore.sidebarCollapsed" class="collapse-text">收起导航</span>
        </div>
      </el-tooltip>
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import MenuNode from '@/components/admin/MenuNode.vue'
import { menuGroups, modules } from '@/config/modules'
import { appConfig } from '@/config/app'
import { useAdminStore } from '@/stores/admin'
import { useRoute, useRouter } from 'vue-router'
import { Management, Fold, Expand } from '@element-plus/icons-vue'
import { useAppStore } from '@/stores/app'

const route = useRoute()
const router = useRouter()
const appStore = useAppStore()

const userStore = useAdminStore()
const menuItems = computed(() => {
  const items = []
  for (const item of modules.filter((item) => userStore.can(item.permission))) {
    if (!item.group) {
      items.push(item)
      continue
    }
    let group = items.find((entry) => entry.title === item.group && entry.children)
    if (!group) {
      group = { title: item.group, icon: menuGroups[item.group]?.icon || 'Grid', children: [] }
      items.push(group)
    }
    group.children.push(item)
  }
  return items
})

const activeMenu = computed(() => {
  return route.path
})

const goHome = () => {
  router.push('/dashboard')
}
</script>

<style scoped>
.sidebar-wrapper {
  --sidebar-item-inset: 10px;
  --sidebar-icon-slot-width: calc(var(--sidebar-collapsed-width) - 1px - var(--sidebar-item-inset) - var(--sidebar-item-inset));
  width: var(--sidebar-width);
  height: 100vh;
  background-color: var(--sidebar-bg);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  transition:
    width 0.28s cubic-bezier(0.4, 0, 0.2, 1),
    background-color 0.25s ease;
  overflow: hidden;
  position: relative;
  z-index: 100;
  box-shadow: var(--shadow-sm);
}

.sidebar-wrapper.is-collapsed {
  width: var(--sidebar-collapsed-width);
}

.sidebar-logo-container {
  height: var(--header-height);
  padding: 0;
  display: flex;
  align-items: center;
  gap: 0;
  overflow: hidden;
  cursor: pointer;
  border-bottom: 1px solid var(--border-color);
  user-select: none;
  background-color: var(--sidebar-bg);
  transition: background-color 0.25s ease;
}

.logo-mark-slot {
  width: calc(var(--sidebar-collapsed-width) - 1px);
  height: 100%;
  flex-shrink: 0;
  display: grid;
  place-items: center;
}

.logo-icon-box {
  width: 36px;
  height: 36px;
  min-width: 36px;
  border-radius: 8px;
  background: linear-gradient(135deg, #2563eb, #3b82f6);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 10px rgba(37, 99, 235, 0.3);
}

.logo-text-box {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  white-space: nowrap;
}

.logo-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-main);
  letter-spacing: 0.5px;
}

.logo-sub {
  font-size: 11px;
  color: var(--text-muted);
  letter-spacing: 0.2px;
}

.menu-scrollbar {
  flex: 1;
  background-color: var(--sidebar-bg);
}

.sidebar-menu {
  border-right: none !important;
  padding: 10px 8px;
  background-color: transparent !important;
  --el-menu-bg-color: transparent !important;
  --el-menu-hover-bg-color: transparent !important;
}

/* Fixed icon slots keep the same anchor throughout sidebar width transitions. */
.sidebar-menu {
  width: 100%;
  box-sizing: border-box;
}

:deep(.sidebar-menu > .el-menu-item),
:deep(.sidebar-menu > .el-sub-menu > .el-sub-menu__title),
:deep(.sidebar-menu > .el-menu-item > .el-menu-tooltip__trigger) {
  padding: 0 !important;
  justify-content: flex-start;
}

:deep(.sidebar-menu .menu-primary-icon) {
  width: var(--sidebar-icon-slot-width) !important;
  flex: 0 0 var(--sidebar-icon-slot-width);
}

/* Menu Item & Submenu Title - Driven by CSS variables so theme transitions 100% reliably */
:deep(.el-menu-item),
:deep(.el-sub-menu__title) {
  height: 44px;
  line-height: 44px;
  border-radius: 8px;
  margin-bottom: 4px;
  color: var(--menu-text-color) !important;
  font-weight: 500;
  font-size: 13px;
  transition: all 0.2s ease;
  background-color: transparent;
}

:deep(.el-menu-item .el-icon),
:deep(.el-sub-menu__title .el-icon) {
  font-size: 17px;
  margin-right: 10px;
  color: var(--menu-icon-color) !important;
  transition: color 0.2s ease;
}

:deep(.el-menu-item:hover),
:deep(.el-sub-menu__title:hover) {
  background-color: var(--menu-hover-bg) !important;
  color: var(--menu-hover-text) !important;
}

:deep(.el-menu-item:hover .el-icon),
:deep(.el-sub-menu__title:hover .el-icon) {
  color: var(--menu-hover-icon) !important;
}

/* Active Item - Driven by CSS variables */
:deep(.el-menu-item.is-active) {
  background-color: var(--menu-active-bg) !important;
  color: var(--menu-active-text) !important;
  font-weight: 600;
  position: relative;
}

:deep(.el-menu-item.is-active .el-icon) {
  color: var(--menu-active-text) !important;
}

:deep(.el-menu-item.is-active)::before {
  content: '';
  position: absolute;
  left: 0;
  top: 8px;
  bottom: 8px;
  width: 4px;
  background-color: var(--menu-active-bar);
  border-radius: 0 4px 4px 0;
}

/* Inline Secondary Submenu (when expanded) */
:deep(.el-menu--inline) {
  background-color: var(--menu-inline-bg) !important;
  border-radius: 8px;
  margin: 2px 0 6px;
  padding: 4px 0;
}

:deep(.el-menu--inline .el-menu-item) {
  padding-left: 54px !important;
}

:deep(.el-sub-menu.is-active > .el-sub-menu__title) {
  color: var(--menu-active-text) !important;
}

:deep(.el-sub-menu.is-active > .el-sub-menu__title .el-icon) {
  color: var(--menu-active-text) !important;
}

/* Footer Section */
.sidebar-footer {
  height: 48px;
  border-top: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  padding: 0 var(--sidebar-item-inset);
  background-color: var(--sidebar-bg);
  transition: background-color 0.25s ease;
}

.collapse-btn {
  display: flex;
  align-items: center;
  gap: 0;
  color: var(--text-muted);
  cursor: pointer;
  font-size: 13px;
  width: 100%;
  padding: 6px 0;
  border-radius: 6px;
  transition: all 0.2s;
}

.collapse-btn:hover {
  color: var(--menu-collapse-btn-hover-text);
  background-color: var(--menu-collapse-btn-hover-bg);
}

.collapse-icon-slot {
  width: var(--sidebar-icon-slot-width);
  flex: 0 0 var(--sidebar-icon-slot-width);
}

.collapse-text {
  margin-left: 10px;
  white-space: nowrap;
}

.fade-slide-enter-active,
.fade-slide-leave-active {
  transition:
    opacity 0.2s ease,
    transform 0.2s ease;
}

.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translateX(-10px);
}
</style>
