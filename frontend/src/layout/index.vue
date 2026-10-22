<template>
  <div class="app-layout">
    <Sidebar />
    <div
      v-if="!appStore.sidebarCollapsed"
      class="mobile-sidebar-backdrop"
      @click="appStore.toggleSidebar"
    />

    <div class="main-wrapper">
      <Navbar />
      <CommandSearch />
      <AppearanceSettings />

      <main class="content-container">
        <router-view v-slot="{ Component, route }">
          <transition name="page-slide" mode="out-in">
            <component :is="Component" :key="route.fullPath + '-' + appStore.viewKey" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup>
import { useAppStore } from '@/stores/app'
import Sidebar from './components/Sidebar.vue'
import Navbar from './components/Navbar.vue'
import CommandSearch from '@/components/admin/CommandSearch.vue'
import AppearanceSettings from '@/components/admin/AppearanceSettings.vue'

const appStore = useAppStore()
</script>

<style scoped>
.app-layout {
  display: flex;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  background-color: var(--bg-color);
}

.main-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  height: 100vh;
  overflow: hidden;
}

.content-container {
  flex: 1;
  min-height: 0;
  overflow-x: hidden;
  /* Keep the gutter even for short pages and browsers without scrollbar-gutter support. */
  overflow-y: scroll;
  scrollbar-gutter: stable;
  position: relative;
  background-color: var(--bg-color);
}

.content-container::-webkit-scrollbar {
  width: 8px;
}

/* Page Transition - Subtle Natural Fade Slide Y */
.page-slide-enter-active {
  transition:
    opacity var(--motion-duration-base, 220ms) var(--ease-out-natural, cubic-bezier(0.16, 1, 0.3, 1)),
    transform var(--motion-duration-base, 220ms) var(--ease-out-natural, cubic-bezier(0.16, 1, 0.3, 1));
  will-change: opacity, transform;
}

.page-slide-leave-active {
  transition: opacity 100ms var(--ease-in-swift, cubic-bezier(0.4, 0, 1, 1));
  will-change: opacity;
}

.page-slide-enter-from {
  opacity: 0;
  transform: translateY(6px);
}

.page-slide-leave-to {
  opacity: 0;
}
</style>
