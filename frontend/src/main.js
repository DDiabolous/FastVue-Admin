import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus, { ElTooltip } from 'element-plus'
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/dark/css-vars.css'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

import App from './App.vue'
import { authDirective } from './directives/auth'
import router from './router'
import './style.css'
import './styles/admin.css'
import './styles/transitions.css'
import './styles/business.css'
import './styles/examples.css'
import { useAppStore } from './stores/app'

const app = createApp(App)
const pinia = createPinia()

// Register all Element Plus icons
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 文字提示在鼠标停留 1 秒后显示，避免划过时频繁闪烁。
if (ElTooltip?.props?.showAfter) {
  // Popover/Popconfirm share this prop definition. Replace it for Tooltip only.
  ElTooltip.props.showAfter = { ...ElTooltip.props.showAfter, default: 1000 }
}

app.use(pinia)
useAppStore().initializeAppearance()
app.directive('auth', authDirective)
app.use(router)
app.use(ElementPlus, {
  locale: zhCn,
})

app.mount('#app')
