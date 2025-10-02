<template>
  <div class="form-container">
    <h2>找回账号</h2>
    <el-form :model="form" :rules="rules" ref="formRef" label-width="80px" @submit.prevent="onSubmit">
      <el-form-item label="邮箱" prop="email">
        <el-input v-model="form.email" placeholder="请输入注册邮箱" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" native-type="submit" @click="onSubmit">找回账号</el-button>
      </el-form-item>
    </el-form>
    <div v-if="error || msg" style="margin-top: 10px;">
      <span v-if="error" class="error">{{ error }}</span>
      <span v-else class="msg">{{ msg }}</span>
    </div>
    <el-button type="default" style="margin-top: 16px; width: 100%;" @click="$router.push('/')">返回主页</el-button>
  </div>

</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const formRef = ref()
const form = ref({ email: '' })
const msg = ref('')
const error = ref('')

const rules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }
  ]
}

const onSubmit = () => {
  formRef.value.validate(async valid => {
    if (valid) {
      msg.value = '';
      error.value = '';
      try {
        const res = await axios.post('/api/recover/', { email: form.value.email })
        msg.value = res.data.msg || '如果该邮箱已注册，找回信息已发送，请查收邮件。'
        error.value = ''
        console.log('成功信息:', msg.value)
      } catch (e) {
        // 控制台输出错误详情，便于调试
        console.log('找回账号错误:', e, e.response)
        if (e.response && e.response.data && e.response.data.detail) {
          error.value = e.response.data.detail
        } else if (e.response && e.response.data && typeof e.response.data === 'string') {
          error.value = e.response.data
        } else if (e.message) {
          error.value = e.message
        } else {
          error.value = '找回失败'
        }
        msg.value = ''
        console.log('错误信息:', error.value)
      }
    } else {
      error.value = '请填写正确的邮箱';
      msg.value = '';
    }
  })
}
</script>

<style scoped>
.form-container {
  max-width: 400px;
  margin: 40px auto;
  padding: 24px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
@media (max-width: 600px) {
  .form-container {
    margin: 0 8px;
    padding: 16px;
    max-width: 100vw;
  }
}
.error {
  color: red;
  margin-top: 10px;
}
.msg {
  color: #409eff;
  margin-top: 10px;
}
</style>
