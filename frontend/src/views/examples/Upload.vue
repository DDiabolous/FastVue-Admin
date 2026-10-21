<template>
  <PageContainer
    title="文件上传"
    description="演示文件选择、大小校验、列表和本地图片预览。此示例不会上传文件。"
  >
    <el-card shadow="never">
      <el-upload
        v-model:file-list="files"
        drag
        :auto-upload="false"
        :limit="5"
        accept=".png,.jpg,.jpeg,.pdf"
        :on-change="validate"
        :on-exceed="exceeded"
        :on-preview="preview"
      >
        <el-icon :size="42"><UploadFilled /></el-icon>
        <p>拖拽文件到这里，或点击选择</p>
        <template #tip>
          <p class="starter-muted">
            支持 PNG、JPG、PDF，单个文件不超过 5 MB，最多 5 个。图片可点击文件名预览。
          </p>
        </template>
      </el-upload>
    </el-card>
    <el-dialog v-model="visible" title="图片预览" width="min(720px, 94vw)">
      <img
        :src="previewUrl"
        alt="本地图片预览"
        style="width: 100%; max-height: 60vh; object-fit: contain"
      />
    </el-dialog>
  </PageContainer>
</template>
<script setup>
import { ref, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import PageContainer from '@/components/admin/PageContainer.vue'
const files = ref([]),
  visible = ref(false),
  previewUrl = ref('')
function validate(file) {
  if (file.size > 5 * 1024 * 1024 || !/\.(png|jpe?g|pdf)$/i.test(file.name)) {
    files.value = files.value.filter((item) => item.uid !== file.uid)
    ElMessage.error('请选择 5 MB 以内的 PNG、JPG 或 PDF 文件')
  }
}
function exceeded() {
  ElMessage.warning('最多选择 5 个文件')
}
function preview(file) {
  if (!file.raw?.type.startsWith('image/')) {
    ElMessage.info('此示例仅预览图片')
    return
  }
  URL.revokeObjectURL(previewUrl.value)
  previewUrl.value = URL.createObjectURL(file.raw)
  visible.value = true
}
onUnmounted(() => URL.revokeObjectURL(previewUrl.value))
</script>
