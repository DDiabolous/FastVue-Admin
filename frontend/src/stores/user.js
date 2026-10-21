import { defineStore } from 'pinia'
import { authApi } from '@/api/system'
import { storageKey } from '@/config/app'
import { useTagsViewStore } from './tagsView'
import { hasPermission } from '@/config/permissions'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem(storageKey('token')) || '',
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
      const result = await authApi.login(username, password)
      this.token = result.token
      localStorage.setItem(storageKey('token'), result.token)
      this.userInfo = result.user
      this.loaded = true
    },
    async fetchUser() {
      this.userInfo = await authApi.me()
      this.loaded = true
    },
    clearSession() {
      useTagsViewStore().delAllViews()
      this.token = ''
      this.userInfo = null
      this.loaded = false
      localStorage.removeItem(storageKey('token'))
    },
    async logout() {
      try {
        await authApi.logout()
      } finally {
        this.clearSession()
      }
    },
    async updateUserProfile(data) {
      this.userInfo = await authApi.profile(data)
    },
    async changePassword(oldPassword, newPassword) {
      await authApi.password({ oldPassword, newPassword })
      this.clearSession()
    },
  },
})
