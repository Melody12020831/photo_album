<template>
  <div class="form-container">
    <h2>登录</h2>
    <el-form :model="form" :rules="rules" ref="formRef" label-width="80px" @submit.prevent="onSubmit">
      <el-form-item label="用户名" prop="username">
        <el-input v-model="form.username" placeholder="请输入用户名" />
      </el-form-item>
      <el-form-item label="密码" prop="password">
        <el-input v-model="form.password" type="password" placeholder="请输入密码" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" native-type="submit" @click="onSubmit">登录</el-button>
      </el-form-item>
    </el-form>
    <div v-if="success || error" style="margin-top: 10px;">
      <span v-if="success" class="msg">{{ success }}</span>
      <span v-if="error" class="error">{{ error }}</span>
    </div>
    <el-button type="default" style="margin-top: 16px; width: 100%;" @click="$router.push('/')">返回主页</el-button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { login } from '../api/user'

const router = useRouter()
const formRef = ref()
const form = ref({ username: '', password: '' })
const error = ref('')
const success = ref('')

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' }
  ]
}

const onSubmit = () => {
  formRef.value.validate(async valid => {
    if (valid) {
      try {
        const res = await login(form.value)
        localStorage.setItem('token', res.data.token)
        error.value = ''
        success.value = '登录成功，正在跳转...'
        setTimeout(() => {
          router.push('/')
        }, 1200)
      } catch (e) {
        let errMsg = '';
        if (e.response && e.response.data) {
          const data = e.response.data;
          if (typeof data === 'string') {
            errMsg = data;
          } else if (typeof data === 'object') {
            errMsg = Object.values(data).map(arr => Array.isArray(arr) ? arr.join('; ') : arr).join('; ');
          }
        }
        error.value = errMsg || '登录失败';
        success.value = '';
      }
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
