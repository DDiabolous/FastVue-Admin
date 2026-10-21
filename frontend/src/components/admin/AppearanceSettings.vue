<template>
  <el-drawer v-model="app.appearanceVisible" title="界面设置" size="min(360px, 100vw)">
    <section class="preference-section">
      <h3>外观模式</h3>
      <p>选择浅色、深色或跟随系统。</p>
      <el-radio-group :model-value="app.theme" @update:model-value="app.setTheme">
        <el-radio-button value="light">浅色</el-radio-button>
        <el-radio-button value="dark">深色</el-radio-button>
        <el-radio-button value="system">跟随系统</el-radio-button>
      </el-radio-group>
    </section>
    <section class="preference-section">
      <h3>主题色</h3>
      <p>应用于按钮、导航与选中状态。</p>
      <div class="accent-options">
        <button
          v-for="accent in accents"
          :key="accent.value"
          type="button"
          :aria-label="accent.label"
          :aria-pressed="app.accent === accent.value"
          :style="{ backgroundColor: accent.value }"
          @click="app.updateAppearance({ accent: accent.value })"
        >
          <el-icon v-if="app.accent === accent.value"><Check /></el-icon>
        </button>
      </div>
    </section>
    <section class="preference-section">
      <h3>表格密度</h3>
      <p>在信息密度与阅读空间之间自由切换。</p>
      <el-radio-group
        :model-value="app.density"
        @update:model-value="(value) => app.updateAppearance({ density: value })"
      >
        <el-radio-button value="comfortable">舒适</el-radio-button>
        <el-radio-button value="compact">紧凑</el-radio-button>
      </el-radio-group>
    </section>
    <div class="preference-note">
      <el-icon><InfoFilled /></el-icon>
      <span>偏好自动保存在当前浏览器，刷新后仍然生效。</span>
    </div>
    <template #footer>
      <el-button
        @click="app.updateAppearance({ theme: 'light', accent: '#2563eb', density: 'comfortable' })"
      >
        恢复默认外观
      </el-button>
      <el-button type="primary" @click="app.appearanceVisible = false">完成</el-button>
    </template>
  </el-drawer>
</template>
<script setup>
import { useAppStore } from '@/stores/app'
import { accents } from '@/utils/preferences'
const app = useAppStore()
</script>
