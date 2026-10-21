import { onMounted, onUnmounted } from 'vue'
import { onBeforeRouteLeave } from 'vue-router'
import { ElMessageBox } from 'element-plus'

export function useUnsavedChanges(dirty) {
  async function confirmDiscard() {
    if (!dirty.value) return true
    try {
      await ElMessageBox.confirm('当前修改尚未保存，离开后将丢失。', '放弃修改？', {
        type: 'warning',
        confirmButtonText: '放弃修改',
        cancelButtonText: '继续编辑',
        closeOnClickModal: false,
      })
      return true
    } catch {
      return false
    }
  }
  const beforeUnload = (event) => {
    if (dirty.value) {
      event.preventDefault()
      event.returnValue = ''
    }
  }
  onBeforeRouteLeave((to) => (to.path === '/login' ? true : confirmDiscard()))
  onMounted(() => window.addEventListener('beforeunload', beforeUnload))
  onUnmounted(() => window.removeEventListener('beforeunload', beforeUnload))
  return { confirmDiscard }
}
