<template>
  <el-dialog
    :model-value="modelValue"
    title="裁剪头像"
    width="680px"
    destroy-on-close
    :close-on-click-modal="false"
    class="avatar-cropper-dialog"
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <div class="cropper-container">
      <!-- 左侧：双层裁剪交互区 (纯净图片 Canvas + 纯 CSS 视觉遮罩) -->
      <div class="cropper-stage-wrapper">
        <div class="stage-viewport-box" :style="{ width: stageSize + 'px', height: stageSize + 'px' }">
          <!-- 底层：仅绘制用户图片的高清画布，使用 DPR 物理像素超采样消除视网膜屏模糊 -->
          <canvas
            ref="canvasRef"
            class="cropper-canvas"
            :width="stageSize * dpr"
            :height="stageSize * dpr"
            :style="{ width: stageSize + 'px', height: stageSize + 'px' }"
            @mousedown="handleMouseDown"
            @wheel.prevent="handleWheel"
            @touchstart.passive="handleTouchStart"
            @touchmove.prevent="handleTouchMove"
            @touchend="handleTouchEnd"
          />

          <!-- 顶层：视觉交互遮罩层 (不拦截鼠标事件，pointer-events: none) -->
          <div class="cropper-mask-layer">
            <div class="crop-viewport" :class="{ circle: isCircleMask }">
              <!-- 九宫格参考线 (纯视觉，绝不进入导出图片) -->
              <div class="grid-line horizontal h1"></div>
              <div class="grid-line horizontal h2"></div>
              <div class="grid-line vertical v1"></div>
              <div class="grid-line vertical v2"></div>
            </div>
          </div>
        </div>

        <div class="canvas-tip">按住拖拽调整构图，滚动鼠标滚轮可平滑缩放</div>
      </div>

      <!-- 右侧：控制面板与超清多尺寸实时预览 -->
      <div class="cropper-controls-wrapper">
        <div class="preview-block">
          <div class="preview-title">实时效果预览</div>
          <div class="preview-list">
            <div class="preview-item">
              <div class="preview-box lg" :class="{ circle: isCircleMask }">
                <img v-if="previewSrc" :src="previewSrc" alt="大头像预览" />
              </div>
              <span class="preview-label">100 × 100</span>
            </div>
            <div class="preview-item">
              <div class="preview-box md" :class="{ circle: isCircleMask }">
                <img v-if="previewSrc" :src="previewSrc" alt="中头像预览" />
              </div>
              <span class="preview-label">48 × 48</span>
            </div>
            <div class="preview-item">
              <div class="preview-box sm" :class="{ circle: isCircleMask }">
                <img v-if="previewSrc" :src="previewSrc" alt="小头像预览" />
              </div>
              <span class="preview-label">32 × 32</span>
            </div>
          </div>
        </div>

        <div class="control-actions">
          <div class="zoom-slider-box">
            <span class="slider-label">缩放</span>
            <el-slider
              v-model="sliderScale"
              :min="minScale"
              :max="maxScale"
              :step="0.005"
              :show-tooltip="false"
              @input="onSliderInput"
            />
          </div>

          <div class="tool-buttons">
            <el-button size="small" icon="RefreshRight" @click="rotateRight">旋转</el-button>
            <el-button size="small" icon="Aim" @click="resetTransform">重置</el-button>
            <el-button
              size="small"
              icon="View"
              :type="isCircleMask ? 'primary' : 'default'"
              plain
              @click="isCircleMask = !isCircleMask"
            >
              视图
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="$emit('update:modelValue', false)">取消</el-button>
        <el-button type="primary" :disabled="!imageLoaded" @click="handleConfirm">
          应用头像
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { encodeAvatar } from '@/utils/avatarEncoding'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  imageSrc: { type: String, default: '' },
  outputSize: { type: Number, default: 640 }, // 默认 640x640 视网膜超清画质
})

const emit = defineEmits(['update:modelValue', 'confirm'])

const stageSize = 360 // 主舞台尺寸 360x360
const cropSize = 240 // 裁剪视口 240x240
// 获取设备像素比 (Retina 屏为 2 或 3，最少取 2 进行超采样)
const dpr = typeof window !== 'undefined' ? Math.max(window.devicePixelRatio || 1, 2) : 2

const canvasRef = ref(null)
const previewSrc = ref('')
const imageLoaded = ref(false)
const isCircleMask = ref(true)

let imgElement = null
const currentScale = ref(1)
const minScale = ref(0.2)
const maxScale = ref(4)
const sliderScale = ref(1)
const offsetX = ref(0)
const offsetY = ref(0)
const rotation = ref(0)

// 拖拽状态管理
let isDragging = false
let startX = 0
let startY = 0

// 初始化加载原图
function initImage() {
  if (!props.imageSrc) return
  imageLoaded.value = false
  const img = new Image()
  img.crossOrigin = 'anonymous'
  img.onload = () => {
    imgElement = img
    imageLoaded.value = true
    resetTransform()
  }
  img.src = props.imageSrc
}

// 重置变换状态
function resetTransform() {
  if (!imgElement) return
  const W = imgElement.naturalWidth || imgElement.width
  const H = imgElement.naturalHeight || imgElement.height
  // 计算最短边填满视口的初始比例
  const initScale = Math.max(cropSize / W, cropSize / H)
  currentScale.value = initScale
  minScale.value = Math.max(0.05, initScale * 0.4)
  maxScale.value = initScale * 4
  sliderScale.value = initScale
  offsetX.value = 0
  offsetY.value = 0
  rotation.value = 0
  draw()
}

function rotateRight() {
  rotation.value = (rotation.value + 90) % 360
  draw()
}

function onSliderInput(val) {
  currentScale.value = val
  draw()
}

function handleWheel(e) {
  const delta = e.deltaY > 0 ? -0.06 : 0.06
  let next = currentScale.value + delta * currentScale.value
  if (next < minScale.value) next = minScale.value
  if (next > maxScale.value) next = maxScale.value
  currentScale.value = next
  sliderScale.value = next
  draw()
}

function handleMouseDown(e) {
  isDragging = true
  startX = e.clientX - offsetX.value
  startY = e.clientY - offsetY.value
  window.addEventListener('mousemove', handleMouseMove)
  window.addEventListener('mouseup', handleMouseUp)
}

function handleMouseMove(e) {
  if (!isDragging) return
  offsetX.value = e.clientX - startX
  offsetY.value = e.clientY - startY
  draw()
}

function handleMouseUp() {
  isDragging = false
  window.removeEventListener('mousemove', handleMouseMove)
  window.removeEventListener('mouseup', handleMouseUp)
}

// 触摸交互适配
let touchStartX = 0
let touchStartY = 0
function handleTouchStart(e) {
  if (e.touches.length === 1) {
    touchStartX = e.touches[0].clientX - offsetX.value
    touchStartY = e.touches[0].clientY - offsetY.value
  }
}

function handleTouchMove(e) {
  if (e.touches.length === 1) {
    offsetX.value = e.touches[0].clientX - touchStartX
    offsetY.value = e.touches[0].clientY - touchStartY
    draw()
  }
}

function handleTouchEnd() {}

// 1. 主舞台画布绘制：使用物理像素超采样消除视网膜屏模糊
function draw() {
  const canvas = canvasRef.value
  if (!canvas || !imgElement || !imageLoaded.value) return
  const ctx = canvas.getContext('2d')

  const W = imgElement.naturalWidth || imgElement.width
  const H = imgElement.naturalHeight || imgElement.height

  // 清除整张物理像素画布
  ctx.clearRect(0, 0, stageSize * dpr, stageSize * dpr)
  ctx.save()
  // 关键：缩放 dpr 倍率，将坐标系对齐逻辑像素，同时享受 Retina 2x/3x 高清超采样
  ctx.scale(dpr, dpr)
  ctx.imageSmoothingEnabled = true
  ctx.imageSmoothingQuality = 'high'
  // 原点平移至舞台中心 + 用户拖拽位移
  ctx.translate(stageSize / 2 + offsetX.value, stageSize / 2 + offsetY.value)
  ctx.rotate((rotation.value * Math.PI) / 180)
  ctx.scale(currentScale.value, currentScale.value)
  // 将原图居中画在原点，严格传入真实的物理像素尺寸
  ctx.drawImage(imgElement, -W / 2, -H / 2, W, H)
  ctx.restore()

  // 2. 实时生成超清无损裁剪结果
  renderCroppedResult()
}

// 2. 超清裁剪生成器：直接从原始高清图片采样，按视口变换映射至高清离线画布
function renderCroppedResult() {
  if (!imgElement || !imageLoaded.value) return

  const W = imgElement.naturalWidth || imgElement.width
  const H = imgElement.naturalHeight || imgElement.height

  const outCanvas = document.createElement('canvas')
  outCanvas.width = props.outputSize
  outCanvas.height = props.outputSize
  const outCtx = outCanvas.getContext('2d')

  outCtx.imageSmoothingEnabled = true
  outCtx.imageSmoothingQuality = 'high'
  outCtx.clearRect(0, 0, props.outputSize, props.outputSize)

  // 缩放放大倍数：从视口尺寸 (cropSize) 映射到目标高清输出尺寸 (outputSize)
  const ratio = props.outputSize / cropSize

  outCtx.save()
  // 目标画布中心
  outCtx.translate(props.outputSize / 2, props.outputSize / 2)
  // 平移偏移量等比例放大
  outCtx.translate(offsetX.value * ratio, offsetY.value * ratio)
  // 旋转
  outCtx.rotate((rotation.value * Math.PI) / 180)
  // 缩放比例
  outCtx.scale(currentScale.value * ratio, currentScale.value * ratio)
  // 采样绘制原图，严格传入真实的物理像素尺寸，彻底告别低分辨率二次缩放与模糊！
  outCtx.drawImage(imgElement, -W / 2, -H / 2, W, H)
  outCtx.restore()

  // Prefer lossless output; compress detailed images to fit the API request limit.
  previewSrc.value = encodeAvatar(outCanvas)
}

function handleConfirm() {
  if (!previewSrc.value) {
    ElMessage.error('裁剪图片仍然过大，请缩小裁剪范围或更换图片')
    return
  }
  emit('confirm', previewSrc.value)
  emit('update:modelValue', false)
}

watch(
  () => props.modelValue,
  (val) => {
    if (val) {
      nextTick(() => {
        initImage()
      })
    }
  },
)

watch(
  () => props.imageSrc,
  () => {
    if (props.modelValue) {
      nextTick(() => {
        initImage()
      })
    }
  },
)

onMounted(() => {
  if (props.modelValue) initImage()
})

onUnmounted(() => {
  window.removeEventListener('mousemove', handleMouseMove)
  window.removeEventListener('mouseup', handleMouseUp)
})
</script>

<style scoped>
.cropper-container {
  display: flex;
  gap: 28px;
}
.cropper-stage-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.stage-viewport-box {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  background-color: #121212;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}
.cropper-canvas {
  width: 100%;
  height: 100%;
  cursor: grab;
  display: block;
}
.cropper-canvas:active {
  cursor: grabbing;
}
.canvas-tip {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-top: 10px;
}

/* 顶层纯 CSS 视觉遮罩层 (pointer-events: none 确保操作穿透至底层画布) */
.cropper-mask-layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
}
.crop-viewport {
  position: relative;
  width: 240px;
  height: 240px;
  border: 1.5px solid #ffffff;
  box-shadow: 0 0 0 9999px rgba(0, 0, 0, 0.58);
  transition: border-radius 0.2s ease;
}
.crop-viewport.circle {
  border-radius: 50%;
}

/* 九宫格参考线 */
.grid-line {
  position: absolute;
  background-color: rgba(255, 255, 255, 0.35);
}
.grid-line.horizontal {
  left: 0;
  right: 0;
  height: 1px;
}
.grid-line.horizontal.h1 {
  top: 33.333%;
}
.grid-line.horizontal.h2 {
  top: 66.666%;
}
.grid-line.vertical {
  top: 0;
  bottom: 0;
  width: 1px;
}
.grid-line.vertical.v1 {
  left: 33.333%;
}
.grid-line.vertical.v2 {
  left: 66.666%;
}

/* 右侧预览与控制面板 */
.cropper-controls-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
.preview-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--el-text-color-primary);
  margin-bottom: 14px;
}
.preview-list {
  display: flex;
  align-items: flex-end;
  gap: 18px;
}
.preview-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}
.preview-box {
  overflow: hidden;
  border: 1px solid var(--el-border-color);
  background-color: var(--el-fill-color-light);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
  transition: border-radius 0.2s ease;
}
.preview-box.circle {
  border-radius: 50%;
}
.preview-box img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.preview-box.lg {
  width: 100px;
  height: 100px;
}
.preview-box.md {
  width: 48px;
  height: 48px;
}
.preview-box.sm {
  width: 32px;
  height: 32px;
}
.preview-label {
  font-size: 11px;
  color: var(--el-text-color-secondary);
}

.control-actions {
  margin-top: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.zoom-slider-box {
  display: flex;
  align-items: center;
  gap: 12px;
}
.slider-label {
  font-size: 13px;
  color: var(--el-text-color-secondary);
  width: 32px;
}
.tool-buttons {
  display: flex;
  gap: 10px;
}
</style>
