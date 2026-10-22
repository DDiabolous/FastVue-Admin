<template>
  <PageContainer
    class="business-page example-page"
    title="文件上传"
    description="演示图片裁剪、附件选择、进度反馈、取消与重试。所有操作均在本地完成。"
  >
    <template #actions>
      <ExampleGuide
        source="Upload.vue"
        :features="[
          'AvatarCropper：图片裁剪与预览',
          '类型、大小与数量限制',
          '模拟上传进度、取消与失败重试',
        ]"
        scope="本地文件选择、预览和裁剪演示，不会上传到服务端。生产上传需接入真实上传接口。"
      />
    </template>
    <el-row :gutter="20">
      <!-- 单图与头像上传卡片 -->
      <el-col :xs="24" :md="12">
        <el-card shadow="never" class="upload-card">
          <template #header>
            <div class="card-header">
              <span>单图 / 头像裁剪</span>
              <el-tag size="small">图片裁剪</el-tag>
            </div>
          </template>
          <div class="single-upload-demo">
            <el-upload
              action="#"
              :auto-upload="false"
              :show-file-list="false"
              accept="image/jpeg,image/png,image/webp"
              :on-change="handleSingleImageChange"
            >
              <div v-if="singleImageUrl" class="image-preview-wrapper">
                <img :src="singleImageUrl" class="uploaded-image" alt="预览" />
                <div class="image-mask">
                  <el-icon><Edit /></el-icon>
                  <span>点击更换</span>
                </div>
              </div>
              <div v-else class="upload-placeholder">
                <el-icon :size="36"><Plus /></el-icon>
                <div class="upload-text">点击上传图片</div>
              </div>
            </el-upload>
            <div class="security-rules-tip">
              <ul>
                <li>支持 JPG/PNG/WebP 格式，单张不超过 2MB。</li>
                <li>文件仅用于本地演示，不提交到服务端。</li>
              </ul>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 批量文件上传卡片 -->
      <el-col :xs="24" :md="12">
        <el-card shadow="never" class="upload-card">
          <template #header>
            <div class="card-header">
              <span>批量附件</span>
              <el-tag size="small" type="success">支持拖拽</el-tag>
            </div>
          </template>
          <el-upload
            v-model:file-list="fileList"
            drag
            action="#"
            :auto-upload="false"
            :limit="5"
            accept=".png,.jpg,.jpeg,.pdf,.xlsx,.docx"
            :on-change="handleBatchValidate"
            :on-exceed="handleExceed"
            :on-preview="handlePreview"
            :on-remove="removeUpload"
          >
            <el-icon :size="42"><UploadFilled /></el-icon>
            <p>
              拖拽文件到这里，或
              <em>点击浏览</em>
            </p>
            <template #tip>
              <div class="starter-muted">
                支持 PNG、JPG、PDF、Excel、Word 附件，单个文件不超过 10 MB，单次最多 5 个。
              </div>
            </template>
          </el-upload>
          <div class="upload-job-tools">
            <el-button
              type="primary"
              :disabled="
                !fileList.some(
                  (f) => !jobs[f.uid] || ['cancelled', 'error'].includes(jobs[f.uid].state),
                )
              "
              @click="startAll"
            >
              模拟上传
            </el-button>
            <el-checkbox v-model="failNext">模拟首个文件失败</el-checkbox>
          </div>
          <p class="starter-muted">进度为本地模拟，不会向服务端发送文件。</p>
          <div v-for="file in fileList" :key="file.uid" class="upload-job">
            <div>
              <span>{{ file.name }}</span>
              <el-tag size="small" :type="jobs[file.uid]?.state === 'error' ? 'danger' : 'info'">
                {{ jobLabels[jobs[file.uid]?.state] || '待上传' }}
              </el-tag>
            </div>
            <el-progress
              :percentage="jobs[file.uid]?.progress || 0"
              :status="
                jobs[file.uid]?.state === 'done'
                  ? 'success'
                  : jobs[file.uid]?.state === 'error'
                    ? 'exception'
                    : undefined
              "
            />
            <el-button
              v-if="jobs[file.uid]?.state === 'uploading'"
              link
              @click="cancelUpload(file.uid)"
            >
              取消
            </el-button>
            <el-button
              v-if="['cancelled', 'error'].includes(jobs[file.uid]?.state)"
              link
              type="primary"
              @click="startUpload(file)"
            >
              重试
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图片安全预览弹窗 -->
    <el-dialog
      class="business-overlay"
      v-model="previewVisible"
      title="安全图片预览"
      width="min(680px, 92vw)"
    >
      <div style="text-align: center">
        <img
          :src="currentPreviewUrl"
          alt="本地图片预览"
          style="max-width: 100%; max-height: 60vh; object-fit: contain; border-radius: 4px"
        />
      </div>
    </el-dialog>
    <AvatarCropper
      v-model="cropperVisible"
      :image-src="rawImage"
      @confirm="singleImageUrl = $event"
    />
  </PageContainer>
</template>

<script setup>
import ExampleGuide from '@/components/examples/ExampleGuide.vue'
import { ref, reactive, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Edit, UploadFilled } from '@element-plus/icons-vue'
import PageContainer from '@/components/admin/PageContainer.vue'
import AvatarCropper from '@/components/admin/AvatarCropper.vue'

const cropperVisible = ref(false),
  rawImage = ref('')
const singleImageUrl = ref('')
const jobs = reactive({}),
  timers = new Map(),
  failNext = ref(false)
const jobLabels = { uploading: '上传中', done: '已完成', error: '失败', cancelled: '已取消' }
function cancelUpload(uid) {
  clearInterval(timers.get(uid))
  timers.delete(uid)
  if (jobs[uid]) jobs[uid].state = 'cancelled'
}
function removeUpload(file) {
  cancelUpload(file.uid)
  delete jobs[file.uid]
}
function startUpload(file, fail = false) {
  cancelUpload(file.uid)
  jobs[file.uid] = { state: 'uploading', progress: 0 }
  timers.set(
    file.uid,
    setInterval(() => {
      jobs[file.uid].progress = Math.min(100, jobs[file.uid].progress + 20)
      if ((fail && jobs[file.uid].progress >= 60) || jobs[file.uid].progress === 100) {
        clearInterval(timers.get(file.uid))
        timers.delete(file.uid)
        jobs[file.uid].state = fail ? 'error' : 'done'
      }
    }, 180),
  )
}
function startAll() {
  const pending = fileList.value.filter(
    (file) => !jobs[file.uid] || ['cancelled', 'error'].includes(jobs[file.uid].state),
  )
  pending.forEach((file, index) => startUpload(file, failNext.value && index === 0))
  failNext.value = false
}
const fileList = ref([])
const previewVisible = ref(false)
const currentPreviewUrl = ref('')

function handleSingleImageChange(uploadFile) {
  const file = uploadFile.raw
  if (!file) return

  const allowed = ['image/jpeg', 'image/png', 'image/webp']
  if (!allowed.includes(file.type)) {
    ElMessage.error('仅允许上传 JPG、PNG 或 WebP 图片格式')
    return
  }
  if (file.size > 2 * 1024 * 1024) {
    ElMessage.error('图片大小不可超过 2MB')
    return
  }

  if (rawImage.value) URL.revokeObjectURL(rawImage.value)
  rawImage.value = URL.createObjectURL(file)
  cropperVisible.value = true
}

function handleBatchValidate(file) {
  const maxSize = 10 * 1024 * 1024
  const allowedExts = /\.(png|jpe?g|pdf|xlsx|docx)$/i
  if (file.size > maxSize || !allowedExts.test(file.name)) {
    fileList.value = fileList.value.filter((item) => item.uid !== file.uid)
    ElMessage.error(`文件 [${file.name}] 不符合安全规范（仅支持 10MB 内的合规附件）`)
  }
}

function handleExceed() {
  ElMessage.warning('单次最多允许上传 5 个附件')
}

function handlePreview(file) {
  if (!file.raw?.type.startsWith('image/')) {
    ElMessage.info('非图片文件不支持内置预览，可对接安全下载接口')
    return
  }
  if (currentPreviewUrl.value) URL.revokeObjectURL(currentPreviewUrl.value)
  currentPreviewUrl.value = URL.createObjectURL(file.raw)
  previewVisible.value = true
}

onUnmounted(() => {
  timers.forEach(clearInterval)
  if (rawImage.value) URL.revokeObjectURL(rawImage.value)
  if (singleImageUrl.value) URL.revokeObjectURL(singleImageUrl.value)
  if (currentPreviewUrl.value) URL.revokeObjectURL(currentPreviewUrl.value)
})
</script>

<style scoped>
.upload-card {
  margin-bottom: 20px;
}
.upload-job-tools {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
  margin-top: 20px;
}
.upload-job {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
}
.upload-job > div:first-child {
  display: flex;
  gap: 12px;
  align-items: center;
  justify-content: space-between;
  font-size: 13px;
  margin-bottom: 8px;
}
.upload-job > div:first-child > span {
  min-width: 0;
  overflow-wrap: anywhere;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.single-upload-demo {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px 0;
}
.upload-placeholder {
  width: 140px;
  height: 140px;
  border: 1px dashed var(--el-border-color);
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  transition: border-color 0.2s;
}
.upload-placeholder:hover {
  border-color: var(--el-color-primary);
}
.upload-text {
  font-size: 13px;
  color: var(--el-text-color-secondary);
  margin-top: 8px;
}
.image-preview-wrapper {
  position: relative;
  width: 140px;
  height: 140px;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid var(--el-border-color-light);
}
.uploaded-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.image-mask {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: #fff;
  opacity: 0;
  transition: opacity 0.2s;
  cursor: pointer;
}
.image-preview-wrapper:hover .image-mask {
  opacity: 1;
}
.security-rules-tip {
  margin-top: 16px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
  line-height: 1.6;
}
.security-rules-tip ul {
  padding-left: 18px;
  margin: 0;
}
.starter-muted {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-top: 8px;
}
</style>
