import { defineStore } from 'pinia'

export const useTagsViewStore = defineStore('tagsView', {
  state: () => ({
    visitedViews: [
      {
        name: 'Dashboard',
        path: '/dashboard',
        title: '工作台',
        affix: true
      }
    ]
  }),
  actions: {
    addView(view) {
      if (!view.meta || !view.meta.title) return
      this.visitedViews = this.visitedViews.filter(v => v.path !== view.path || v.affix)
      if (this.visitedViews.some(v => v.path === view.path)) return
      this.visitedViews.push({
        name: view.name,
        path: view.path,
        title: view.meta.title,
        affix: view.meta.affix || false
      })
    },
    delView(view) {
      const index = this.visitedViews.findIndex((v) => v.path === view.path)
      if (index > -1) {
        this.visitedViews.splice(index, 1)
      }
    },
    delOthersViews(view) {
      this.visitedViews = this.visitedViews.filter((v) => v.affix || v.path === view.path)
    },
    delAllViews() {
      this.visitedViews = this.visitedViews.filter((v) => v.affix)
    }
  }
})
