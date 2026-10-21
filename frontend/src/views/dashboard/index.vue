<template>
  <PageContainer
    title="工作台"
    :description="`${greeting}，${user.currentRealName}。让常用功能触手可及。`"
  >
    <template #actions>
      <span class="dashboard-date">
        <el-icon><Calendar /></el-icon>
        {{ date }}
      </span>
      <el-button @click="helpVisible = true">
        <el-icon><QuestionFilled /></el-icon>
        项目帮助
      </el-button>
    </template>
    <div class="starter-welcome">
      <div>
        <span class="starter-eyebrow">{{ appConfig.name }}</span>
        <h2>为你的下一个后台项目做好准备</h2>
        <p>统一布局、系统管理与可复用页面示例，按需组合你的业务。</p>
        <el-button type="primary" @click="$router.push('/examples/list')">
          查看列表示例
          <el-icon><ArrowRight /></el-icon>
        </el-button>
      </div>
      <div class="starter-welcome-mark">
        <el-icon :size="76"><Grid /></el-icon>
      </div>
    </div>
    <div class="workspace-grid">
      <section class="workspace-main">
        <el-card shadow="never" class="workspace-card">
          <template #header>
            <div class="card-heading">
              <div>
                <h2>
                  我的收藏
                  <span class="count-pill">{{ favorites.length }}</span>
                </h2>
                <p>把经常使用的页面放在这里</p>
              </div>
              <el-button link type="primary" @click="app.searchVisible = true">
                查找页面
                <el-icon><ArrowRight /></el-icon>
              </el-button>
            </div>
          </template>
          <div v-if="favorites.length" class="shortcut-grid">
            <div v-for="item in favorites" :key="item.path" class="shortcut-item">
              <router-link :to="item.path">
                <span class="shortcut-icon">
                  <el-icon :size="23"><component :is="item.icon" /></el-icon>
                </span>
                <strong>{{ item.title }}</strong>
                <small>{{ item.group || '常用页面' }}</small>
              </router-link>
              <button
                type="button"
                class="unfavorite"
                :aria-label="`取消收藏${item.title}`"
                @click="app.toggleFavorite(item.path)"
              >
                <el-icon><StarFilled /></el-icon>
              </button>
            </div>
          </div>
          <div v-else class="favorites-empty">
            <span class="favorites-empty-icon">
              <el-icon :size="30"><Star /></el-icon>
            </span>
            <h3>让工作台更懂你的习惯</h3>
            <p>点击页面标题旁的星标，即可收藏常用功能。</p>
            <el-button type="primary" plain @click="addDefaults">添加常用入口</el-button>
          </div>
        </el-card>
        <el-card shadow="never" class="workspace-card">
          <template #header>
            <div class="card-heading">
              <div>
                <h2>功能导航</h2>
                <p>按模块浏览当前可用的页面</p>
              </div>
              <span class="starter-muted">{{ available.length }} 个页面</span>
            </div>
          </template>
          <div class="module-groups">
            <section v-for="group in groups" :key="group.title">
              <h3>{{ group.title }}</h3>
              <div class="module-links">
                <router-link v-for="item in group.items" :key="item.path" :to="item.path">
                  <el-icon><component :is="item.icon" /></el-icon>
                  <span>{{ item.title }}</span>
                  <el-icon class="link-arrow"><ArrowRight /></el-icon>
                </router-link>
              </div>
            </section>
          </div>
        </el-card>
      </section>
      <aside class="workspace-aside">
        <el-card shadow="never" class="workspace-card">
          <template #header>
            <div class="card-heading">
              <h2>最近访问</h2>
              <el-icon class="starter-muted"><Clock /></el-icon>
            </div>
          </template>
          <div v-if="recent.length" class="recent-list">
            <router-link v-for="(item, index) in recent" :key="item.path" :to="item.path">
              <span class="recent-index">{{ String(index + 1).padStart(2, '0') }}</span>
              <span>{{ item.title }}</span>
              <el-icon><TopRight /></el-icon>
            </router-link>
          </div>
          <div v-else class="recent-empty">
            <el-icon :size="28"><Clock /></el-icon>
            <p>还没有访问记录</p>
            <small>打开页面后，会在这里显示</small>
          </div>
        </el-card>
        <div class="workspace-tip">
          <span class="tip-icon">
            <el-icon><MagicStick /></el-icon>
          </span>
          <h3>按照你的习惯使用</h3>
          <p>试试菜单搜索、紧凑表格，或为工作空间换一个主题色。</p>
          <el-button @click="app.appearanceVisible = true">
            调整界面
            <el-icon><ArrowRight /></el-icon>
          </el-button>
        </div>
      </aside>
    </div>
    <el-dialog v-model="helpVisible" title="项目帮助" width="min(620px, 94vw)">
      <p class="starter-copy">
        {{ appConfig.description }}。按需添加业务模块，复用现有布局与基础组件。
      </p>
      <div class="help-steps">
        <section v-for="(step, index) in steps" :key="step.title">
          <span>{{ index + 1 }}</span>
          <div>
            <h3>{{ step.title }}</h3>
            <p>{{ step.description }}</p>
            <code>{{ step.file }}</code>
          </div>
        </section>
      </div>
      <el-descriptions :column="1">
        <el-descriptions-item label="当前模式">
          {{ appConfig.fullDemo ? '完整演示' : '精简启动' }}
        </el-descriptions-item>
        <el-descriptions-item label="数据来源">
          {{ appConfig.useMock ? '浏览器 Mock 数据' : '后端 API' }}
        </el-descriptions-item>
        <el-descriptions-item label="开发指南">docs/development.md</el-descriptions-item>
        <el-descriptions-item label="接口约定">docs/api.md</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button type="primary" @click="helpVisible = false">知道了</el-button>
      </template>
    </el-dialog>
  </PageContainer>
</template>
<script setup>
import { computed, ref } from 'vue'
import { useUserStore } from '@/stores/user'
import { useTagsViewStore } from '@/stores/tagsView'
import { useAppStore } from '@/stores/app'
import { appConfig } from '@/config/app'
import { modules } from '@/config/modules'
import PageContainer from '@/components/admin/PageContainer.vue'
const user = useUserStore(),
  tags = useTagsViewStore(),
  app = useAppStore()
const helpVisible = ref(false)
const hour = new Date().getHours(),
  greeting = hour < 12 ? '上午好' : hour < 18 ? '下午好' : '晚上好'
const date = new Intl.DateTimeFormat('zh-CN', {
  month: 'long',
  day: 'numeric',
  weekday: 'long',
}).format(new Date())
const available = computed(() =>
  modules.filter((item) => item.path !== '/dashboard' && user.can(item.permission)),
)
const favorites = computed(() =>
  app.favoritePaths
    .map((path) => available.value.find((item) => item.path === path))
    .filter(Boolean),
)
const groups = computed(() => {
  const result = []
  for (const item of available.value) {
    const title = item.group || '个人空间'
    let group = result.find((group) => group.title === title)
    if (!group) {
      group = { title, items: [] }
      result.push(group)
    }
    group.items.push(item)
  }
  return result
})
const recent = computed(() =>
  tags.visitedViews
    .filter((item) => available.value.some((module) => module.path === item.path))
    .slice(-5)
    .reverse(),
)
function addDefaults() {
  for (const item of available.value.filter((item) =>
    ['/users', '/dictionary', '/examples/list', '/profile'].includes(item.path),
  ))
    if (!app.favoritePaths.includes(item.path)) app.toggleFavorite(item.path)
}
const steps = [
  {
    title: '配置应用',
    description: '修改名称、API 地址及模块开关。',
    file: '.env.local · src/config/app.js',
  },
  {
    title: '添加业务页面',
    description: '参考页面示例，复用页面容器和表格工具栏。',
    file: 'src/views/examples/',
  },
  {
    title: '注册菜单与权限',
    description: '在模块配置中声明路由，菜单自动同步。',
    file: 'src/config/modules.js',
  },
]
</script>
