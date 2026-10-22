<template>
  <PageContainer title="个人中心" description="管理个人资料、登录设备与账号安全。">
    <div class="profile-layout">
      <el-card shadow="never" class="identity-card">
        <div class="identity-cover" :class="{ 'is-busy': coverLoading || mediaSaving === 'coverImage' }"
          :aria-busy="coverLoading || mediaSaving === 'coverImage'">
          <img v-if="user.userInfo?.coverImage" :src="user.userInfo?.coverImage" alt="个人背景墙" />
          <el-upload class="cover-uploader" action="#" :auto-upload="false" :show-file-list="false"
            :disabled="saving || mediaBusy" accept="image/jpeg,image/png,image/webp,image/gif"
            :on-change="handleCoverSelect">
            <button type="button" class="cover-edit-trigger" :disabled="saving || mediaBusy" aria-label="更换背景">
              <span class="cover-edit-label">
                <el-icon :class="{ 'is-loading': coverLoading || mediaSaving === 'coverImage' }">
                  <Loading v-if="coverLoading || mediaSaving === 'coverImage'" /><Camera v-else />
                </el-icon>
                {{ coverLoading || mediaSaving === 'coverImage' ? '保存中' : '更换背景' }}
              </span>
            </button>
          </el-upload>
          <button v-if="user.userInfo?.coverImage" type="button" class="cover-reset"
            :disabled="saving || mediaBusy" @click="saveAppearance('coverImage', '')">
            <el-icon><RefreshLeft /></el-icon>重置
          </button>
        </div>
        <div class="identity-body">
          <div class="identity-overview">
            <el-upload class="avatar-uploader" action="#" :auto-upload="false" :show-file-list="false"
              :disabled="saving || mediaBusy" accept="image/jpeg,image/png,image/webp,image/gif"
              :on-change="handleAvatarSelect">
              <button type="button" class="avatar-edit-trigger" :class="{ 'is-busy': mediaSaving === 'avatar' }"
                :disabled="saving || mediaBusy" :aria-busy="mediaSaving === 'avatar'" aria-label="更换头像">
                <el-avatar :size="112" :src="user.currentAvatar" class="identity-avatar">
                  {{ (user.currentRealName || user.currentUsername)?.slice(0, 2) }}
                </el-avatar>
                <span class="avatar-edit-label">
                  <el-icon :class="{ 'is-loading': mediaSaving === 'avatar' }">
                    <Loading v-if="mediaSaving === 'avatar'" /><Camera v-else />
                  </el-icon>
                  {{ mediaSaving === 'avatar' ? '保存中' : '更换头像' }}
                </span>
              </button>
            </el-upload>
            <div class="identity-heading">
              <h2>{{ user.currentRealName || user.currentUsername }}</h2>
              <el-tag effect="light" size="small" :disable-transitions="true">{{ user.currentRoleName }}</el-tag>
            </div>
          </div>
          <dl class="identity-details">
            <div><dt>登录账号：</dt><dd>{{ user.currentUsername }}</dd></div>
            <div><dt>性别：</dt><dd>{{ genderLabel }}</dd></div>
            <div><dt>手机号：</dt><dd>{{ user.userInfo?.phone || '未设置' }}</dd></div>
            <div><dt>所在地：</dt><dd>{{ user.userInfo?.location || '未设置' }}</dd></div>
            <div><dt>联系邮箱：</dt><dd>{{ user.userInfo?.email || '未设置' }}</dd></div>
            <div><dt>个人介绍：</dt><dd class="identity-bio">{{ user.userInfo?.bio || '还没有填写个人介绍' }}</dd></div>
          </dl>
          <p class="identity-note">头像与背景更换后自动保存。</p>
        </div>
      </el-card>

      <el-card shadow="never" class="settings-card">
        <el-tabs v-model="tab">
          <el-tab-pane label="个人资料" name="profile">
            <div class="pane-heading">
              <h2>基本资料</h2>
              <p>完善基本信息，让团队更了解你。</p>
            </div>
            <el-form
              ref="profileRef" :model="profile" :rules="profileRules"
              label-position="top" class="profile-form" :disabled="saving"
              @submit.prevent="saveProfile"
            >
              <div class="profile-fields">
                <el-form-item label="姓名" prop="realName">
                  <el-input v-model="profile.realName" placeholder="请输入姓名" autocomplete="name" maxlength="100" />
                </el-form-item>
                <el-form-item label="性别" prop="gender">
                  <el-select v-model="profile.gender" aria-label="性别">
                    <el-option label="保密" value="unspecified" />
                    <el-option label="男" value="male" />
                    <el-option label="女" value="female" />
                    <el-option label="其他" value="other" />
                  </el-select>
                </el-form-item>
                <el-form-item label="邮箱" prop="email">
                  <el-input v-model="profile.email" placeholder="example@domain.com" autocomplete="email" maxlength="254" />
                </el-form-item>
                <el-form-item label="手机号" prop="phone">
                  <el-input v-model="profile.phone" placeholder="请输入手机号" autocomplete="tel" type="tel" maxlength="32" />
                </el-form-item>
                <el-form-item label="所在地" prop="location" class="full-width">
                  <el-input v-model="profile.location" placeholder="如：上海" autocomplete="address-level2" maxlength="100" />
                </el-form-item>
                <el-form-item label="个人介绍" prop="bio" class="full-width">
                  <el-input v-model="profile.bio" type="textarea" :rows="4" maxlength="500" show-word-limit
                    placeholder="介绍一下自己，如工作方向、兴趣爱好等" resize="vertical" />
                </el-form-item>
              </div>
              <div class="form-footer">
                <span class="save-state" role="status">{{ profileDirty ? '有修改尚未保存' : '资料已同步' }}</span>
                <div class="footer-actions">
                  <el-button v-if="profileDirty" @click="resetProfile">取消修改</el-button>
                  <el-button type="primary" native-type="submit" :loading="saving" :disabled="!profileDirty || mediaBusy">
                    保存资料
                  </el-button>
                </div>
              </div>
            </el-form>
          </el-tab-pane>

          <el-tab-pane label="登录会话" name="sessions">
            <div class="pane-heading session-heading">
              <div><h2>登录设备</h2><p>查看有效会话，可随时退出不再使用的设备。</p></div>
              <el-button icon="Refresh" :loading="loadingSessions" @click="fetchSessions">刷新</el-button>
            </div>
            <el-alert v-if="sessionError" :title="sessionError" type="error" show-icon :closable="false" />
            <div v-else v-loading="loadingSessions" class="session-list" aria-live="polite">
              <article v-for="session in sessionList" :key="session.tokenHash" class="session-item">
                <div class="device-icon"><el-icon :size="22"><Monitor /></el-icon></div>
                <div class="session-info">
                  <div class="session-title">
                    <h3>{{ session.device || 'Web 浏览器' }}</h3>
                    <el-tag v-if="session.isCurrent" size="small" type="success">当前设备</el-tag>
                  </div>
                  <div class="session-meta">
                    <span>IP：{{ session.ip || '未提供' }}</span>
                    <span>登录时间：{{ formatSessionTime(session.createdAt) }}</span>
                  </div>
                </div>
                <el-popconfirm
                  :title="session.isCurrent ? '退出当前设备将返回登录页，确定继续吗？' : '确定退出此设备吗？'"
                  confirm-button-text="退出" cancel-button-text="取消" confirm-button-type="danger"
                  @confirm="handleRevoke(session)"
                >
                  <template #reference>
                    <el-button class="session-revoke" plain type="danger" size="small"
                      :loading="revokingSession === session.tokenHash" :disabled="!!revokingSession">
                      {{ session.isCurrent ? '退出登录' : '退出设备' }}
                    </el-button>
                  </template>
                </el-popconfirm>
              </article>
              <el-empty v-if="!loadingSessions && !sessionList.length" description="暂无有效会话" :image-size="80" />
            </div>
          </el-tab-pane>

          <el-tab-pane label="账号安全" name="security">
            <div class="pane-heading"><h2>修改密码</h2><p>定期更新密码，保护账号安全。</p></div>
            <el-alert class="password-notice" title="修改密码后，所有设备需要重新登录。" type="info" show-icon :closable="false" />
            <el-form
              ref="passwordRef" :model="password" :rules="passwordRules"
              label-position="top" class="profile-form" :disabled="saving" @submit.prevent="savePassword"
            >
              <el-form-item label="当前密码" prop="oldPassword">
                <el-input v-model="password.oldPassword" type="password" show-password autocomplete="current-password" />
              </el-form-item>
              <el-form-item label="新密码" prop="newPassword">
                <el-input v-model="password.newPassword" type="password" show-password placeholder="至少 8 位" autocomplete="new-password" />
              </el-form-item>
              <el-form-item label="确认新密码" prop="confirm">
                <el-input v-model="password.confirm" type="password" show-password placeholder="再次输入新密码" autocomplete="new-password" />
              </el-form-item>
              <div class="form-footer password-footer">
                <el-button type="primary" native-type="submit" :loading="saving" :disabled="mediaBusy">更新密码</el-button>
              </div>
            </el-form>
          </el-tab-pane>
        </el-tabs>
      </el-card>
    </div>
    <AvatarCropper v-model="cropperVisible" :image-src="rawAvatarSrc" :output-size="640" @confirm="handleCropConfirm" />
  </PageContainer>
</template>

<script setup>
import { reactive, ref, watch, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Camera, Loading, Monitor, RefreshLeft } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { authApi } from '@/api/system'
import { useUnsavedChanges } from '@/composables/useUnsavedChanges'
import PageContainer from '@/components/admin/PageContainer.vue'
import AvatarCropper from '@/components/admin/AvatarCropper.vue'

const user = useUserStore()
const router = useRouter()
const route = useRoute()

const resolveTab = (value) => ['profile', 'sessions', 'security'].includes(value) ? value : 'profile'
const tab = ref(resolveTab(route.query.tab))
const saving = ref(false)
const profileRef = ref()
const passwordRef = ref()
const genderLabel = computed(() => ({
  unspecified: '保密', male: '男', female: '女', other: '其他',
})[user.userInfo?.gender] || '保密')

const profile = reactive({
  realName: user.currentRealName,
  email: user.userInfo?.email || '',
  gender: user.userInfo?.gender || 'unspecified',
  phone: user.userInfo?.phone || '',
  location: user.userInfo?.location || '',
  bio: user.userInfo?.bio || '',
})

const coverLoading = ref(false)
const mediaSaving = ref('')
const mediaBusy = computed(() => coverLoading.value || !!mediaSaving.value)

async function saveAppearance(field, value) {
  if (saving.value || mediaSaving.value) return
  mediaSaving.value = field
  try {
    // 只提交图片字段，避免把尚未保存的姓名、邮箱一并提交。
    await user.updateUserProfile({ [field]: value })
    ElMessage.success(field === 'avatar' ? '头像已更新' : value ? '背景已更新' : '背景已重置')
  } catch (err) {
    ElMessage.error(err.message || '保存失败，请重试')
  } finally {
    mediaSaving.value = ''
  }
}

async function handleCoverSelect(uploadFile) {
  const file = uploadFile.raw
  if (!file || saving.value || mediaBusy.value) return
  if (!['image/jpeg', 'image/png', 'image/webp', 'image/gif'].includes(file.type)) {
    ElMessage.error('请选择 JPG、PNG、WebP 或 GIF 图片')
    return
  }
  if (file.size > 20 * 1024 * 1024) {
    ElMessage.error('背景原图大小不能超过 20MB')
    return
  }
  coverLoading.value = true
  let bitmap
  try {
    bitmap = await createImageBitmap(file)
    // 中心裁剪并压缩，避免将大尺寸原图直接保存到资料中。
    const canvas = document.createElement('canvas')
    canvas.width = 1200
    canvas.height = 600
    const scale = Math.max(canvas.width / bitmap.width, canvas.height / bitmap.height)
    const width = canvas.width / scale
    const height = canvas.height / scale
    canvas.getContext('2d').drawImage(bitmap,
      (bitmap.width - width) / 2, (bitmap.height - height) / 2, width, height,
      0, 0, canvas.width, canvas.height)
    await saveAppearance('coverImage', canvas.toDataURL('image/webp', 0.85))
  } catch {
    ElMessage.error('图片读取失败，请更换图片后重试')
  } finally {
    bitmap?.close()
    coverLoading.value = false
  }
}

// 裁剪弹窗状态
const cropperVisible = ref(false)
const rawAvatarSrc = ref('')

watch(
  () => route.query.tab,
  (value) => {
    tab.value = resolveTab(value)
  },
)

// 选择头像图片并进行类型与放宽后大小校验 (放宽至 20MB)
function handleAvatarSelect(uploadFile) {
  const file = uploadFile.raw
  if (!file || saving.value || mediaBusy.value) return

  const allowedTypes = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
  if (!allowedTypes.includes(file.type)) {
    ElMessage.error('仅支持上传 JPG、PNG、WebP 或 GIF 格式的图片文件')
    return
  }

  // 大小限制放宽至 20MB
  const isLt20M = file.size / 1024 / 1024 <= 20
  if (!isLt20M) {
    ElMessage.error('头像原图大小不能超过 20MB')
    return
  }

  const reader = new FileReader()
  reader.onload = (e) => {
    rawAvatarSrc.value = e.target.result
    cropperVisible.value = true
  }
  reader.readAsDataURL(file)
}

// 确认裁剪结果
async function handleCropConfirm(croppedBase64) {
  await saveAppearance('avatar', croppedBase64)
}

// 会话管理
const sessionList = ref([])
const loadingSessions = ref(false)
const sessionError = ref('')
const revokingSession = ref('')

function formatSessionTime(value) {
  if (!value) return '未提供'
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString('zh-CN', { hour12: false })
}

async function fetchSessions() {
  if (loadingSessions.value) return
  loadingSessions.value = true
  sessionError.value = ''
  try {
    const res = await authApi.sessions()
    sessionList.value = Array.isArray(res) ? res : res?.data || []
  } catch (err) {
    sessionError.value = err.message || '无法加载登录会话，请稍后重试'
  } finally {
    loadingSessions.value = false
  }
}

async function handleRevoke(row) {
  if (revokingSession.value) return
  revokingSession.value = row.tokenHash
  try {
    await authApi.revokeSession(row.tokenHash)
    ElMessage.success('会话已成功撤销')
    if (row.isCurrent) {
      user.clearSession()
      router.replace('/login')
    } else {
      fetchSessions()
    }
  } catch (err) {
    ElMessage.error(err.message || '撤销会话失败')
  } finally {
    revokingSession.value = ''
  }
}

watch(tab, (newTab) => {
  if (newTab === 'sessions') {
    fetchSessions()
  }
})

const password = reactive({ oldPassword: '', newPassword: '', confirm: '' })
const initialProfile = ref(JSON.stringify(profile))
const profileDirty = computed(() => JSON.stringify(profile) !== initialProfile.value)

function resetProfile() {
  Object.assign(profile, JSON.parse(initialProfile.value))
  profileRef.value?.clearValidate()
}

useUnsavedChanges(
  computed(
    () => profileDirty.value || Object.values(password).some(Boolean),
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
  if (saving.value || mediaBusy.value || !profileDirty.value) return
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
  if (saving.value || mediaBusy.value) return
  if (!(await passwordRef.value.validate().catch(() => false))) return
  saving.value = true
  try {
    await user.changePassword(password.oldPassword, password.newPassword)
    Object.assign(password, { oldPassword: '', newPassword: '', confirm: '' })
    ElMessage.success('密码已更新，请重新登录')
    router.replace('/login')
  } catch (err) {
    ElMessage.error(err.message)
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  if (tab.value === 'sessions') {
    fetchSessions()
  }
})
</script>

<style scoped>
.profile-layout { display: grid; grid-template-columns: 40% minmax(0, 1fr); gap: 24px; align-items: start; }
.identity-card, .settings-card { min-width: 0; }
.identity-card :deep(.el-card__body) { padding: 0; }
.identity-cover { position: relative; height: 200px; overflow: hidden; background: radial-gradient(ellipse at 85% 15%, #93c5fd 0%, transparent 60%), linear-gradient(125deg, #1e3a8a, #3b82f6 65%, #60a5fa); }
.identity-cover > img { display: block; width: 100%; height: 100%; object-fit: cover; }
.cover-uploader { position: absolute; inset: 0; }
.cover-uploader :deep(.el-upload) { display: block; width: 100%; height: 100%; }
.cover-edit-trigger { display: flex; align-items: center; justify-content: center; width: 100%; height: 100%; padding: 0; border: 0; background: transparent; cursor: pointer; transition: background 0.2s; }
.cover-edit-label, .cover-reset { display: inline-flex; align-items: center; gap: 8px; padding: 10px 16px; border-radius: 20px; color: #fff; background: rgba(15, 23, 42, 0.6); font-size: 13px; opacity: 0; transition: opacity 0.2s; }
.cover-reset { position: absolute; top: 14px; right: 14px; border: 0; cursor: pointer; pointer-events: none; }
.identity-cover:is(:hover, .is-busy) .cover-edit-label,
.identity-cover:hover .cover-reset,
.identity-cover:has(:focus-visible) :is(.cover-edit-label, .cover-reset) { opacity: 1; pointer-events: auto; }
.cover-edit-trigger:hover { background: rgba(15, 23, 42, 0.12); }
.avatar-edit-trigger { position: relative; display: flex; border: 0; border-radius: 50%; padding: 0; background: transparent; cursor: pointer; }
.avatar-edit-label { position: absolute; inset: 5px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 6px; border-radius: 50%; background: rgba(15, 23, 42, 0.55); color: #fff; font-size: 13px; opacity: 0; transition: opacity 0.2s; }
.avatar-edit-trigger:is(:hover, :focus-visible, .is-busy) .avatar-edit-label,
.avatar-uploader:has(:focus-visible) .avatar-edit-label { opacity: 1; }
.avatar-edit-trigger:focus-visible, .cover-edit-trigger:focus-visible, .cover-reset:focus-visible { outline: 2px solid var(--el-color-primary); outline-offset: -2px; }
.avatar-edit-trigger:disabled, .cover-edit-trigger:disabled { cursor: wait; }
@media (hover: none) {
  .cover-edit-label, .cover-reset, .avatar-edit-label { opacity: 1; pointer-events: auto; }
  .avatar-edit-label { inset: auto 5px 5px; height: 30px; border-radius: 0 0 48px 48px; font-size: 11px; }
  .avatar-edit-label .el-icon { display: none; }
}
.identity-body { padding: 0 28px 28px; }
.identity-overview { position: relative; margin-top: -56px; }
.avatar-edit-trigger .identity-avatar { border-width: 5px; }

.identity-overview { display: flex; flex-direction: column; align-items: center; gap: 16px; text-align: center; }
.identity-avatar { flex-shrink: 0; background: var(--el-color-primary-light-9); color: var(--el-color-primary); font-size: 32px; font-weight: 600; border: 4px solid var(--el-bg-color); box-shadow: 0 0 0 1px var(--el-border-color-lighter); }
.identity-avatar :deep(img) { width: 100%; height: 100%; object-fit: cover; }
.identity-heading { display: flex; align-items: center; justify-content: center; flex-wrap: wrap; gap: 8px 10px; min-width: 0; }
.identity-heading > .el-tag { flex-shrink: 0; }
.identity-heading h2 { margin: 0; font-size: 20px; line-height: 1.4; overflow-wrap: anywhere; color: var(--el-text-color-primary); }
.identity-details { display: flex; flex-direction: column; gap: 16px; margin: 28px 0 0; padding-top: 24px; border-top: 1px solid var(--el-border-color-lighter); }
.identity-details > div { display: flex; align-items: baseline; min-width: 0; line-height: 1.8; }
.identity-details dt { flex-shrink: 0; font-size: 14px; color: var(--el-text-color-secondary); }
.identity-details dd { flex: 1; min-width: 0; margin: 0; font-size: 14px; color: var(--el-text-color-primary); overflow-wrap: anywhere; }
.identity-details .identity-bio { white-space: pre-wrap; line-height: 1.8; }
.identity-note { margin: 24px 0 0; color: var(--el-text-color-secondary); font-size: 12px; line-height: 1.7; }
.settings-card :deep(.el-card__body) { padding: 12px 28px 28px; }
.settings-card :deep(.el-tabs__header) { margin: 0 0 28px; }
.settings-card :deep(.el-tabs__item) { height: 52px; }
.pane-heading { margin-bottom: 28px; }
.pane-heading h2 { margin: 0 0 8px; color: var(--el-text-color-primary); font-size: 17px; font-weight: 600; }
.pane-heading p { margin: 0; color: var(--el-text-color-secondary); font-size: 13px; line-height: 1.7; }
.profile-form { max-width: 600px; }
.profile-fields { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0 20px; }
.profile-fields > * { min-width: 0; }
.profile-fields .full-width { grid-column: 1 / -1; }
.profile-fields :deep(.el-select) { width: 100%; }
.profile-form :deep(.el-form-item) { margin-bottom: 24px; }
.profile-form :deep(.el-form-item__label) { padding-bottom: 8px; line-height: 22px; }
.form-footer { display: flex; justify-content: space-between; align-items: center; gap: 16px; margin-top: 32px; padding-top: 24px; border-top: 1px solid var(--el-border-color-lighter); }
.save-state { color: var(--el-text-color-secondary); font-size: 12px; }
.footer-actions { display: flex; gap: 12px; }
.footer-actions .el-button + .el-button { margin-left: 0; }
.session-heading { display: flex; justify-content: space-between; align-items: start; gap: 16px; }
.session-list { min-height: 120px; }
.session-item { display: flex; align-items: center; gap: 16px; padding: 22px 0; border-bottom: 1px solid var(--el-border-color-lighter); }
.session-item:first-child { padding-top: 0; }
.session-item:last-child { border-bottom: 0; padding-bottom: 4px; }
.device-icon { display: flex; align-items: center; justify-content: center; flex-shrink: 0; width: 48px; height: 48px; border-radius: 12px; background: var(--el-fill-color-light); color: var(--el-text-color-regular); }
.session-info { flex: 1; min-width: 0; }
.session-title { display: flex; align-items: center; flex-wrap: wrap; gap: 10px; }
.session-title h3 { margin: 0; font-size: 14px; font-weight: 500; line-height: 1.6; overflow-wrap: anywhere; }
.session-meta { display: flex; flex-wrap: wrap; gap: 6px 20px; margin-top: 8px; font-size: 12px; line-height: 1.6; color: var(--el-text-color-secondary); overflow-wrap: anywhere; }
.session-revoke { flex-shrink: 0; }
.password-notice { max-width: 600px; margin-bottom: 24px; box-sizing: border-box; }
.password-footer { justify-content: flex-end; }
@media (max-width: 1100px) {
  .profile-layout { gap: 20px; }
}
@media (max-width: 900px) {
  .profile-layout { grid-template-columns: minmax(0, 1fr); }
  .identity-cover { height: 190px; }
}
@media (max-width: 600px) {
  .profile-fields { grid-template-columns: minmax(0, 1fr); }
  .identity-cover { height: 160px; }
  .identity-body { padding: 0 24px 24px; }
  .identity-overview { margin-top: -48px; }
  .identity-avatar { width: 96px !important; height: 96px !important; }
  .settings-card :deep(.el-card__body) { padding: 8px 20px 20px; }
  .form-footer { flex-wrap: wrap; margin-top: 24px; gap: 16px; }
  .footer-actions { margin-left: auto; }
  .session-item { flex-wrap: wrap; gap: 12px; align-items: start; }
  .session-revoke { margin-left: 60px; }
  .session-meta { flex-direction: column; }
  .session-heading { align-items: center; }
}
</style>
