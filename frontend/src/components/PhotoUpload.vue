<template>
  <div class="photo-upload">
    <el-form ref="formRef" :model="form" label-width="80px">
      <el-form-item label="图片">
        <input type="file" accept="image/*" @change="onFileChange" />
      </el-form-item>
      <el-form-item label="描述">
        <el-input v-model="form.description" placeholder="图片描述（可选）" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="onUpload" :loading="loading">上传</el-button>
      </el-form-item>
    </el-form>
    <div v-if="msg" :class="msgType">{{ msg }}</div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const formRef = ref()
const form = ref({ file: null, description: '' })
const loading = ref(false)
const msg = ref('')
const msgType = ref('')

function onFileChange(e) {
  const file = e.target.files[0]
  form.value.file = file
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