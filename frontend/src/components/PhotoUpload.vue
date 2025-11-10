<template>
  <div class="photo-upload">
    <el-form ref="formRef" label-width="80px">
      <el-form-item label="选择图片">
        <input 
          ref="fileInputRef" 
          type="file" 
          accept="image/*" 
          multiple 
          @change="onFileChange" 
        />
        <div class="file-hint">可同时选择多张图片</div>
      </el-form-item>

      <!-- 图片预览列表 -->
      <div v-if="photoItems.length > 0" class="photo-items">
        <el-card 
          v-for="(item, index) in photoItems" 
          :key="index" 
          class="photo-item"
          shadow="hover"
        >
          <div class="photo-item-header">
            <span class="photo-number">图片 {{ index + 1 }}</span>
            <el-button 
              type="danger" 
              size="small" 
              text
              @click="removePhotoItem(index)"
            >
              删除
            </el-button>
          </div>

          <!-- 图片预览 -->
          <div class="photo-preview">
            <img :src="item.previewUrl" :alt="item.file.name" />
          </div>

          <div class="photo-name">{{ item.file.name }}</div>

          <!-- 描述 -->
          <el-form-item label="描述" label-width="60px">
            <el-input 
              v-model="item.description" 
              placeholder="图片描述（可选）" 
              type="textarea"
              :rows="2"
            />
          </el-form-item>

          <!-- 标签 -->
          <el-form-item label="标签" label-width="60px">
            <div style="display: flex; gap: 8px;">
              <el-select
                v-model="item.tags"
                multiple
                placeholder="请选择或输入标签"
                style="flex: 1;"
                :loading="tagLoading"
                filterable
                allow-create
                default-first-option
              >
                <el-option
                  v-for="tag in tagOptions"
                  :key="tag"
                  :label="tag"
                  :value="tag"
                />
              </el-select>
              <el-button 
                size="small" 
                @click="createNewTagForItem(item)"
              >
                新建
              </el-button>
            </div>
            <div v-if="tagOptions.length === 0" style="font-size: 12px; color: #909399; margin-top: 4px;">
              暂无标签，请先创建
            </div>
          </el-form-item>

          <!-- AI分析选项 -->
          <el-form-item label="AI分析" label-width="60px">
            <el-checkbox v-model="item.useAI">上传后使用AI分析标签</el-checkbox>
          </el-form-item>
        </el-card>
      </div>

      <!-- 批量操作按钮 -->
      <div v-if="photoItems.length > 0" class="batch-actions">
        <el-button @click="showBatchTagDialog">批量添加标签</el-button>
        <el-button @click="batchToggleAI(true)">全部启用AI</el-button>
        <el-button @click="batchToggleAI(false)">全部禁用AI</el-button>
      </div>

      <el-form-item v-if="photoItems.length > 0">
        <el-button 
          type="primary" 
          @click="onUploadAll" 
          :loading="uploading"
          size="large"
        >
          上传全部图片 ({{ photoItems.length }})
        </el-button>
      </el-form-item>
    </el-form>

    <div v-if="msg" :class="msgType">{{ msg }}</div>

    <!-- 批量添加标签对话框 -->
    <el-dialog
      v-model="batchTagDialogVisible"
      title="批量添加标签"
      width="500px"
    >
      <div>
        <p v-if="tagOptions.length === 0" style="color: #909399; margin-bottom: 12px;">
          暂无标签，请先创建标签
        </p>
        <p v-else style="color: #606266; margin-bottom: 12px;">
          已有 {{ tagOptions.length }} 个标签可选
        </p>
        <el-select
          v-model="batchTags"
          multiple
          placeholder="选择或输入要批量添加的标签"
          style="width: calc(100% - 90px);"
          :loading="tagLoading"
          filterable
          allow-create
          default-first-option
        >
          <el-option
            v-for="tag in tagOptions"
            :key="tag"
            :label="tag"
            :value="tag"
          />
        </el-select>
        <el-button 
          style="margin-left: 8px;" 
          @click="createNewTagForBatch"
        >
          新建标签
        </el-button>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="batchTagDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="applyBatchTags" :disabled="batchTags.length === 0">
            应用到所有图片
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- AI分析对话框 -->
    <el-dialog
      v-model="aiDialogVisible"
      title="AI 标签分析"
      width="500px"
      :before-close="handleAiDialogCancel"
    >
      <div v-loading="aiLoading">
        <p class="ai-progress">正在分析第 {{ currentAIIndex + 1 }} / {{ aiQueue.length }} 张图片</p>
        
        <div v-if="suggestedTags.length > 0">
          <p>AI 建议以下标签，请勾选：</p>
          <el-checkbox-group v-model="finalTagSelection">
            <el-checkbox v-for="tag in suggestedTags" :key="tag" :label="tag" border />
          </el-checkbox-group>
        </div>
        <p v-if="suggestedTags.length === 0 && !aiLoading">
          AI 未分析出任何标签，您可以手动添加。
        </p>
        
        <el-divider />
        
        <p>管理此图片的所有标签：</p>
        <el-select
          v-model="finalTagSelection"
          multiple
          placeholder="选择或输入标签"
          style="width: calc(100% - 90px);"
          :loading="tagLoading"
          filterable
          allow-create
          default-first-option
        >
          <el-option
            v-for="tag in allAvailableTags"
            :key="tag"
            :label="tag"
            :value="tag"
          />
        </el-select>
        <el-button style="margin-left: 8px;" @click="createNewTag(finalTagSelection)">新建</el-button>
      </div>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="skipCurrentAI">跳过</el-button>
          <el-button type="primary" @click="handleAiDialogConfirm">
            保存标签并继续
          </el-button>
        </span>
      </template>
    </el-dialog>

  </div>
</template>

<script setup>

import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { ElMessageBox, ElMessage, ElDialog, ElCheckbox, ElCheckboxGroup, ElDivider } from 'element-plus'
import EXIF from 'exif-js'

const formRef = ref()
const photoItems = ref([]) // 存储多张图片的信息
const tagOptions = ref([])
const tagLoading = ref(false)

const fileInputRef = ref(null)
const uploading = ref(false)
const msg = ref('')
const msgType = ref('')

// 批量标签对话框
const batchTagDialogVisible = ref(false)
const batchTags = ref([])

// AI分析相关
const aiDialogVisible = ref(false)
const aiLoading = ref(false)
const aiQueue = ref([]) // 需要AI分析的图片队列
const currentAIIndex = ref(0)
const currentPhoto = ref(null)
const suggestedTags = ref([])
const finalTagSelection = ref([])

// 计算属性，合并用户已有标签和AI建议标签
const allAvailableTags = computed(() => {
  const allTags = new Set([...tagOptions.value, ...suggestedTags.value, ...finalTagSelection.value]);
  return Array.from(allTags).sort();
});

// 获取用户所有标签
async function fetchUserTags() {
  const token = sessionStorage.getItem('token')
  if (!token) return
  tagLoading.value = true
  try {
    const res = await axios.get('/api/user_tags/', {
      headers: { Authorization: `Token ${token}` }
    })
    tagOptions.value = res.data.tags || []
  } catch (e) {
    tagOptions.value = []
  } finally {
    tagLoading.value = false
  }
}

// 创建新标签（通用函数）
async function createNewTag(targetTagList) {
  try {
    const { value } = await ElMessageBox.prompt('请输入新的标签名', '新建标签', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputPattern: /\S/,
      inputErrorMessage: '标签名不能为空'
    });

    if (value) {
      const token = sessionStorage.getItem('token');
      const res = await axios.post('/api/user_tags/', { tag: value }, {
        headers: { Authorization: `Token ${token}` }
      });

      ElMessage.success(res.data.msg || '操作成功');
      
      await fetchUserTags();
      if (!targetTagList.includes(value)) {
        targetTagList.push(value);
      }
    }
  } catch (error) {
    if (error !== 'cancel') {
      const errorMsg = error.response?.data?.error || '创建失败';
      ElMessage.error(errorMsg);
    }
  }
}

// 为单个图片项创建新标签
async function createNewTagForItem(item) {
  try {
    const { value } = await ElMessageBox.prompt('请输入新的标签名', '新建标签', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputPattern: /\S/,
      inputErrorMessage: '标签名不能为空'
    });

    if (value) {
      const token = sessionStorage.getItem('token');
      const res = await axios.post('/api/user_tags/', { tag: value }, {
        headers: { Authorization: `Token ${token}` }
      });

      ElMessage.success(res.data.msg || '标签创建成功');
      
      // 刷新标签列表
      await fetchUserTags();
      
      // 自动添加到当前图片的标签中
      if (!item.tags.includes(value)) {
        item.tags.push(value);
      }
    }
  } catch (error) {
    if (error !== 'cancel') {
      const errorMsg = error.response?.data?.error || '创建失败';
      ElMessage.error(errorMsg);
    }
  }
}

// 处理文件选择（支持多选）
async function onFileChange(e) {
  const files = Array.from(e.target.files)
  if (files.length === 0) return

  for (const file of files) {
    // 创建预览URL
    const previewUrl = URL.createObjectURL(file)
    
    // 初始化图片项
    const photoItem = {
      file: file,
      previewUrl: previewUrl,
      description: '',
      tags: [],
      useAI: true, // 默认启用AI分析
      exifProcessed: false
    }

    photoItems.value.push(photoItem)

    // 异步读取EXIF信息
    processEXIF(file, photoItem)
  }
}

// 处理EXIF信息
async function processEXIF(file, photoItem) {
  EXIF.getData(file, async function() {
    const make = EXIF.getTag(this, "Make");
    const model = EXIF.getTag(this, "Model");
    const dateTime = EXIF.getTag(this, "DateTimeOriginal");

    const potentialTags = [make, model, dateTime].filter(tag => tag && typeof tag === 'string' && tag.trim());
    
    const newExifTags = potentialTags.filter(
      tag => !tagOptions.value.includes(tag) && !photoItem.tags.includes(tag)
    );
    
    if (newExifTags.length > 0 && !photoItem.exifProcessed) {
      photoItem.exifProcessed = true
      try {
        await ElMessageBox.confirm(
          `从图片 "${file.name}" 中识别出：[${newExifTags.join(', ')}]，是否将它们创建为新标签并添加到此图片？`,
          '发现新标签',
          {
            confirmButtonText: '是，创建并添加',
            cancelButtonText: '否，忽略',
            type: 'info',
          }
        )
        
        const token = sessionStorage.getItem('token');
        for (const tag of newExifTags) {
          try {
            await axios.post('/api/user_tags/', { tag }, {
              headers: { Authorization: `Token ${token}` }
            });
            if (!photoItem.tags.includes(tag)) {
              photoItem.tags.push(tag);
            }
          } catch (e) {
            console.error('创建EXIF标签失败:', e)
          }
        }
        await fetchUserTags();

      } catch (action) {
        console.log('用户选择不添加EXIF标签。');
      }
    }
  });
}

// 删除图片项
function removePhotoItem(index) {
  // 释放预览URL
  URL.revokeObjectURL(photoItems.value[index].previewUrl)
  photoItems.value.splice(index, 1)
  
  // 如果没有图片了，重置文件输入框
  if (photoItems.value.length === 0 && fileInputRef.value) {
    fileInputRef.value.value = null
  }
}

// 批量添加标签对话框
function showBatchTagDialog() {
  batchTags.value = []
  batchTagDialogVisible.value = true
}

// 为批量标签创建新标签
async function createNewTagForBatch() {
  try {
    const { value } = await ElMessageBox.prompt('请输入新的标签名', '新建标签', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputPattern: /\S/,
      inputErrorMessage: '标签名不能为空'
    });

    if (value) {
      const token = sessionStorage.getItem('token');
      const res = await axios.post('/api/user_tags/', { tag: value }, {
        headers: { Authorization: `Token ${token}` }
      });

      ElMessage.success(res.data.msg || '标签创建成功');
      
      // 刷新标签列表
      await fetchUserTags();
      
      // 自动添加到批量标签选择中
      if (!batchTags.value.includes(value)) {
        batchTags.value.push(value);
      }
    }
  } catch (error) {
    if (error !== 'cancel') {
      const errorMsg = error.response?.data?.error || '创建失败';
      ElMessage.error(errorMsg);
    }
  }
}

// 应用批量标签
function applyBatchTags() {
  if (batchTags.value.length === 0) {
    ElMessage.warning('请先选择要添加的标签')
    return
  }
  
  photoItems.value.forEach(item => {
    batchTags.value.forEach(tag => {
      if (!item.tags.includes(tag)) {
        item.tags.push(tag)
      }
    })
  })
  batchTagDialogVisible.value = false
  ElMessage.success(`已为所有图片添加 ${batchTags.value.length} 个标签`)
}

// 批量切换AI分析
function batchToggleAI(enabled) {
  photoItems.value.forEach(item => {
    item.useAI = enabled
  })
  ElMessage.success(enabled ? '已全部启用AI分析' : '已全部禁用AI分析')
}

// 上传所有图片
async function onUploadAll() {
  if (photoItems.value.length === 0) {
    ElMessage.warning('请先选择图片')
    return
  }

  uploading.value = true
  msg.value = ''
  msgType.value = ''

  const uploadResults = []
  let successCount = 0
  let failCount = 0

  // 逐个上传图片
  for (let i = 0; i < photoItems.value.length; i++) {
    const item = photoItems.value[i]
    
    try {
      const token = sessionStorage.getItem('token')
      const data = new FormData()
      data.append('image', item.file)
      data.append('description', item.description)

      if (item.tags.length) {
        item.tags.forEach(tag => {
          data.append('tags', tag)
        })
      }
      
      const res = await axios.post('/api/upload_photo/', data, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'Authorization': `Token ${token}`
        }
      })

      const uploadedPhoto = res.data.photo
      successCount++
      
      // 如果用户选择了使用AI分析，加入队列
      if (item.useAI && uploadedPhoto && uploadedPhoto.id) {
        uploadResults.push({
          photo: uploadedPhoto,
          useAI: true
        })
      }

      ElMessage.success(`${item.file.name} 上传成功 (${i + 1}/${photoItems.value.length})`)

    } catch (e) {
      failCount++
      let detail = ''
      if (e.response && e.response.data) {
        detail = JSON.stringify(e.response.data)
      } else {
        detail = e.message
      }
      ElMessage.error(`${item.file.name} 上传失败: ${detail}`)
      console.error('上传失败', e, detail)
    }
  }

  uploading.value = false

  // 显示上传结果
  if (successCount > 0) {
    msg.value = `成功上传 ${successCount} 张图片` + (failCount > 0 ? `，失败 ${failCount} 张` : '')
    msgType.value = failCount > 0 ? 'warning' : 'success'
  } else {
    msg.value = '所有图片上传失败'
    msgType.value = 'error'
  }

  // 如果有需要AI分析的图片，开始批量处理
  const aiItems = uploadResults.filter(r => r.useAI)
  if (aiItems.length > 0) {
    aiQueue.value = aiItems
    currentAIIndex.value = 0
    processNextAI()
  } else {
    // 没有AI分析需求，直接重置
    resetForm()
  }
}

// 处理下一个AI分析
async function processNextAI() {
  if (currentAIIndex.value >= aiQueue.value.length) {
    // 所有AI分析完成
    ElMessage.success('所有图片处理完成！')
    resetForm()
    return
  }

  const item = aiQueue.value[currentAIIndex.value]
  await triggerAiAnalysis(item.photo)
}

// 触发 AI 分析
async function triggerAiAnalysis(photo) {
  currentPhoto.value = photo
  aiDialogVisible.value = true
  aiLoading.value = true
  
  finalTagSelection.value = [...photo.tags]
  suggestedTags.value = []

  try {
    const token = sessionStorage.getItem('token')
    const res = await axios.post(`/api/photos/${photo.id}/analyze-tags/`, {}, {
      headers: { Authorization: `Token ${token}` }
    })
    
    suggestedTags.value = res.data.suggested_tags || []
    
    if (suggestedTags.value.length > 0) {
      ElMessage.success('AI分析完成')
      const allTags = new Set([...finalTagSelection.value, ...suggestedTags.value])
      finalTagSelection.value = Array.from(allTags)
    } else {
      ElMessage.info('AI未分析出任何标签，您可以手动添加。')
    }

  } catch (e) {
    ElMessage.error(e.response?.data?.error || 'AI分析失败')
  } finally {
    aiLoading.value = false
  }
}

// 处理 AI 弹窗确认
async function handleAiDialogConfirm() {
  if (!currentPhoto.value) return
  const token = sessionStorage.getItem('token')
  try {
    await axios.post('/api/update_photo_tags/', {
      photo_id: currentPhoto.value.id,
      tags: finalTagSelection.value
    }, {
      headers: { Authorization: `Token ${token}` }
    })
    ElMessage.success('标签已更新')
    
    // 继续下一个
    currentAIIndex.value++
    aiDialogVisible.value = false
    
    // 短暂延迟后处理下一个
    setTimeout(() => {
      processNextAI()
    }, 300)
    
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '标签更新失败')
  }
}

// 跳过当前AI分析
function skipCurrentAI() {
  currentAIIndex.value++
  aiDialogVisible.value = false
  
  setTimeout(() => {
    processNextAI()
  }, 300)
}

// 处理 AI 弹窗取消
function handleAiDialogCancel() {
  ElMessageBox.confirm(
    '还有图片未完成AI分析，确定要取消吗？',
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '继续分析',
      type: 'warning',
    }
  ).then(() => {
    resetForm()
  }).catch(() => {
    // 用户选择继续分析
  })
}

// 重置表单
function resetForm() {
  msg.value = ''
  msgType.value = ''
  
  // 释放所有预览URL
  photoItems.value.forEach(item => {
    URL.revokeObjectURL(item.previewUrl)
  })
  
  photoItems.value = []
  
  if (formRef.value) formRef.value.resetFields()
  if (fileInputRef.value) fileInputRef.value.value = null
  
  aiDialogVisible.value = false
  aiLoading.value = false
  aiQueue.value = []
  currentAIIndex.value = 0
  currentPhoto.value = null
  suggestedTags.value = []
  finalTagSelection.value = []
}

onMounted(() => {
  fetchUserTags()
})
</script>

<style scoped>
.photo-upload {
  max-width: 800px;
  margin: 24px auto;
  padding: 24px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.file-hint {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.photo-items {
  margin: 20px 0;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.photo-item {
  padding: 16px;
}

.photo-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.photo-number {
  font-weight: bold;
  color: #409eff;
}

.photo-preview {
  width: 100%;
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 12px;
}

.photo-preview img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.photo-name {
  font-size: 12px;
  color: #606266;
  margin-bottom: 12px;
  word-break: break-all;
}

.batch-actions {
  display: flex;
  gap: 8px;
  margin: 20px 0;
  flex-wrap: wrap;
}

.success {
  color: #67c23a;
  margin-top: 10px;
  padding: 8px;
  background: #f0f9ff;
  border-radius: 4px;
}

.warning {
  color: #e6a23c;
  margin-top: 10px;
  padding: 8px;
  background: #fdf6ec;
  border-radius: 4px;
}

.error {
  color: #f56c6c;
  margin-top: 10px;
  padding: 8px;
  background: #fef0f0;
  border-radius: 4px;
}

.ai-progress {
  font-weight: bold;
  color: #409eff;
  margin-bottom: 16px;
}

.el-checkbox-group {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 15px;
}

.el-checkbox.is-bordered {
  margin-left: 0;
  margin-right: 0;
}
</style>
