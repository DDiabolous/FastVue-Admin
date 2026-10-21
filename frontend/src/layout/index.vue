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
          <transition name="page-fade" mode="out-in">
            <component :is="Component" :key="route.path" />
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
  overflow-y: auto;
  scrollbar-gutter: stable;
  position: relative;
  background-color: var(--bg-color);
}

/* Page Transition */
.page-fade-leave-active,
.page-fade-enter-active {
  transition: opacity 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.page-fade-enter-from {
  opacity: 0;
}

.page-fade-leave-to {
  opacity: 0;
}
</style>
