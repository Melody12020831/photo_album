<template>
  <div class="upload-container" :class="{ 'dark': isDark }">
    <div class="top-bar-absolute">
      <el-switch
        v-model="isDark"
        inline-prompt
        :active-icon="Moon"
        :inactive-icon="Sunny"
        style="--el-switch-on-color: #4c4d4f; --el-switch-off-color: #d4b483"
        @change="toggleTheme"
      />
    </div>

    <div class="upload-header">
      <h2>上传照片</h2>
      <p>添加到您的速写本 · EXIF 自动识别 · AI 智能标签</p>
    </div>

    <el-form ref="formRef" label-position="top">
      <!-- 拖拽上传区域 -->
      <div 
        class="drop-zone"
        :class="{ 'is-dragover': isDragOver }"
        @dragover.prevent="isDragOver = true"
        @dragleave.prevent="isDragOver = false"
        @drop.prevent="handleDrop"
        @click="triggerFileInput"
      >
        <el-icon class="upload-icon"><UploadFilled /></el-icon>
        <div class="upload-text">
          <span>点击或拖拽图片到此处</span>
          <p class="sub-text">支持 JPG, PNG, WebP 等格式</p>
        </div>
        <input 
          ref="fileInputRef" 
          type="file" 
          accept="image/*" 
          multiple 
          class="hidden-input"
          @change="onFileChange" 
        />
      </div>

      <!-- 功能操作栏 -->
      <div v-if="photoItems.length > 0" class="action-bar">
        <div class="left-actions">
          <span class="selection-count">已选 {{ photoItems.length }} 张图片</span>
          <el-button link class="theme-link-btn" @click="showBatchTagDialog">批量标签</el-button>
          <el-divider direction="vertical" />
          <el-button link class="theme-link-btn" @click="batchToggleAI(true)">全开 AI</el-button>
          <el-button link class="theme-link-btn secondary" @click="batchToggleAI(false)">全关 AI</el-button>
        </div>
        <div class="right-actions">
          <el-button type="danger" link @click="resetForm">清空</el-button>
          <el-button type="primary" size="large" @click="onUploadAll" :loading="uploading" class="upload-btn">
            开始上传
          </el-button>
        </div>
      </div>

      <!-- 图片预览网格 -->
      <transition-group name="list" tag="div" class="photo-grid">
        <div v-for="(item, index) in photoItems" :key="item.previewUrl" class="photo-card">
          <div class="photo-thumb">
            <img :src="item.previewUrl" :alt="item.file.name" />
            <div class="overlay">
              <el-button type="danger" circle size="small" @click.stop="removePhotoItem(index)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
            <div class="img-meta-badge" v-if="item.file.size">{{ formatSize(item.file.size) }}</div>
          </div>
          
          <div class="photo-form">
            <el-input 
              v-model="item.description" 
              placeholder="添加描述..." 
              size="small"
              class="desc-input theme-input"
            />
            
            <div class="tag-input-wrapper">
              <el-select
                v-model="item.tags"
                multiple
                filterable
                allow-create
                default-first-option
                placeholder="添加标签"
                size="small"
                class="tag-select theme-select"
              >
                <el-option v-for="tag in tagOptions" :key="tag" :label="tag" :value="tag" />
              </el-select>
              <el-tooltip content="新建标签" placement="top">
                <el-button size="small" circle @click="createNewTagForItem(item)">
                  <el-icon><Plus /></el-icon>
                </el-button>
              </el-tooltip>
            </div>

            <div class="ai-switch">
              <el-checkbox v-model="item.useAI" size="small" class="theme-checkbox">AI 分析</el-checkbox>
            </div>
          </div>
        </div>
      </transition-group>
    </el-form>

    <!-- 批量标签对话框 -->
    <el-dialog v-model="batchTagDialogVisible" title="批量添加标签" width="400px" class="custom-dialog">
      <p class="dialog-desc">将标签添加到当前所有图片中</p>
      <div class="flex-row" style="display: flex; gap: 8px;">
        <el-select v-model="batchTags" multiple filterable allow-create default-first-option placeholder="选择或输入标签" style="flex: 1">
          <el-option v-for="tag in tagOptions" :key="tag" :label="tag" :value="tag" />
        </el-select>
        <el-button @click="createNewTagForBatch">新建</el-button>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="batchTagDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="applyBatchTags" :disabled="batchTags.length === 0">应用</el-button>
        </span>
      </template>
    </el-dialog>

    <el-dialog v-model="aiDialogVisible" title="AI 智能分析中" width="450px" :before-close="handleAiDialogCancel" class="custom-dialog">
      <div v-loading="aiLoading" element-loading-text="AI 正在思考..." class="ai-content">
        <p class="progress-text">正在分析第 <span>{{ currentAIIndex + 1 }}</span> / {{ aiQueue.length }} 张</p>
        <div v-if="suggestedTags.length > 0" class="ai-suggestions">
          <p class="sub-title">AI 建议标签：</p>
          <el-checkbox-group v-model="finalTagSelection">
            <el-checkbox v-for="tag in suggestedTags" :key="tag" :label="tag" border size="small" class="theme-checkbox" />
          </el-checkbox-group>
        </div>
        <el-divider content-position="center">确认标签</el-divider>
        <el-select v-model="finalTagSelection" multiple filterable allow-create default-first-option placeholder="最终确认的标签" style="width: 100%">
          <el-option v-for="tag in allAvailableTags" :key="tag" :label="tag" :value="tag" />
        </el-select>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="skipCurrentAI">跳过</el-button>
          <el-button type="primary" @click="handleAiDialogConfirm">保存并继续</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { ElMessageBox, ElMessage } from 'element-plus'
import { UploadFilled, Delete, Plus, Moon, Sunny } from '@element-plus/icons-vue' 
import EXIF from 'exif-js'

const formRef = ref()
const photoItems = ref([])
const tagOptions = ref([])
const fileInputRef = ref(null)
const uploading = ref(false)
const isDragOver = ref(false)
const isDark = ref(false)

// 对话框相关状态
const batchTagDialogVisible = ref(false)
const batchTags = ref([])
const aiDialogVisible = ref(false)
const aiLoading = ref(false)
const aiQueue = ref([])
const currentAIIndex = ref(0)
const currentPhoto = ref(null)
const suggestedTags = ref([])
const finalTagSelection = ref([])


// 计算所有可用标签（用户标签、AI建议标签、最终选择标签的合集）
const allAvailableTags = computed(() => {
  const allTags = new Set([...tagOptions.value, ...suggestedTags.value, ...finalTagSelection.value]);
  return Array.from(allTags).sort();
});


// 组件挂载时初始化用户标签和主题
onMounted(() => {
  fetchUserTags()
  initTheme()
})


// 初始化主题（深色/浅色）
function initTheme() {
  const storedTheme = localStorage.getItem('theme')
  if (storedTheme) {
    isDark.value = storedTheme === 'dark'
  } else {
    isDark.value = window.matchMedia('(prefers-color-scheme: dark)').matches
  }
  applyTheme(isDark.value)
}


// 切换主题（深色/浅色）
function toggleTheme(val) {
  isDark.value = val
  localStorage.setItem('theme', val ? 'dark' : 'light')
  applyTheme(val)
}


// 应用主题样式到页面
function applyTheme(dark) {
  if (dark) {
    document.documentElement.classList.add('dark')
    document.body.style.backgroundColor = '#1a1a1a'
  } else {
    document.documentElement.classList.remove('dark')
    document.body.style.backgroundColor = '#fdfaf4'
  }
}


// 获取当前用户的所有标签
async function fetchUserTags() {
  const token = sessionStorage.getItem('token')
  if (!token) return
  try {
    const res = await axios.get('/api/user_tags/', { headers: { Authorization: `Token ${token}` } })
    tagOptions.value = res.data.tags || []
  } catch (e) { tagOptions.value = [] }
}


// 处理拖拽上传图片事件
function handleDrop(e) {
  isDragOver.value = false
  const files = e.dataTransfer.files
  if (files.length) processFiles(files)
}

// 触发文件选择框点击
function triggerFileInput() { fileInputRef.value.click() }

// 处理文件选择变化事件
function onFileChange(e) { processFiles(e.target.files); e.target.value = '' }

// 格式化文件大小显示
function formatSize(size) {
  if(size < 1024) return size + ' B'
  if(size < 1024*1024) return (size/1024).toFixed(1) + ' KB'
  return (size/(1024*1024)).toFixed(1) + ' MB'
}

// 处理用户选择或拖拽的图片文件
async function processFiles(files) {
  for (const file of Array.from(files)) {
    if (!file.type.startsWith('image/')) continue
    const previewUrl = URL.createObjectURL(file)
    const photoItem = { file: file, previewUrl: previewUrl, description: '', tags: [], useAI: true }
    photoItems.value.push(photoItem)
    processEXIF(file, photoItem)
  }
}

// 解析图片 EXIF 信息并自动添加标签
async function processEXIF(file, photoItem) {
  EXIF.getData(file, async function() {
    const make = EXIF.getTag(this, "Make");
    const model = EXIF.getTag(this, "Model");
    const potentialTags = [make, model].filter(t => t && typeof t.trim === 'function' && t.trim());
    if (potentialTags.length > 0) {
      potentialTags.forEach(tag => { if(!photoItem.tags.includes(tag)) photoItem.tags.push(tag) })
    }
  });
}

// 移除指定索引的图片
function removePhotoItem(index) { URL.revokeObjectURL(photoItems.value[index].previewUrl); photoItems.value.splice(index, 1) }

// 重置上传表单，清空所有图片
function resetForm() { photoItems.value.forEach(item => URL.revokeObjectURL(item.previewUrl)); photoItems.value = []; if (fileInputRef.value) fileInputRef.value.value = null }

// 为单张图片新建标签
async function createNewTagForItem(item) { promptAndCreateTag((tag) => { if(!item.tags.includes(tag)) item.tags.push(tag) }) }

// 批量新建标签
async function createNewTagForBatch() { promptAndCreateTag((tag) => { if(!batchTags.value.includes(tag)) batchTags.value.push(tag) }) }

// 弹窗输入新标签并保存到服务器
async function promptAndCreateTag(callback) {
  try {
    const { value } = await ElMessageBox.prompt('标签名', '新建', { confirmButtonText: '确定', cancelButtonText: '取消', inputPattern: /\S/ });
    if (value) {
      const token = sessionStorage.getItem('token');
      await axios.post('/api/user_tags/', { tag: value }, { headers: { Authorization: `Token ${token}` } });
      ElMessage.success('创建成功');
      await fetchUserTags();
      callback(value);
    }
  } catch (e) { /* cancel */ }
}

// 显示批量标签对话框
function showBatchTagDialog() { batchTags.value = []; batchTagDialogVisible.value = true }

// 应用批量标签到所有图片
function applyBatchTags() { photoItems.value.forEach(item => { batchTags.value.forEach(tag => { if(!item.tags.includes(tag)) item.tags.push(tag) }) }); batchTagDialogVisible.value = false; ElMessage.success('已添加') }

// 批量切换所有图片的 AI 分析开关
function batchToggleAI(val) { photoItems.value.forEach(item => item.useAI = val) }

// 上传所有图片到服务器，并根据需要进入 AI 分析流程
async function onUploadAll() {
  if (photoItems.value.length === 0) return
  uploading.value = true
  const uploadResults = []
  let successCount = 0
  for (const item of photoItems.value) {
    try {
      const token = sessionStorage.getItem('token')
      const data = new FormData()
      data.append('image', item.file)
      data.append('description', item.description)
      item.tags.forEach(tag => data.append('tags', tag))
      const res = await axios.post('/api/upload_photo/', data, { headers: { 'Content-Type': 'multipart/form-data', 'Authorization': `Token ${token}` } })
      successCount++
      if (item.useAI && res.data.photo) uploadResults.push({ photo: res.data.photo, useAI: true })
    } catch (e) { console.error('Upload failed', e) }
  }
  uploading.value = false
  ElMessage.success(`上传完成：${successCount} 张`)
  if (uploadResults.length > 0) { aiQueue.value = uploadResults; currentAIIndex.value = 0; processNextAI() } else { resetForm() }
}

// 处理下一个需要 AI 分析的图片
async function processNextAI() {
  if (currentAIIndex.value >= aiQueue.value.length) { ElMessage.success('AI分析完成'); resetForm(); return }
  const item = aiQueue.value[currentAIIndex.value]
  triggerAiAnalysis(item.photo)
}

// 向后端请求 AI 分析图片标签
async function triggerAiAnalysis(photo) {
  currentPhoto.value = photo; aiDialogVisible.value = true; aiLoading.value = true; finalTagSelection.value = [...photo.tags]; suggestedTags.value = []
  try {
    const token = sessionStorage.getItem('token')
    const res = await axios.post(`/api/photos/${photo.id}/analyze-tags/`, {}, { headers: { Authorization: `Token ${token}` } })
    suggestedTags.value = res.data.suggested_tags || []
  } catch (e) { ElMessage.warning('AI问题') } finally { aiLoading.value = false }
}

// 确认 AI 分析标签并保存
async function handleAiDialogConfirm() {
  const token = sessionStorage.getItem('token')
  try {
    await axios.post('/api/update_photo_tags/', { photo_id: currentPhoto.value.id, tags: finalTagSelection.value }, { headers: { Authorization: `Token ${token}` } })
    currentAIIndex.value++; aiDialogVisible.value = false; setTimeout(processNextAI, 300)
  } catch(e) { ElMessage.error('更新失败') }
}

// 跳过当前图片的 AI 分析
function skipCurrentAI() { currentAIIndex.value++; aiDialogVisible.value = false; setTimeout(processNextAI, 300) }

// 关闭 AI 分析对话框并重置表单
function handleAiDialogCancel() { resetForm() }
</script>

<style scoped>
/* 适配深色模式 */
.upload-container {
  max-width: 1000px;
  margin: 20px auto;
  padding: 30px;
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.04);
  transition: background 0.3s, border-color 0.3s;
}
.upload-container.dark {
  background: #2c2c2c;
  box-shadow: 0 10px 30px rgba(0,0,0,0.4);
}

.top-bar-absolute {
  position: absolute;
  top: 20px;
  right: 20px;
}

.upload-header { text-align: center; margin-bottom: 30px; }
.upload-header h2 { margin: 0 0 8px; font-size: 1.8rem; color: #4a4a4a; }
.dark .upload-header h2 { color: #e0e0e0; }
.upload-header p { color: #8c7b75; font-size: 0.9rem; }
.dark .upload-header p { color: #a0a0a0; }

.drop-zone {
  border: 2px dashed #dcdfe6;
  border-radius: 12px;
  padding: 40px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #fbfdff;
}
.dark .drop-zone { background: #333; border-color: #555; }
.drop-zone:hover, .drop-zone.is-dragover { border-color: #8c7b75; background: #fdfaf4; }
.dark .drop-zone:hover { border-color: #d4b483; background: #3a3a3a; }

.upload-icon { font-size: 48px; color: #8c7b75; margin-bottom: 16px; }
.dark .upload-icon { color: #d4b483; }
.upload-text span { font-size: 1.1rem; font-weight: 500; color: #606266; }
.dark .upload-text span { color: #ccc; }
.sub-text { font-size: 0.85rem; color: #c0c4cc; margin-top: 4px; }
.hidden-input { display: none; }

.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 24px 0 16px;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 8px;
}
.dark .action-bar { background: #3a3a3a; }
.selection-count { font-size: 0.9rem; color: #606266; margin-right: 12px; font-weight: 600; }
.dark .selection-count { color: #ccc; }

.theme-link-btn { color: #8c7b75 !important; font-weight: 500; }
.theme-link-btn:hover { color: #6b5b56 !important; }
.theme-link-btn.secondary { color: #909399 !important; }
.dark .theme-link-btn { color: #d4b483 !important; }

.photo-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 20px; }
.photo-card { background: #fff; border: 1px solid #ebeef5; border-radius: 8px; overflow: hidden; transition: all 0.3s; }
.dark .photo-card { background: #333; border-color: #555; }
.photo-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.08); transform: translateY(-2px); }

.photo-thumb { height: 160px; position: relative; background: #f5f7fa; }
.photo-thumb img { width: 100%; height: 100%; object-fit: cover; }
.photo-thumb .overlay { position: absolute; top: 8px; right: 8px; opacity: 0; transition: opacity 0.2s; }
.photo-card:hover .overlay { opacity: 1; }
.img-meta-badge { position: absolute; bottom: 4px; right: 4px; background: rgba(0,0,0,0.6); color: #fff; font-size: 10px; padding: 2px 6px; border-radius: 4px; }

.photo-form { padding: 12px; }
.tag-input-wrapper { display: flex; gap: 4px; margin-bottom: 8px; }
.tag-select { flex: 1; }

.theme-input :deep(.el-input__wrapper),
.theme-select :deep(.el-input__wrapper) {
  box-shadow: 0 0 0 1px #dcdfe6;
}
.dark .theme-input :deep(.el-input__wrapper),
.dark .theme-select :deep(.el-input__wrapper) {
  background: #444; box-shadow: 0 0 0 1px #555;
}
.dark .theme-input :deep(.el-input__inner) { color: #eee; }

.theme-checkbox :deep(.el-checkbox__label) { color: #606266; }
.dark .theme-checkbox :deep(.el-checkbox__label) { color: #ccc; }
.theme-checkbox :deep(.el-checkbox__input.is-checked .el-checkbox__inner) { background-color: #8c7b75; border-color: #8c7b75; }
.dark .theme-checkbox :deep(.el-checkbox__input.is-checked .el-checkbox__inner) { background-color: #d4b483; border-color: #d4b483; }
.theme-checkbox :deep(.el-checkbox__input.is-checked + .el-checkbox__label) { color: #8c7b75; }
.dark .theme-checkbox :deep(.el-checkbox__input.is-checked + .el-checkbox__label) { color: #d4b483; }

.list-enter-active, .list-leave-active { transition: all 0.3s ease; }
.list-enter-from, .list-leave-to { opacity: 0; transform: translateY(20px); }

.el-button--primary:not(.is-link) { --el-button-bg-color: #8c7b75; --el-button-border-color: #8c7b75; }
.el-button--primary:not(.is-link):hover { --el-button-bg-color: #7a6a65; --el-button-border-color: #7a6a65; }
.dark .el-button--primary:not(.is-link) { --el-button-bg-color: #d4b483; --el-button-border-color: #d4b483; --el-button-text-color: #333; }
</style>