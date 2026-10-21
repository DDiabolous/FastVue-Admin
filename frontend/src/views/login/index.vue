<template>
  <div class="starter-login">
    <section class="starter-login-brand">
      <div class="starter-login-logo">
        <el-icon :size="30"><Management /></el-icon>
        <span>{{ appConfig.name }}</span>
      </div>
      <div>
        <span class="starter-eyebrow">ADMIN STARTER</span>
        <h1>
          从通用底座，
          <br />
          开始你的业务。
        </h1>
        <p>
          简洁的界面、清晰的模块、可替换的数据层。
          <br />
          为各类后台管理系统提供开发起点。
        </p>
        <div class="starter-login-features">
          <span>系统管理</span>
          <span>角色权限</span>
          <span>页面示例</span>
        </div>
      </div>
      <small>Vue 3 · Element Plus · Vite</small>
    </section>
    <section class="starter-login-panel">
      <div class="starter-login-form">
        <h2>欢迎登录</h2>
        <p class="starter-muted">请输入你的账号和密码</p>
        <el-alert
          v-if="appConfig.useMock"
          title="演示环境：数据仅保存在当前浏览器。"
          type="info"
          :closable="false"
          show-icon
          class="starter-gap"
        />
        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          label-position="top"
          size="large"
          @submit.prevent="login"
        >
          <el-form-item label="账号" prop="username">
            <el-input
              v-model="form.username"
              placeholder="请输入账号"
              autocomplete="username"
              :prefix-icon="User"
            />
          </el-form-item>
          <el-form-item label="密码" prop="password">
            <el-input
              v-model="form.password"
              type="password"
              show-password
              placeholder="请输入密码"
              autocomplete="current-password"
              :prefix-icon="Lock"
            />
          </el-form-item>
          <el-button
            type="primary"
            native-type="submit"
            :loading="loading"
            class="starter-login-submit"
          >
            登录
          </el-button>
        </el-form>
        <div v-if="appConfig.useMock" class="starter-demo-accounts">
          <p>体验不同权限</p>
          <div>
            <el-button v-for="account in accounts" :key="account.username" @click="fill(account)">
              {{ account.label }}
            </el-button>
          </div>
          <small>
            初始账号：admin / admin123、editor / editor123、viewer /
            viewer123。修改密码后使用新密码登录。
          </small>
        </div>
      </div>
    </section>
  </div>
</template>
<script setup>
import { reactive, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { User, Lock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { appConfig } from '@/config/app'
import { useUserStore } from '@/stores/user'
const router = useRouter(),
  route = useRoute(),
  user = useUserStore()
const loading = ref(false),
  formRef = ref()
const form = reactive({
  username: appConfig.useMock ? 'admin' : '',
  password: appConfig.useMock ? 'admin123' : '',
})
const accounts = [
  { username: 'admin', password: 'admin123', label: '管理员' },
  { username: 'editor', password: 'editor123', label: '编辑' },
  { username: 'viewer', password: 'viewer123', label: '只读' },
]
const rules = {
  username: [{ required: true, message: '请输入账号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}
function fill(account) {
  Object.assign(form, { username: account.username, password: account.password })
}
async function login() {
  if (!(await formRef.value.validate().catch(() => false))) return
  loading.value = true
  try {
    await user.login(form.username, form.password)
    const redirect =
      typeof route.query.redirect === 'string' &&
      route.query.redirect.startsWith('/') &&
      !route.query.redirect.startsWith('//') &&
      !route.query.redirect.startsWith('/login')
        ? route.query.redirect
        : '/dashboard'
    await router.replace(redirect)
  } catch (err) {
    ElMessage.error(err.message || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>
