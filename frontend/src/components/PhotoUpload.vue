<template>
  <div class="photo-upload">
    <el-form ref="formRef" :model="form" label-width="80px">
      <el-form-item label="图片">
        <input ref="fileInputRef" type="file" accept="image/*" @change="onFileChange" />
      </el-form-item>
      <el-form-item label="描述">
        <el-input v-model="form.description" placeholder="图片描述（可选）" />
      </el-form-item>
      <el-form-item label="标签">
        <el-select
          v-model="form.tags"
          multiple
          placeholder="请选择标签"
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
        <el-button style="margin-left: 8px;" @click="createNewTag(form.tags)">新建标签</el-button>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="onUpload" :loading="loading">上传</el-button>
      </el-form-item>
    </el-form>
    <div v-if="msg" :class="msgType">{{ msg }}</div>

    <el-dialog
      v-model="aiDialogVisible"
      title="AI 标签分析"
      width="500px"
      :before-close="handleAiDialogCancel"
    >
      <div v-loading="aiLoading">
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
          <el-button @click="handleAiDialogCancel">取消</el-button>
          <el-button type="primary" @click="handleAiDialogConfirm">
            保存标签
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
const form = ref({ file: null, description: '', tags: [] })
const tagOptions = ref([])
const tagLoading = ref(false)

const fileInputRef = ref(null) // 用于重置文件输入框
const loading = ref(false)
const msg = ref('')
const msgType = ref('')

const aiDialogVisible = ref(false)
const aiLoading = ref(false)
const currentPhoto = ref(null)    // 存储当前上传的图片信息
const suggestedTags = ref([])   // AI分析出的标签
const finalTagSelection = ref([]) // AI弹窗中，用户最终选择的标签

// 计算属性，合并用户已有标签和AI建议标签，用于弹窗中的 el-select
const allAvailableTags = computed(() => {
  const allTags = new Set([...tagOptions.value, ...suggestedTags.value, ...finalTagSelection.value]);
  return Array.from(allTags).sort();
});

// 获取用户所有标签
async function fetchUserTags() {
  const token = localStorage.getItem('token')
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

// 重构 createNewTag，使其可以操作任意标签数组
async function createNewTag(targetTagList) { // 接收一个 ref 数组
  try {
    const { value } = await ElMessageBox.prompt('请输入新的标签名', '新建标签', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputPattern: /\S/,
      inputErrorMessage: '标签名不能为空'
    });

    if (value) {
      const token = localStorage.getItem('token');
      const res = await axios.post('/api/user_tags/', { tag: value }, {
        headers: { Authorization: `Token ${token}` }
      });

      ElMessage.success(res.data.msg || '操作成功');
      
      // 刷新标签列表并将新标签选中
      await fetchUserTags();
      if (!targetTagList.includes(value)) {
        targetTagList.push(value); // 操作传入的目标数组
      }
    }
  } catch (error) {
    if (error !== 'cancel') {
      const errorMsg = error.response?.data?.error || '创建失败';
      ElMessage.error(errorMsg);
    }
  }
}

function onFileChange(e) {
  const file = e.target.files[0]
  if (!file) return;
  form.value.file = file

  // EXIF.js 读取逻辑
  EXIF.getData(file, async function() {
    const make = EXIF.getTag(this, "Make");
    const model = EXIF.getTag(this, "Model");
    const dateTime = EXIF.getTag(this, "DateTimeOriginal");

    const potentialTags = [make, model, dateTime].filter(tag => tag && typeof tag === 'string' && tag.trim());
    
    const newExifTags = potentialTags.filter(
      tag => !tagOptions.value.includes(tag) && !form.value.tags.includes(tag)
    );
    
    if (newExifTags.length > 0) {
      try {
        await ElMessageBox.confirm(
          `我们从图片中识别出以下新信息：[${newExifTags.join(', ')}]，是否将它们创建为新标签并添加到此图片？`,
          '发现新标签',
          {
            confirmButtonText: '是，创建并添加',
            cancelButtonText: '否，忽略',
            type: 'info',
          }
        )
        for (const tag of newExifTags) {
          const token = localStorage.getItem('token');
          await axios.post('/api/user_tags/', { tag }, {
             headers: { Authorization: `Token ${token}` }
          });
          if (!form.value.tags.includes(tag)) {
            form.value.tags.push(tag);
          }
        }
        await fetchUserTags();

      } catch (action) {
        console.log('用户选择不添加EXIF标签。');
      }
    }
  });
}

// 重置表单和状态的辅助函数
function resetForm() {
  msg.value = ''
  msgType.value = ''
  form.value.file = null
  form.value.description = ''
  form.value.tags = []
  if (formRef.value) formRef.value.resetFields()
  if (fileInputRef.value) fileInputRef.value.value = null // 清空文件选择框
  
  // 重置AI状态
  aiDialogVisible.value = false
  aiLoading.value = false
  currentPhoto.value = null
  suggestedTags.value = []
  finalTagSelection.value = []
}

// 重构 onUpload 函数
async function onUpload() {
  if (!form.value.file) {
    msg.value = '请选择图片文件';
    msgType.value = 'error';
    return;
  }
  loading.value = true
  msg.value = ''
  msgType.value = ''
  try {
    const token = localStorage.getItem('token')
    const data = new FormData()
    data.append('image', form.value.file)
    data.append('description', form.value.description)

    if (form.value.tags.length) {
      form.value.tags.forEach(tag => {
        data.append('tags', tag) // 多次 append 同一个 key
      })
    }
    
    const res = await axios.post('/api/upload_photo/', data, {
      headers: {
        'Content-Type': 'multipart/form-data',
        'Authorization': `Token ${token}`
      }
    })

    msg.value = res.data.msg || '上传成功'
    msgType.value = 'success'

    //  从响应中获取完整的 photo 对象
    const uploadedPhoto = res.data.photo 
    if (!uploadedPhoto || !uploadedPhoto.id) {
        throw new Error("后端未正确返回图片信息");
    }

    // 上传成功后弹窗询问是否启用AI分析
    try {
      await ElMessageBox.confirm(
        '图片上传成功，是否启用AI模型分析图片标签？',
        'AI标签分析',
        {
          confirmButtonText: '是，分析图片',
          cancelButtonText: '否，稍后处理',
          type: 'info',
        }
      )
      // 用户选择启用AI分析 -> 触发AI分析流程
      triggerAiAnalysis(uploadedPhoto)

    } catch (aiAction) {
      // 用户选择不启用AI分析或取消
      console.log('用户未启用AI分析')
      resetForm() // 同样重置表单
    }

  } catch (e) {
    let detail = ''
    if (e.response && e.response.data) {
      detail = JSON.stringify(e.response.data)
    } else {
      detail = e.message
    }
    msg.value = `上传失败: ${detail}`
    msgType.value = 'error'
    console.error('上传失败', e, detail);
  } finally {
    loading.value = false
  }
}

// 触发 AI 分析的函数
async function triggerAiAnalysis(photo) {
  currentPhoto.value = photo
  aiDialogVisible.value = true
  aiLoading.value = true
  
  // 预先填入用户在上传时已选择的标签
  finalTagSelection.value = [...photo.tags]
  suggestedTags.value = []

  try {
    const token = localStorage.getItem('token')
    // 调用新的 AI 分析接口
    const res = await axios.post(`/api/photos/${photo.id}/analyze-tags/`, {}, {
      headers: { Authorization: `Token ${token}` }
    })
    
    suggestedTags.value = res.data.suggested_tags || []
    
    if (suggestedTags.value.length > 0) {
      ElMessage.success('AI分析完成')
      // 自动合并 AI 标签到最终选择中（去重）
      const allTags = new Set([...finalTagSelection.value, ...suggestedTags.value])
      finalTagSelection.value = Array.from(allTags)
    } else {
      ElMessage.info('AI未分析出任何标签，您可以手动添加。')
    }

  } catch (e) {
    ElMessage.error(e.response?.data?.error || 'AI分析失败')
    // 失败了也保持弹窗打开，让用户可以手动添加
  } finally {
    aiLoading.value = false
  }
}

// 处理 AI 弹窗确认
async function handleAiDialogConfirm() {
  if (!currentPhoto.value) return;
  const token = localStorage.getItem('token')
  try {
    // 调用更新标签的接口
    await axios.post('/api/update_photo_tags/', {
      photo_id: currentPhoto.value.id,
      tags: finalTagSelection.value // 发送最终的标签列表
    }, {
      headers: { Authorization: `Token ${token}` }
    })
    ElMessage.success('标签已更新')
    resetForm() // 完成后重置
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '标签更新失败')
  }
}

// 处理 AI 弹窗取消
function handleAiDialogCancel() {
  resetForm() // 取消也重置表单
}

onMounted(() => {
  fetchUserTags()
})
</script>

<style scoped>
.photo-upload {
  max-width: 400px;
  margin: 24px auto;
  padding: 24px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.success {
  color: #409eff;
  margin-top: 10px;
}
.error {
  color: #f56c6c;
  margin-top: 10px;
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