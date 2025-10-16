<template>
  <div class="photo-upload">
    <el-form ref="formRef" :model="form" label-width="80px">
      <el-form-item label="图片">
        <input type="file" accept="image/*" @change="onFileChange" />
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
        >
          <el-option
            v-for="tag in tagOptions"
            :key="tag"
            :label="tag"
            :value="tag"
          />
          <template #empty>
            <div style="padding: 8px 12px; text-align: center;">
              <span>无可选标签，请先</span>
              <el-button type="text" @click="createNewTag">新建</el-button>
            </div>
          </template>
        </el-select>
        <el-button style="margin-left: 8px;" @click="createNewTag">新建标签</el-button>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="onUpload" :loading="loading">上传</el-button>
      </el-form-item>
    </el-form>
    <div v-if="msg" :class="msgType">{{ msg }}</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessageBox, ElMessage } from 'element-plus' // 导入 ElMessageBox
import EXIF from 'exif-js'

const formRef = ref()
const form = ref({ file: null, description: '', tags: [] })
const tagOptions = ref([])
const tagLoading = ref(false)

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

// 新建标签功能
async function createNewTag() {
  try {
    const { value } = await ElMessageBox.prompt('请输入新的标签名', '新建标签', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputPattern: /\S/, // 不允许输入纯空格
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
      if (!form.value.tags.includes(value)) {
        form.value.tags.push(value);
      }
    }
  } catch (error) {
    if (error !== 'cancel') {
      const errorMsg = error.response?.data?.error || '创建失败';
      ElMessage.error(errorMsg);
    }
  }
}

const loading = ref(false)
const msg = ref('')
const msgType = ref('')

function onFileChange(e) {
  const file = e.target.files[0]
  if (!file) return;
  form.value.file = file

  // 使用EXIF.js读取图片信息
  EXIF.getData(file, async function() {
    const make = EXIF.getTag(this, "Make");
    const model = EXIF.getTag(this, "Model");
    const dateTime = EXIF.getTag(this, "DateTimeOriginal");

    const potentialTags = [make, model, dateTime].filter(tag => tag && typeof tag === 'string' && tag.trim());
    
    // 找出尚未成为用户标签的EXIF信息
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
        // 如果用户点击"是"
        for (const tag of newExifTags) {
          // 调用接口在后台创建该标签
          const token = localStorage.getItem('token');
          await axios.post('/api/user_tags/', { tag }, {
             headers: { Authorization: `Token ${token}` }
          });
          // 将其加入当前图片的待选标签中
          if (!form.value.tags.includes(tag)) {
            form.value.tags.push(tag);
          }
        }
        // 刷新标签库以包含新创建的标签
        await fetchUserTags();

      } catch (action) {
        // 如果用户点击"否"或关闭弹窗
        console.log('用户选择不添加EXIF标签。');
      }
    }
  });
}

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

    // 直接传递标签数组
    if (form.value.tags.length) {
      data.append('tags', JSON.stringify(form.value.tags))
    }
    
    const res = await axios.post('/api/upload_photo/', data, {
      headers: {
        'Content-Type': 'multipart/form-data',
        'Authorization': `Token ${token}`
      }
    })

    msg.value = res.data.msg || '上传成功'
    msgType.value = 'success'
    form.value.file = null
    form.value.description = ''
    form.value.tags = []
    if (formRef.value) formRef.value.resetFields()
  } catch (e) {
    // 输出详细错误信息，便于排查
    let detail = ''
    if (e.response && e.response.data) {
      if (typeof e.response.data === 'object') {
        detail = JSON.stringify(e.response.data)
      } else {
        detail = e.response.data
      }
    }
    msg.value = detail || e.message || '上传失败';
    msgType.value = 'error';
    // 控制台输出详细错误
    console.error('上传失败', e, detail);
    console.log([...data.entries()]);
  } finally {
    loading.value = false
  }
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
</style>