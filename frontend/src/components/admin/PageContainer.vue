<template>
  <div class="page-container starter-page">
    <div class="starter-page-heading">
      <div>
        <div class="page-title-line">
          <h1>{{ title }}</h1>
          <el-tooltip
            v-if="route.path !== '/dashboard'"
            :content="app.favoritePaths.includes(route.path) ? '取消收藏' : '收藏到工作台'"
          >
            <button
              type="button"
              class="page-favorite"
              :class="{ saved: app.favoritePaths.includes(route.path) }"
              :aria-label="app.favoritePaths.includes(route.path) ? '取消收藏' : '收藏到工作台'"
              :aria-pressed="app.favoritePaths.includes(route.path)"
              @click="app.toggleFavorite(route.path)"
            >
              <el-icon>
                <StarFilled v-if="app.favoritePaths.includes(route.path)" />
                <Star v-else />
              </el-icon>
            </button>
          </el-tooltip>
        </div>
        <p v-if="description">{{ description }}</p>
      </div>
      <div class="starter-heading-actions"><slot name="actions" /></div>
    </div>
    <slot />
  </div>
</template>
<script setup>
import { useRoute } from 'vue-router'
import { useAppStore } from '@/stores/app'
const route = useRoute(),
  app = useAppStore()
defineProps({ title: String, description: String })
</script>
