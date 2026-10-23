<template>
  <div class="page-container profile-page">
    <el-row :gutter="16" class="profile-layout-row">
      <!-- Left Column: User Summary & Security Overview -->
      <el-col :xs="24" :md="8" :lg="7">
        <div class="left-cards-stack">
          <!-- Profile Card -->
          <el-card shadow="never" class="user-id-card">
            <div class="avatar-section">
              <div class="avatar-wrapper" @click="avatarDialogVisible = true">
                <el-avatar :size="96" :src="userStore.currentAvatar" class="main-avatar" />
                <div class="avatar-hover-overlay">
                  <el-icon :size="20"><Camera /></el-icon>
                  <span>更换头像</span>
                </div>
              </div>
              <h3 class="user-display-name">{{ userStore.currentRealName }}</h3>
              <p class="user-account-tag">@{{ userStore.currentUsername }}</p>
              <div class="badges-row">
                <el-tag type="primary" effect="light" class="role-badge" :disable-transitions="true">
                  <el-icon><Stamp /></el-icon>
                  <span>{{ userStore.currentRoleName }}</span>
                </el-tag>
                <el-tag type="info" effect="light" class="dept-badge" :disable-transitions="true">
                  <el-icon><OfficeBuilding /></el-icon>
                  <span>{{ userStore.userInfo?.department || '技术研发与数字化中心' }}</span>
                </el-tag>
              </div>
            </div>

            <p class="user-bio-text">
              “{{ userStore.userInfo?.bio || '致力于构建高性能、高可用且通用的现代化数字管理系统架构。' }}”
            </p>

            <div class="user-meta-list">
              <div class="meta-item">
                <span class="meta-k">
                  <el-icon><Postcard /></el-icon> 员工工号
                </span>
                <span class="meta-v mono">{{ userStore.userInfo?.id || 'USR-1001' }}</span>
              </div>
              <div class="meta-item">
                <span class="meta-k">
                  <el-icon><Iphone /></el-icon> 手机号码
                </span>
                <span class="meta-v">{{ userStore.userInfo?.phone || '13800138000' }}</span>
              </div>
              <div class="meta-item">
                <span class="meta-k">
                  <el-icon><Message /></el-icon> 电子邮箱
                </span>
                <span class="meta-v">{{ userStore.userInfo?.email || 'admin@cloudhub-admin.com' }}</span>
              </div>
              <div class="meta-item">
                <span class="meta-k">
                  <el-icon><Briefcase /></el-icon> 岗位职务
                </span>
                <span class="meta-v">{{ userStore.userInfo?.jobTitle || '平台总架构师' }}</span>
              </div>
              <div class="meta-item">
                <span class="meta-k">
                  <el-icon><Timer /></el-icon> 上次登录
                </span>
                <span class="meta-v time-text">{{ userStore.userInfo?.lastLoginTime || '刚刚' }}</span>
              </div>
            </div>
          </el-card>

          <!-- Security Health Card -->
          <el-card shadow="never" class="security-card">
            <template #header>
              <div class="card-header-flex">
                <div class="title-with-icon">
                  <el-icon color="#10b981"><CircleCheckFilled /></el-icon>
                  <span>账号安全评分</span>
                </div>
                <el-tag type="success" size="small" effect="light">良好等级</el-tag>
              </div>
            </template>

            <div class="security-score-box">
              <div class="score-top">
                <span class="score-num">{{ securityScore }}</span>
                <span class="score-unit">/ 100 分</span>
              </div>
              <el-progress
                :percentage="securityScore"
                :stroke-width="8"
                :color="scoreProgressColor"
                :show-text="false"
              />
              <span class="score-subtip">建议定期更换密码并开启双因子认证</span>
            </div>

            <div class="security-checklist">
              <div class="sec-item">
                <div class="sec-info">
                  <div class="sec-title">
                    <el-icon color="#10b981"><Lock /></el-icon>
                    <span>登录认证密码</span>
                  </div>
                  <span class="sec-status">已设置高强度密码</span>
                </div>
                <el-button link type="primary" size="small" @click="activeTab = 'security'">修改</el-button>
              </div>

              <div class="sec-item">
                <div class="sec-info">
                  <div class="sec-title">
                    <el-icon color="#10b981"><Iphone /></el-icon>
                    <span>密保手机绑定</span>
                  </div>
                  <span class="sec-status">{{ userStore.userInfo?.phone || '已绑定' }}</span>
                </div>
                <el-button link type="primary" size="small" @click="activeTab = 'basic'">更改</el-button>
              </div>

              <div class="sec-item">
                <div class="sec-info">
                  <div class="sec-title">
                    <el-icon color="#10b981"><Message /></el-icon>
                    <span>安全邮箱验证</span>
                  </div>
                  <span class="sec-status">{{ userStore.userInfo?.email || '已验证' }}</span>
                </div>
                <el-button link type="primary" size="small" @click="activeTab = 'basic'">更改</el-button>
              </div>

              <div class="sec-item">
                <div class="sec-info">
                  <div class="sec-title">
                    <el-icon :color="enable2FA ? '#10b981' : '#94a3b8'"><Key /></el-icon>
                    <span>双因子认证 (2FA)</span>
                  </div>
                  <span class="sec-status">{{ enable2FA ? '已开启安全加固' : '未开启 (推荐)' }}</span>
                </div>
                <el-switch v-model="enable2FA" @change="toggle2FA" size="small" />
              </div>
            </div>
          </el-card>
        </div>
      </el-col>

      <!-- Right Column: Tabbed Settings -->
      <el-col :xs="24" :md="16" :lg="17">
        <el-card shadow="never" class="profile-tabs-card">
          <el-tabs v-model="activeTab" class="profile-tabs">
            <!-- Tab 1: Basic Profile Information -->
            <el-tab-pane label="基本资料" name="basic">
              <div class="tab-pane-inner">
                <div class="pane-headline">
                  <h4 class="pane-title">编辑个人基本资料</h4>
                  <p class="pane-sub">维护并更新您在企业内部花名册与系统中的身份信息</p>
                </div>

                <el-form
                  ref="profileFormRef"
                  :model="profileForm"
                  :rules="profileRules"
                  label-position="top"
                  class="profile-edit-form"
                >
                  <el-row :gutter="16">
                    <el-col :xs="24" :sm="12">
                      <el-form-item label="用户登录账号">
                        <el-input :model-value="userStore.currentUsername" disabled>
                          <template #prefix>
                            <el-icon><User /></el-icon>
                          </template>
                        </el-input>
                      </el-form-item>
                    </el-col>

                    <el-col :xs="24" :sm="12">
                      <el-form-item label="企业员工工号">
                        <el-input :model-value="userStore.userInfo?.id || 'USR-1001'" disabled>
                          <template #prefix>
                            <el-icon><Postcard /></el-icon>
                          </template>
                        </el-input>
                      </el-form-item>
                    </el-col>
                  </el-row>

                  <el-row :gutter="16">
                    <el-col :xs="24" :sm="12">
                      <el-form-item label="真实姓名" prop="realName">
                        <el-input v-model="profileForm.realName" placeholder="请输入真实姓名">
                          <template #prefix>
                            <el-icon><Avatar /></el-icon>
                          </template>
                        </el-input>
                      </el-form-item>
                    </el-col>

                    <el-col :xs="24" :sm="12">
                      <el-form-item label="性别" prop="gender">
                        <el-radio-group v-model="profileForm.gender">
                          <el-radio-button label="男">男</el-radio-button>
                          <el-radio-button label="女">女</el-radio-button>
                          <el-radio-button label="保密">保密</el-radio-button>
                        </el-radio-group>
                      </el-form-item>
                    </el-col>
                  </el-row>

                  <el-row :gutter="16">
                    <el-col :xs="24" :sm="12">
                      <el-form-item label="联系手机" prop="phone">
                        <el-input v-model="profileForm.phone" placeholder="11位大陆手机号码">
                          <template #prefix>
                            <el-icon><Iphone /></el-icon>
                          </template>
                        </el-input>
                      </el-form-item>
                    </el-col>

                    <el-col :xs="24" :sm="12">
                      <el-form-item label="电子邮箱" prop="email">
                        <el-input v-model="profileForm.email" placeholder="example@cloudhub.com">
                          <template #prefix>
                            <el-icon><Message /></el-icon>
                          </template>
                        </el-input>
                      </el-form-item>
                    </el-col>
                  </el-row>

                  <el-row :gutter="16">
                    <el-col :xs="24" :sm="12">
                      <el-form-item label="所属组织部门" prop="department">
                        <el-select v-model="profileForm.department" placeholder="请选择部门" style="width: 100%">
                          <el-option
                            v-for="dept in departmentOptions"
                            :key="dept"
                            :label="dept"
                            :value="dept"
                          />
                        </el-select>
                      </el-form-item>
                    </el-col>

                    <el-col :xs="24" :sm="12">
                      <el-form-item label="职务职称" prop="jobTitle">
                        <el-input v-model="profileForm.jobTitle" placeholder="如：架构师、总监、运维主管">
                          <template #prefix>
                            <el-icon><Briefcase /></el-icon>
                          </template>
                        </el-input>
                      </el-form-item>
                    </el-col>
                  </el-row>

                  <el-form-item label="个性签名 / 个人简介" prop="bio">
                    <el-input
                      v-model="profileForm.bio"
                      type="textarea"
                      :rows="3"
                      maxlength="150"
                      show-word-limit
                      placeholder="写几句话介绍一下自己的业务职责或技术理念..."
                    />
                  </el-form-item>

                  <div class="form-actions-bar">
                    <el-button type="primary" :loading="savingProfile" @click="submitSaveProfile">
                      <el-icon><Check /></el-icon> 保存个人资料
                    </el-button>
                    <el-button @click="resetProfileForm">重置更改</el-button>
                  </div>
                </el-form>
              </div>
            </el-tab-pane>

            <!-- Tab 2: Security & Password Modification -->
            <el-tab-pane label="安全与密码" name="security">
              <div class="tab-pane-inner">
                <div class="pane-headline">
                  <h4 class="pane-title">修改系统登录密码</h4>
                  <p class="pane-sub">为了账号安全，请定期更换符合企业规范的强密码</p>
                </div>

                <div class="password-guidelines-box">
                  <el-icon :size="16" color="#2563eb"><InfoFilled /></el-icon>
                  <div class="guideline-text">
                    <strong>企业级强密码规范建议：</strong>
                    <span>密码长度不少于 8 位，且包含大写字母、小写字母、数字及特殊符号（如 @$!%*?&）。</span>
                  </div>
                </div>

                <el-form
                  ref="pwdFormRef"
                  :model="pwdForm"
                  :rules="pwdRules"
                  label-position="top"
                  class="password-change-form"
                >
                  <el-form-item label="当前原密码" prop="oldPassword">
                    <el-input
                      v-model="pwdForm.oldPassword"
                      type="password"
                      show-password
                      placeholder="请输入您当前使用的登录密码"
                    >
                      <template #prefix>
                        <el-icon><Lock /></el-icon>
                      </template>
                    </el-input>
                  </el-form-item>

                  <el-form-item label="设置新密码" prop="newPassword">
                    <el-input
                      v-model="pwdForm.newPassword"
                      type="password"
                      show-password
                      placeholder="请输入新的系统登录密码 (至少8位)"
                    >
                      <template #prefix>
                        <el-icon><Key /></el-icon>
                      </template>
                    </el-input>

                    <!-- Real-time dynamic password strength meter -->
                    <div class="pwd-strength-container" v-if="pwdForm.newPassword">
                      <div class="meter-bars">
                        <div class="meter-bar" :class="{ active: pwdStrengthScore >= 1, weak: pwdStrengthScore === 1, medium: pwdStrengthScore === 2, strong: pwdStrengthScore >= 3 }"></div>
                        <div class="meter-bar" :class="{ active: pwdStrengthScore >= 2, medium: pwdStrengthScore === 2, strong: pwdStrengthScore >= 3 }"></div>
                        <div class="meter-bar" :class="{ active: pwdStrengthScore >= 3, strong: pwdStrengthScore >= 3 }"></div>
                      </div>
                      <span class="strength-label" :class="pwdStrengthClass">
                        密码强度：{{ pwdStrengthText }}
                      </span>
                    </div>
                  </el-form-item>

                  <el-form-item label="确认新密码" prop="confirmPassword">
                    <el-input
                      v-model="pwdForm.confirmPassword"
                      type="password"
                      show-password
                      placeholder="请再次输入新密码"
                    >
                      <template #prefix>
                        <el-icon><CircleCheck /></el-icon>
                      </template>
                    </el-input>
                  </el-form-item>

                  <div class="form-actions-bar">
                    <el-button type="primary" :loading="changingPwd" @click="submitChangePassword">
                      <el-icon><Lock /></el-icon> 确认修改密码
                    </el-button>
                    <el-button @click="resetPwdForm">清空重填</el-button>
                  </div>
                </el-form>
              </div>
            </el-tab-pane>

            <!-- Tab 3: Personal Audit Logs & Activity -->
            <el-tab-pane label="个人操作轨迹" name="activity">
              <div class="tab-pane-inner">
                <div class="pane-headline flex-between">
                  <div>
                    <h4 class="pane-title">最近账号审计与操作记录</h4>
                    <p class="pane-sub">仅展示当前登录账号（{{ userStore.currentUsername }}）的操作与登录轨迹</p>
                  </div>
                  <el-button size="small" @click="loadPersonalLogs">
                    <el-icon><Refresh /></el-icon> 刷新记录
                  </el-button>
                </div>

                <el-table :data="personalLogs" stripe style="width: 100%" class="activity-table">
                  <el-table-column prop="time" label="操作时间" width="170" />
                  <el-table-column prop="action" label="操作行为" width="130">
                    <template #default="{ row }">
                      <el-tag size="small" :type="getActionTagType(row.action)">
                        {{ row.action }}
                      </el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column prop="target" label="操作目标" width="160" show-overflow-tooltip />
                  <el-table-column prop="detail" label="详细描述" min-width="220" show-overflow-tooltip />
                  <el-table-column prop="ip" label="操作IP" width="130">
                    <template #default="{ row }">
                      <span class="mono">{{ row.ip }}</span>
                    </template>
                  </el-table-column>
                  <el-table-column prop="status" label="执行结果" width="90" align="center">
                    <template #default="{ row }">
                      <el-tag size="small" :type="row.status === 'success' ? 'success' : 'warning'">
                        {{ row.status === 'success' ? '成功' : '告警' }}
                      </el-tag>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </el-tab-pane>

            <!-- Tab 4: System Preferences -->
            <el-tab-pane label="系统偏好设置" name="preferences">
              <div class="tab-pane-inner">
                <div class="pane-headline">
                  <h4 class="pane-title">中台界面与交互偏好</h4>
                  <p class="pane-sub">定制专属于您的中台视觉主题与操作交互习惯</p>
                </div>

                <div class="preferences-grid">
                  <!-- Theme Preference Card -->
                  <div class="pref-card">
                    <div class="pref-head">
                      <span class="pref-title">
                        <el-icon><Sunny v-if="!appStore.isDark" /><Moon v-else /></el-icon>
                        界面深浅视觉模式
                      </span>
                      <span class="pref-desc">自由切换深色护眼模式与极简纯白天际模式</span>
                    </div>
                    <div class="theme-switch-row">
                      <el-radio-group v-model="themeSelection" @change="handleThemeChange">
                        <el-radio-button label="light">
                          <el-icon><Sunny /></el-icon> 浅色天际
                        </el-radio-button>
                        <el-radio-button label="dark">
                          <el-icon><Moon /></el-icon> 深邃暗夜
                        </el-radio-button>
                      </el-radio-group>
                    </div>
                  </div>

                  <!-- Sidebar Behavior Card -->
                  <div class="pref-card">
                    <div class="pref-head">
                      <span class="pref-title">
                        <el-icon><Fold /></el-icon>
                        侧边导航栏展开状态
                      </span>
                      <span class="pref-desc">控制左侧主功能导航菜单默认紧凑折叠还是完整展开</span>
                    </div>
                    <el-switch
                      v-model="sidebarCollapsedState"
                      @change="handleSidebarToggle"
                      active-text="紧凑折叠"
                      inactive-text="完整展开"
                    />
                  </div>

                  <!-- Notifications Card -->
                  <div class="pref-card">
                    <div class="pref-head">
                      <span class="pref-title">
                        <el-icon><Bell /></el-icon>
                        系统消息桌面弹窗与声音
                      </span>
                      <span class="pref-desc">当核心通信代理或设备离线预警时是否触发通知提醒</span>
                    </div>
                    <el-switch v-model="notificationPref" @change="handleNotificationChange" />
                  </div>
                </div>
              </div>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>
    </el-row>

    <!-- Avatar Selection Dialog -->
    <el-dialog
      v-model="avatarDialogVisible"
      title="更换个人用户头像"
      width="520px"
      destroy-on-close
      class="avatar-picker-dialog"
    >
      <div class="avatar-dialog-body">
        <p class="dialog-hint">从官方企业预设头像中选择，或者从本地上传自定义头像图片：</p>

        <div class="preset-avatars-grid">
          <div
            v-for="(avatarUrl, idx) in presetAvatars"
            :key="idx"
            class="preset-item"
            :class="{ active: selectedAvatar === avatarUrl }"
            @click="selectedAvatar = avatarUrl"
          >
            <el-avatar :size="64" :src="avatarUrl" />
            <el-icon v-if="selectedAvatar === avatarUrl" class="check-mark"><Check /></el-icon>
          </div>
        </div>

        <div class="custom-upload-section">
          <span class="custom-upload-label">或者选择本地图片上传：</span>
          <input
            type="file"
            ref="fileInputRef"
            accept="image/*"
            style="display: none"
            @change="handleFileChange"
          />
          <el-button @click="$refs.fileInputRef.click()">
            <el-icon><Upload /></el-icon> 本地图片上传
          </el-button>
        </div>
      </div>

      <template #footer>
        <el-button @click="avatarDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmAvatarChange">确认更换</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Camera,
  Stamp,
  OfficeBuilding,
  Postcard,
  Iphone,
  Message,
  Briefcase,
  Timer,
  CircleCheckFilled,
  CircleCheck,
  Lock,
  Key,
  User,
  Avatar,
  Check,
  InfoFilled,
  Refresh,
  Sunny,
  Moon,
  Fold,
  Bell,
  Upload
} from '@element-plus/icons-vue'
import { useAdminStore } from '@/stores/admin'
import { useAppStore } from '@/stores/app'
import { getStoredLogs } from '@/utils/mockData'

const route = useRoute()
const userStore = useAdminStore()
const appStore = useAppStore()

// Active tab, support query param ?tab=security
const activeTab = ref(route.query.tab === 'security' ? 'security' : 'basic')

// Security score & 2FA
const securityScore = computed(() => userStore.userInfo?.securityScore || 85)
const scoreProgressColor = computed(() => {
  if (securityScore.value >= 80) return '#10b981'
  if (securityScore.value >= 60) return '#f59e0b'
  return '#ef4444'
})
const enable2FA = ref(userStore.userInfo?.enable2FA || false)

const toggle2FA = (val) => {
  userStore.updateUserInfo({
    enable2FA: val,
    securityScore: val ? 95 : 85
  })
  ElMessage.success(val ? '已成功开启双因子认证(2FA)安全防护' : '已关闭双因子认证')
}

// Department list
const departmentOptions = [
  '技术研发与数字化中心',
  '前端架构与应用研发组',
  '后端微服务与云原生组',
  '数据智能与算法工程组',
  '产品设计与用户体验中心',
  '基础设施与网络工程部',
  '运营管理与客户成功中心',
  '财务管理与法务审计部'
]

// Profile Form State
const profileFormRef = ref(null)
const savingProfile = ref(false)

const profileForm = reactive({
  realName: userStore.userInfo?.realName || userStore.currentUsername,
  phone: userStore.userInfo?.phone || '13800138000',
  email: userStore.userInfo?.email || 'admin@cloudhub-admin.com',
  department: userStore.userInfo?.department || '技术研发与数字化中心',
  jobTitle: userStore.userInfo?.jobTitle || '平台总架构师',
  gender: userStore.userInfo?.gender || '男',
  bio: userStore.userInfo?.bio || '致力于构建高性能、高可用且通用的现代化数字管理系统架构。'
})

const profileRules = {
  realName: [{ required: true, message: '真实姓名不能为空', trigger: 'blur' }],
  phone: [
    { required: true, message: '请输入联系手机', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入有效的11位手机号码', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入电子邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ]
}

const submitSaveProfile = async () => {
  if (!profileFormRef.value) return
  await profileFormRef.value.validate((valid) => {
    if (!valid) return
    savingProfile.value = true
    try {
      userStore.updateUserProfile({
        realName: profileForm.realName,
        phone: profileForm.phone,
        email: profileForm.email,
        department: profileForm.department,
        jobTitle: profileForm.jobTitle,
        gender: profileForm.gender,
        bio: profileForm.bio
      })
      ElMessage.success('个人基本资料已成功保存更新！')
    } catch (e) {
      ElMessage.error(e.message || '更新失败')
    } finally {
      savingProfile.value = false
    }
  })
}

const resetProfileForm = () => {
  profileForm.realName = userStore.userInfo?.realName || userStore.currentUsername
  profileForm.phone = userStore.userInfo?.phone || '13800138000'
  profileForm.email = userStore.userInfo?.email || 'admin@cloudhub-admin.com'
  profileForm.department = userStore.userInfo?.department || '技术研发与数字化中心'
  profileForm.jobTitle = userStore.userInfo?.jobTitle || '平台系统总架构师'
  profileForm.gender = userStore.userInfo?.gender || '男'
  profileForm.bio = userStore.userInfo?.bio || '负责全域中后台微服务架构设计、高可用集群演进与通用数字化基础设施治理。'
  ElMessage.info('已恢复初始资料状态')
}

// Password Form State
const pwdFormRef = ref(null)
const changingPwd = ref(false)

const pwdForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const pwdStrengthScore = computed(() => {
  const pwd = pwdForm.newPassword
  if (!pwd) return 0
  let score = 0
  if (pwd.length >= 6) score++
  if (pwd.length >= 8 && /[A-Z]/.test(pwd) && /[0-9]/.test(pwd)) score++
  if (pwd.length >= 10 && /[^A-Za-z0-9]/.test(pwd)) score++
  return Math.min(score, 3)
})

const pwdStrengthText = computed(() => {
  if (pwdStrengthScore.value === 1) return '弱'
  if (pwdStrengthScore.value === 2) return '中等'
  if (pwdStrengthScore.value >= 3) return '强'
  return '未输入'
})

const pwdStrengthClass = computed(() => {
  if (pwdStrengthScore.value === 1) return 'text-weak'
  if (pwdStrengthScore.value === 2) return 'text-medium'
  if (pwdStrengthScore.value >= 3) return 'text-strong'
  return ''
})

const pwdRules = {
  oldPassword: [{ required: true, message: '请输入当前旧密码', trigger: 'blur' }],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== pwdForm.newPassword) {
          callback(new Error('两次输入的新密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

const submitChangePassword = async () => {
  if (!pwdFormRef.value) return
  await pwdFormRef.value.validate((valid) => {
    if (!valid) return
    changingPwd.value = true
    try {
      userStore.changePassword(pwdForm.oldPassword, pwdForm.newPassword)
      ElMessage.success('密码已成功修改，凭据散列已重新生成')
      pwdForm.oldPassword = ''
      pwdForm.newPassword = ''
      pwdForm.confirmPassword = ''
    } catch (e) {
      ElMessage.error(e.message || '修改密码失败')
    } finally {
      changingPwd.value = false
    }
  })
}

const resetPwdForm = () => {
  pwdForm.oldPassword = ''
  pwdForm.newPassword = ''
  pwdForm.confirmPassword = ''
}

// Personal Logs
const personalLogs = ref([])

const loadPersonalLogs = () => {
  const allLogs = getStoredLogs()
  const currentUser = userStore.currentUsername
  personalLogs.value = allLogs.filter(
    (l) => l.operator === currentUser || l.operator === 'admin'
  )
}

const getActionTagType = (action) => {
  if (action.includes('登录')) return 'success'
  if (action.includes('修改') || action.includes('更新')) return 'primary'
  if (action.includes('指令') || action.includes('下发')) return 'warning'
  return 'info'
}

// Preferences
const themeSelection = computed({
  get: () => (appStore.isDark ? 'dark' : 'light'),
  set: (val) => appStore.setTheme(val)
})
const sidebarCollapsedState = computed({
  get: () => appStore.sidebarCollapsed,
  set: () => appStore.toggleSidebar()
})
const notificationPref = ref(true)

const handleThemeChange = (val) => {
  appStore.setTheme(val)
}

const handleSidebarToggle = () => {
  appStore.toggleSidebar()
}

const handleNotificationChange = (val) => {
  ElMessage.success(val ? '已开启系统告警即时桌面通知' : '已静音桌面弹窗通知')
}

// Preset Avatars Modal
const avatarDialogVisible = ref(false)
const presetAvatars = [
  'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png',
  'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png',
  'https://cube.elemecdn.com/9/c2/f0ee8a3c7c9638a54940382568c9dpng.png',
  'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=256&h=256&q=80',
  'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=256&h=256&q=80',
  'https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=256&h=256&q=80'
]
const selectedAvatar = ref(userStore.currentAvatar)

const handleFileChange = (e) => {
  const file = e.target.files?.[0]
  if (!file) return
  if (!file.type.startsWith('image/')) {
    ElMessage.warning('请选择图片类型文件')
    return
  }
  const reader = new FileReader()
  reader.onload = (event) => {
    selectedAvatar.value = event.target.result
    ElMessage.success('图片已载入预览，点击【确认更换】生效')
  }
  reader.readAsDataURL(file)
}

const confirmAvatarChange = () => {
  userStore.updateUserInfo({ avatar: selectedAvatar.value })
  avatarDialogVisible.value = false
  ElMessage.success('用户头像已成功更新')
}

onMounted(() => {
  loadPersonalLogs()
})
</script>

<style scoped>
.profile-page {
  gap: 16px;
}

.profile-layout-row {
  row-gap: 16px;
}

.left-cards-stack {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* User Identity Card */
.user-id-card {
  border-radius: 12px;
  border: 1px solid var(--border-color);
  background-color: var(--card-bg);
}

.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px 0 16px;
  text-align: center;
}

.avatar-wrapper {
  position: relative;
  width: 96px;
  height: 96px;
  border-radius: 50%;
  cursor: pointer;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  margin-bottom: 12px;
}

.main-avatar {
  width: 100%;
  height: 100%;
  transition: transform 0.3s ease;
}

.avatar-hover-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(15, 23, 42, 0.65);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  font-size: 11px;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.avatar-wrapper:hover .avatar-hover-overlay {
  opacity: 1;
}

.user-display-name {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-main);
  margin-bottom: 2px;
}

.user-account-tag {
  font-size: 12px;
  color: var(--text-muted);
  font-family: monospace;
  margin-bottom: 12px;
}

.badges-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  justify-content: center;
}

.role-badge,
.dept-badge {
  display: flex;
  align-items: center;
  gap: 4px;
  border-radius: 6px;
  font-size: 11px;
}

.user-bio-text {
  font-size: 12px;
  line-height: 1.6;
  color: var(--text-regular);
  background-color: var(--tag-sub-bg, #f8fafc);
  border: 1px solid var(--border-color);
  padding: 10px 14px;
  border-radius: 10px;
  margin-bottom: 16px;
  font-style: italic;
}

.user-meta-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  border-top: 1px solid var(--border-light);
  padding-top: 14px;
}

.meta-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
}

.meta-k {
  color: var(--text-muted);
  display: flex;
  align-items: center;
  gap: 6px;
}

.meta-v {
  color: var(--text-main);
  font-weight: 500;
}

.mono {
  font-family: monospace;
}

.time-text {
  font-size: 11px;
  color: var(--text-muted);
}

/* Security Health Card */
.security-card {
  border-radius: 12px;
  border: 1px solid var(--border-color);
  background-color: var(--card-bg);
}

.card-header-flex {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title-with-icon {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-main);
}

.security-score-box {
  background-color: var(--tag-sub-bg, #f8fafc);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  padding: 14px;
  margin-bottom: 14px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.score-top {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.score-num {
  font-size: 26px;
  font-weight: 800;
  color: var(--text-main);
  line-height: 1;
}

.score-unit {
  font-size: 12px;
  color: var(--text-muted);
}

.score-subtip {
  font-size: 11px;
  color: var(--text-muted);
}

.security-checklist {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.sec-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 10px;
  border-radius: 10px;
  background-color: var(--tag-sub-bg, #f8fafc);
  border: 1px solid var(--border-color);
}

.sec-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.sec-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-main);
}

.sec-status {
  font-size: 11px;
  color: var(--text-muted);
}

/* Profile Tabs Card */
.profile-tabs-card {
  border-radius: 12px;
  border: 1px solid var(--border-color);
  background-color: var(--card-bg);
  min-height: 600px;
}

.tab-pane-inner {
  padding: 8px 4px;
}

.pane-headline {
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-light);
}

.pane-headline.flex-between {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pane-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-main);
  margin-bottom: 4px;
}

.pane-sub {
  font-size: 12px;
  color: var(--text-muted);
}

.profile-edit-form,
.password-change-form {
  max-width: 760px;
}

.form-actions-bar {
  display: flex;
  gap: 12px;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid var(--border-light);
}

/* Password Tab Specifics */
.password-guidelines-box {
  display: flex;
  gap: 10px;
  align-items: flex-start;
  padding: 12px 14px;
  border-radius: 10px;
  background-color: rgba(37, 99, 235, 0.08);
  border: 1px solid rgba(37, 99, 235, 0.2);
  margin-bottom: 20px;
}

.guideline-text {
  font-size: 12px;
  color: var(--text-regular);
  line-height: 1.5;
}

.guideline-text strong {
  display: block;
  font-size: 13px;
  color: var(--primary-color);
  margin-bottom: 2px;
}

.pwd-strength-container {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 8px;
  width: 100%;
}

.meter-bars {
  display: flex;
  gap: 4px;
  flex: 1;
}

.meter-bar {
  height: 5px;
  flex: 1;
  border-radius: 3px;
  background-color: var(--border-color);
  transition: background-color 0.3s;
}

.meter-bar.active.weak {
  background-color: #ef4444;
}

.meter-bar.active.medium {
  background-color: #f59e0b;
}

.meter-bar.active.strong {
  background-color: #10b981;
}

.strength-label {
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
}

.text-weak {
  color: #ef4444;
}

.text-medium {
  color: #f59e0b;
}

.text-strong {
  color: #10b981;
}

/* Activity Table */
.activity-table {
  border-radius: 10px;
}

/* Preferences Tab */
.preferences-grid {
  display: flex;
  flex-direction: column;
  gap: 14px;
  max-width: 760px;
}

.pref-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 18px;
  border-radius: 10px;
  background-color: var(--tag-sub-bg, #f8fafc);
  border: 1px solid var(--border-color);
  gap: 16px;
  flex-wrap: wrap;
}

.pref-head {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.pref-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-main);
}

.pref-desc {
  font-size: 12px;
  color: var(--text-muted);
}

/* Avatar Modal */
.avatar-dialog-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.dialog-hint {
  font-size: 13px;
  color: var(--text-regular);
}

.preset-avatars-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
  padding: 6px 0;
}

.preset-item {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 12px;
  border-radius: 10px;
  border: 2px solid var(--border-color);
  cursor: pointer;
  background-color: var(--tag-sub-bg, #f8fafc);
  transition: all 0.2s ease;
}

.preset-item:hover {
  border-color: var(--primary-color);
  transform: translateY(-2px);
}

.preset-item.active {
  border-color: var(--primary-color);
  background-color: var(--menu-active-bg, #eff6ff);
}

.check-mark {
  position: absolute;
  bottom: 8px;
  right: 8px;
  background-color: var(--primary-color);
  color: #ffffff;
  border-radius: 50%;
  padding: 2px;
  font-size: 12px;
}

.custom-upload-section {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 12px;
  border-top: 1px solid var(--border-light);
  gap: 12px;
}

.custom-upload-label {
  font-size: 13px;
  color: var(--text-muted);
}
</style>
