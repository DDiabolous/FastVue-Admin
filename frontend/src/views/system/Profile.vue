<template>
  <PageContainer title="个人中心" description="管理个人资料、界面偏好及登录密码。">
    <el-card shadow="never">
      <el-tabs v-model="tab">
        <el-tab-pane label="个人资料" name="profile">
          <el-form
            ref="profileRef"
            :model="profile"
            :rules="profileRules"
            label-width="100px"
            class="starter-form"
            @submit.prevent="saveProfile"
          >
            <el-form-item label="账号">
              <el-input :model-value="user.currentUsername" disabled />
            </el-form-item>
            <el-form-item label="姓名" prop="realName">
              <el-input v-model="profile.realName" />
            </el-form-item>
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="profile.email" />
            </el-form-item>
            <el-form-item label="角色">
              <el-tag>{{ user.currentRoleName }}</el-tag>
            </el-form-item>
            <el-form-item label="界面主题">
              <el-radio-group :model-value="app.theme" @update:model-value="app.setTheme">
                <el-radio-button value="light">浅色</el-radio-button>
                <el-radio-button value="dark">深色</el-radio-button>
                <el-radio-button value="system">跟随系统</el-radio-button>
              </el-radio-group>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" native-type="submit" :loading="saving">保存资料</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        <el-tab-pane label="修改密码" name="security">
          <el-form
            ref="passwordRef"
            :model="password"
            :rules="passwordRules"
            label-width="100px"
            class="starter-form"
            @submit.prevent="savePassword"
          >
            <el-form-item label="当前密码" prop="oldPassword">
              <el-input v-model="password.oldPassword" type="password" show-password />
            </el-form-item>
            <el-form-item label="新密码" prop="newPassword">
              <el-input
                v-model="password.newPassword"
                type="password"
                show-password
                placeholder="至少 8 位"
              />
            </el-form-item>
            <el-form-item label="确认密码" prop="confirm">
              <el-input v-model="password.confirm" type="password" show-password />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" native-type="submit" :loading="saving">
                修改并重新登录
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </PageContainer>
</template>
<script setup>
import { reactive, ref, watch, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { useAppStore } from '@/stores/app'
import { useUnsavedChanges } from '@/composables/useUnsavedChanges'
import PageContainer from '@/components/admin/PageContainer.vue'
const user = useUserStore(),
  app = useAppStore(),
  router = useRouter(),
  route = useRoute()
const tab = ref(route.query.tab === 'security' ? 'security' : 'profile'),
  saving = ref(false),
  profileRef = ref(),
  passwordRef = ref()
const profile = reactive({ realName: user.currentRealName, email: user.userInfo?.email || '' })
watch(
  () => route.query.tab,
  (value) => {
    tab.value = value === 'security' ? 'security' : 'profile'
  },
)
const password = reactive({ oldPassword: '', newPassword: '', confirm: '' })
const initialProfile = ref(JSON.stringify(profile))
useUnsavedChanges(
  computed(
    () => JSON.stringify(profile) !== initialProfile.value || Object.values(password).some(Boolean),
  ),
)
const profileRules = {
  realName: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  email: [{ type: 'email', message: '邮箱格式不正确', trigger: 'blur' }],
}
const passwordRules = {
  oldPassword: [{ required: true, message: '请输入当前密码', trigger: 'blur' }],
  newPassword: [{ required: true, min: 8, message: '新密码至少 8 位', trigger: 'blur' }],
  confirm: [
    {
      validator: (_, value, callback) =>
        callback(
          value && value === password.newPassword ? undefined : new Error('两次输入的密码不一致'),
        ),
      trigger: 'blur',
    },
  ],
}
async function saveProfile() {
  if (!(await profileRef.value.validate().catch(() => false))) return
  saving.value = true
  try {
    await user.updateUserProfile({ ...profile })
    initialProfile.value = JSON.stringify(profile)
    ElMessage.success('资料已保存')
  } catch (err) {
    ElMessage.error(err.message)
  } finally {
    saving.value = false
  }
}
async function savePassword() {
  if (!(await passwordRef.value.validate().catch(() => false))) return
  saving.value = true
  try {
    await user.changePassword(password.oldPassword, password.newPassword)
    Object.assign(password, { oldPassword: '', newPassword: '', confirm: '' })
    initialProfile.value = JSON.stringify(profile)
    ElMessage.success('密码已更新，请重新登录')
    router.replace('/login')
  } catch (err) {
    ElMessage.error(err.message)
  } finally {
    saving.value = false
  }
}
</script>
