import { defineStore } from 'pinia'
import { adminAuthApi } from '@/api/admin'
import { storageKey } from '@/config/app'
import { useTagsViewStore } from './tagsView'
import { hasPermission } from '@/config/permissions'

export const useAdminStore = defineStore('admin', {
  state: () => ({
    token: localStorage.getItem(storageKey('admin_token')) || '',
    userInfo: null,
    loaded: false,
  }),
  getters: {
    isLoggedIn: (state) => !!state.token,
    permissions: (state) => state.userInfo?.permissions || [],
    currentUsername: (state) => state.userInfo?.username || '未登录',
    currentRoleName: (state) => state.userInfo?.roleName || '用户',
    currentRealName: (state) => state.userInfo?.realName || state.userInfo?.username || '用户',
    currentAvatar: (state) => state.userInfo?.avatar || '',
  },
  actions: {
    can(permission) {
      return hasPermission(this.permissions, permission)
    },
    async login(username, password) {
      const result = await adminAuthApi.login(username, password)
      this.token = result.token
      localStorage.setItem(storageKey('admin_token'), result.token)
      this.userInfo = result.user
      this.loaded = true
    },
    async fetchUser() {
      this.userInfo = await adminAuthApi.me()
      this.loaded = true
    },
    clearSession() {
      useTagsViewStore().delAllViews()
      this.token = ''
      this.userInfo = null
      this.loaded = false
      localStorage.removeItem(storageKey('admin_token'))
    },
    async logout() {
      try {
        await adminAuthApi.logout()
      } finally {
        this.clearSession()
      }
    },
    async updateUserProfile(data) {
      this.userInfo = await adminAuthApi.profile(data)
    },
    async changePassword(oldPassword, newPassword) {
      await adminAuthApi.password({ oldPassword, newPassword })
      this.clearSession()
    },
  },
})
