import { defineStore } from 'pinia'
import { nextTick } from 'vue'
import { readPreference, writePreference, normalizeAppearance } from '@/utils/preferences'
import { transitionTheme } from '@/utils/themeTransition'
import { storageKey } from '@/config/app'
import { confirmViewDiscard } from '@/utils/viewGuards'

export const useAppStore = defineStore('app', {
  state: () => ({
    ...normalizeAppearance(
      readPreference('appearance', { theme: localStorage.getItem(storageKey('theme')) || 'light' }),
    ),
    sidebarCollapsed: window.innerWidth < 768,
    systemDark: window.matchMedia('(prefers-color-scheme: dark)').matches,
    searchVisible: false,
    themeChanging: false,
    appearanceVisible: false,
    viewKey: 0,
    viewReloading: false,
    notifications: [],
    favoritePaths: Array.isArray(readPreference('favorites', []))
      ? readPreference('favorites', []).filter((path) => typeof path === 'string')
      : [],
  }),
  getters: {
    isDark: (state) => state.theme === 'dark' || (state.theme === 'system' && state.systemDark),
    unreadCount: (state) => state.notifications.filter((n) => !n.read).length,
  },
  actions: {
    applyAppearance() {
      const root = document.documentElement
      root.classList.toggle('dark', this.isDark)
      root.style.colorScheme = this.isDark ? 'dark' : 'light'
      root.dataset.density = this.density
      const hex = this.accent.slice(1)
      const rgb = [0, 2, 4].map((i) => parseInt(hex.slice(i, i + 2), 16))
      const mix = (target, ratio) =>
        '#' +
        rgb
          .map((c) =>
            Math.round(c + (target - c) * ratio)
              .toString(16)
              .padStart(2, '0'),
          )
          .join('')
      root.style.setProperty('--primary-color', this.accent)
      root.style.setProperty('--primary-hover', mix(this.isDark ? 255 : 0, 0.15))
      root.style.setProperty('--accent-foreground', this.isDark ? mix(255, 0.3) : this.accent)
      root.style.setProperty('--el-color-primary', this.isDark ? mix(255, 0.3) : this.accent)
      root.style.setProperty('--el-color-primary-dark-2', mix(0, 0.2))
      for (const n of [3, 5, 7, 8, 9])
        root.style.setProperty(`--el-color-primary-light-${n}`, mix(this.isDark ? 24 : 255, n / 10))
      root.style.setProperty('--accent-rgb', rgb.join(', '))
      for (const key of ['primary-light', 'menu-active-bg', 'menu-hover-bg'])
        root.style.setProperty(
          `--${key}`,
          `rgba(${rgb.join(', ')}, ${this.isDark ? '.16' : '.07'})`,
        )
      for (const key of ['menu-active-text', 'menu-active-bar', 'menu-hover-text'])
        root.style.setProperty(`--${key}`, this.isDark ? mix(255, 0.4) : this.accent)
    },
    initializeAppearance() {
      this.applyAppearance()
      const query = window.matchMedia('(prefers-color-scheme: dark)')
      const listener = (event) => {
        this.systemDark = event.matches
        this.applyAppearance()
      }
      query.addEventListener('change', listener)
      return () => query.removeEventListener('change', listener)
    },
    updateAppearance(changes) {
      Object.assign(
        this,
        normalizeAppearance({
          theme: this.theme,
          accent: this.accent,
          density: this.density,
          showPageTitle: this.showPageTitle,
          ...changes,
        }),
      )
      writePreference('appearance', {
        theme: this.theme,
        accent: this.accent,
        density: this.density,
        showPageTitle: this.showPageTitle,
      })
      this.applyAppearance()
    },
    setTheme(theme) {
      this.updateAppearance({ theme })
    },
    async toggleTheme(event) {
      if (this.themeChanging) return
      const dark = !this.isDark
      const trigger = event?.currentTarget
      this.themeChanging = true
      try {
        await transitionTheme({
          dark,
          trigger,
          update: async () => {
            this.setTheme(dark ? 'dark' : 'light')
            await nextTick()
          },
        })
      } finally {
        this.themeChanging = false
      }
    },
    toggleSidebar() {
      this.sidebarCollapsed = !this.sidebarCollapsed
    },
    toggleFavorite(path) {
      this.favoritePaths = this.favoritePaths.includes(path)
        ? this.favoritePaths.filter((item) => item !== path)
        : [...this.favoritePaths, path]
      writePreference('favorites', this.favoritePaths)
    },
    markAllNotificationsAsRead() {
      this.notifications.forEach((n) => {
        n.read = true
      })
    },
    clearNotifications() {
      this.notifications = []
    },
    async reloadView() {
      if (this.viewReloading) return
      this.viewReloading = true
      try {
        if (await confirmViewDiscard()) {
          this.viewKey++
          await nextTick()
        }
      } finally {
        this.viewReloading = false
      }
    },
  },
})
