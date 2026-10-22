<template>
  <header class="navbar-container">
    <!-- Left: Collapse & Breadcrumb -->
    <div class="navbar-left">
      <el-button class="collapse-trigger-btn" text @click="appStore.toggleSidebar">
        <el-icon :size="18">
          <Fold v-if="!appStore.sidebarCollapsed" />
          <Expand v-else />
        </el-icon>
      </el-button>

      <el-breadcrumb separator="/" class="breadcrumb">
        <el-breadcrumb-item :to="{ path: '/dashboard' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item v-if="route.meta.group">{{ route.meta.group }}</el-breadcrumb-item>
        <el-breadcrumb-item v-if="currentRouteTitle && currentRouteTitle !== '工作台'">
          {{ currentRouteTitle }}
        </el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <!-- Right: Theme Toggle, Notification, Fullscreen, User Profile -->
    <div class="navbar-right">
      <button
        class="nav-search"
        type="button"
        aria-label="搜索页面"
        @click="appStore.searchVisible = true"
      >
        <el-icon><Search /></el-icon>
        <span>搜索页面</span>
        <kbd>{{ isMac ? '⌘ K' : 'Ctrl K' }}</kbd>
      </button>
      <el-tooltip content="界面设置" placement="bottom">
        <button
          class="action-item"
          type="button"
          aria-label="界面设置"
          @click="appStore.appearanceVisible = true"
        >
          <el-icon :size="18"><Brush /></el-icon>
        </button>
      </el-tooltip>
      <!-- Action Button 1: Dark Mode Theme Switcher -->
      <el-tooltip
        :content="appStore.isDark ? '切换为浅色日间模式' : '切换为暗黑夜间模式'"
        placement="bottom"
      >
        <button
          class="action-item"
          type="button"
          aria-label="切换主题"
          :disabled="appStore.themeChanging"
          :aria-busy="appStore.themeChanging"
          @click="appStore.toggleTheme"
        >
          <el-icon :size="18">
            <Moon v-if="!appStore.isDark" />
            <Sunny v-else />
          </el-icon>
        </button>
      </el-tooltip>

      <!-- Action Button 2: Fullscreen Toggle -->
      <el-tooltip :content="isFullscreen ? '退出全屏浏览' : '开启全屏显示'" placement="bottom">
        <div class="action-item" @click="toggleFullScreen">
          <el-icon :size="18">
            <FullScreen />
          </el-icon>
        </div>
      </el-tooltip>

      <!-- Action Button 3: Notification Center Popover with Badge -->
      <el-popover
        placement="bottom-end"
        :width="360"
        trigger="click"
        popper-class="notification-popover"
      >
        <template #reference>
          <div class="action-item" aria-label="消息与告警通知">
            <el-badge
              :value="appStore.unreadCount"
              :max="99"
              :hidden="appStore.unreadCount === 0"
              class="badge-container"
            >
              <el-icon :size="18"><Bell /></el-icon>
            </el-badge>
          </div>
        </template>

        <div class="notification-box">
          <div class="notification-header">
            <span class="title">通知中心</span>
            <el-button
              v-if="appStore.unreadCount > 0"
              link
              type="primary"
              size="small"
              @click="appStore.markAllNotificationsAsRead"
            >
              全部已读
            </el-button>
          </div>

          <div class="notification-list">
            <div
              v-for="item in appStore.notifications"
              :key="item.id"
              class="notification-item"
              :class="{ 'is-unread': !item.read }"
              @click="item.read = true"
            >
              <div class="item-icon" :class="item.type">
                <el-icon v-if="item.type === 'warning'"><WarningFilled /></el-icon>
                <el-icon v-else-if="item.type === 'success'"><SuccessFilled /></el-icon>
                <el-icon v-else><InfoFilled /></el-icon>
              </div>
              <div class="item-content">
                <div class="item-title-row">
                  <span class="item-title">{{ item.title }}</span>
                  <span v-if="!item.read" class="unread-dot"></span>
                </div>
                <div class="item-desc">{{ item.desc }}</div>
                <div class="item-time">{{ item.time }}</div>
              </div>
            </div>
            <div v-if="appStore.notifications.length === 0" class="empty-notice">
              暂无新系统通知
            </div>
          </div>
        </div>
      </el-popover>

      <!-- User Dropdown Profile -->
      <el-dropdown trigger="click" @command="handleUserCommand">
        <div class="user-profile-trigger">
          <el-avatar :size="32" :src="userStore.currentAvatar">
            {{ userStore.currentRealName.slice(0, 1) }}
          </el-avatar>
          <div class="user-meta">
            <span class="user-name">{{ userStore.currentRealName }}</span>
            <span class="user-role">{{ userStore.currentRoleName }}</span>
          </div>
          <el-icon class="arrow-icon"><ArrowDown /></el-icon>
        </div>

        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="profile">
              <el-icon><User /></el-icon>
              个人中心
            </el-dropdown-item>
            <el-dropdown-item command="password">
              <el-icon><Lock /></el-icon>
              修改密码
            </el-dropdown-item>
            <el-dropdown-item v-if="userStore.can('system:settings:read')" command="settings">
              <el-icon><Setting /></el-icon>
              系统设置
            </el-dropdown-item>
            <el-dropdown-item divided command="logout" class="logout-item">
              <el-icon color="#ef4444"><SwitchButton /></el-icon>
              <span style="color: #ef4444">退出系统</span>
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </header>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Fold,
  Expand,
  Moon,
  Sunny,
  FullScreen,
  Bell,
  ArrowDown,
  User,
  Lock,
  Setting,
  SwitchButton,
  WarningFilled,
  SuccessFilled,
  InfoFilled,
} from '@element-plus/icons-vue'
import { useAppStore } from '@/stores/app'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const appStore = useAppStore()
const userStore = useUserStore()

const isMac = /Mac/i.test(navigator.platform)
const currentRouteTitle = computed(() => route.meta?.title || '')

const isFullscreen = ref(false)

const syncFullscreen = () => {
  isFullscreen.value = !!document.fullscreenElement
}
onMounted(() => document.addEventListener('fullscreenchange', syncFullscreen))
onUnmounted(() => document.removeEventListener('fullscreenchange', syncFullscreen))

const toggleFullScreen = () => {
  if (!document.fullscreenElement) {
    document.documentElement
      .requestFullscreen()
      .then(() => {
        isFullscreen.value = true
      })
      .catch(() => {})
  } else {
    if (document.exitFullscreen) {
      document
        .exitFullscreen()
        .then(() => {
          isFullscreen.value = false
        })
        .catch(() => {})
    }
  }
}

const handleUserCommand = (cmd) => {
  if (cmd === 'profile') {
    router.push('/profile')
  } else if (cmd === 'password') {
    router.push({ path: '/profile', query: { tab: 'security' } })
  } else if (cmd === 'settings') {
    router.push('/settings')
  } else if (cmd === 'logout') {
    ElMessageBox.confirm('确定退出当前系统吗？', '退出登录', {
      confirmButtonText: '确认退出',
      cancelButtonText: '取消',
      type: 'warning',
    })
      .then(async () => {
        try {
          await userStore.logout()
        } catch (error) {
          ElMessage.warning(error.message || '服务端注销失败，本地会话已清理')
        }
        router.push('/login')
      })
      .catch(() => {})
  }
}
</script>

<style scoped>
.navbar-container {
  height: var(--header-height);
  background-color: var(--header-bg);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 16px;
  position: relative;
  z-index: 99;
}

.navbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.collapse-trigger-btn {
  padding: 6px;
  color: #475569;
  border-radius: 6px;
}

.collapse-trigger-btn:hover {
  background-color: #f1f5f9;
  color: var(--primary-color);
}

.breadcrumb {
  font-size: 13px;
}

.navbar-right {
  display: flex;
  align-items: center;
  gap: 8px;
  height: 100%;
}

/* Action Items: Uniform 36x36px with Subpixel Centering */
.action-item {
  width: 36px;
  height: 36px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  cursor: pointer;
  color: #64748b;
  transition: all 0.2s ease;
  line-height: 1;
  vertical-align: middle;
  padding: 0;
  margin: 0;
  box-sizing: border-box;
}

.action-item:hover {
  background-color: #f1f5f9;
  color: var(--primary-color);
}

html.dark .action-item:hover {
  background-color: #334155;
  color: #60a5fa;
}

/* Perfect alignment for ElBadge and inner ElIcon */
.action-item :deep(.badge-container),
.action-item :deep(.el-badge) {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  line-height: 1;
  position: relative;
}

.action-item :deep(.el-badge__content) {
  top: 4px;
  right: 5px;
  transform: translate(50%, -50%);
}

.action-item :deep(.el-icon) {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  width: 18px;
  height: 18px;
  line-height: 1;
  margin: 0;
  padding: 0;
}

/* User Profile Trigger: Same 36px Height */
.user-profile-trigger {
  height: 36px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
  margin-left: 4px;
}

.user-profile-trigger:hover {
  background-color: var(--menu-hover-bg, #f1f5f9);
}

.user-meta {
  display: flex;
  flex-direction: column;
  line-height: 1.25;
}

.user-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-main);
}

.user-role {
  font-size: 11px;
  color: var(--text-muted);
}

.arrow-icon {
  font-size: 12px;
  color: #94a3b8;
}

.notification-box {
  padding: 4px;
}

.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 8px 12px;
  border-bottom: 1px solid var(--border-color);
  margin-bottom: 8px;
}

.notification-header .title {
  font-weight: 600;
  font-size: 14px;
  color: var(--text-main);
}

.notification-list {
  max-height: 320px;
  overflow-y: auto;
  padding: 2px 4px 6px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.notification-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  border-radius: 10px;
  background-color: var(--tag-sub-bg, #f8fafc);
  border: 1px solid var(--border-color);
  transition: all 0.2s ease;
  cursor: pointer;
}

.notification-item:hover {
  background-color: var(--menu-hover-bg, #f1f5f9);
  border-color: var(--border-color);
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.notification-item.is-unread {
  background-color: var(--menu-active-bg, #eff6ff);
  border-color: rgba(37, 99, 235, 0.28);
}

.notification-item.is-unread:hover {
  border-color: var(--primary-color);
}

.item-icon {
  width: 32px;
  height: 32px;
  min-width: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}

.item-icon.warning {
  background-color: rgba(245, 158, 11, 0.15);
  color: #f59e0b;
}

.item-icon.success {
  background-color: rgba(16, 185, 129, 0.15);
  color: #10b981;
}

.item-icon.info {
  background-color: rgba(59, 130, 246, 0.15);
  color: #3b82f6;
}

.item-content {
  flex: 1;
}

.item-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.item-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-main);
}

.unread-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: var(--primary-color);
  display: inline-block;
}

.item-desc {
  font-size: 12px;
  color: var(--text-muted);
  line-height: 1.45;
  margin-bottom: 4px;
}

.item-time {
  font-size: 11px;
  color: #94a3b8;
  margin-top: 4px;
}

.empty-notice {
  text-align: center;
  padding: 24px;
  color: #94a3b8;
  font-size: 13px;
}
</style>
