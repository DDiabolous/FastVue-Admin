import { createRouter, createWebHistory } from 'vue-router'
import { ElMessage } from 'element-plus'
import Layout from '@/layout/index.vue'
import { modules } from '@/config/modules'
import { appConfig } from '@/config/app'
import { useTagsViewStore } from '@/stores/tagsView'
import { useAdminStore } from '@/stores/admin'

export const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/admin-login/index.vue'),
    meta: { title: '登录', public: true },
  },
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [
      { path: 'examples/cards', redirect: '/examples/list' },
      ...modules.map(({ path, name, component, props, ...meta }) => ({
        path: path.slice(1),
        name,
        component,
        props,
        meta,
      })),
      ...[403, 404].map((code) => ({
        path: String(code),
        name: `Error${code}`,
        component: () => import('@/views/error/index.vue'),
        props: { code },
        meta: { title: String(code) },
      })),
    ],
  },
  { path: '/:pathMatch(.*)*', redirect: '/404' },
]
const router = createRouter({ history: createWebHistory(), routes })
router.beforeEach(async (to) => {
  const user = useAdminStore()
  if (to.meta.public) return true
  if (!user.token) return { path: '/login', query: { redirect: to.fullPath } }
  if (!user.loaded) {
    try {
      await user.fetchUser()
    } catch (error) {
      if (error.code === 401) {
        user.clearSession()
        return { path: '/login', query: { redirect: to.fullPath } }
      }
      ElMessage.error(error.message || '无法获取用户信息，请稍后重试')
      return false
    }
  }
  if (!user.can(to.meta.permission)) return '/403'
})
router.afterEach((to) => {
  document.title = `${to.meta.title || '工作台'} - ${appConfig.name}`
  if (to.name && !to.meta.public && !String(to.name).startsWith('Error'))
    useTagsViewStore().addView(to)
})
window.addEventListener('admin-auth-expired', () => {
  useAdminStore().clearSession()
  if (router.currentRoute.value.path !== '/login')
    router.replace({ path: '/login', query: { redirect: router.currentRoute.value.fullPath } })
})
export default router
