<template>
  <div class="form-container">
    <h2>注册</h2>
    <el-form :model="form" :rules="rules" ref="formRef" label-width="80px" @submit.prevent="onSubmit">
      <el-form-item label="用户名" prop="username">
        <el-input v-model="form.username" placeholder="请输入用户名" />
      </el-form-item>
      <el-form-item label="邮箱" prop="email">
        <el-input v-model="form.email" placeholder="请输入邮箱" />
      </el-form-item>
      <el-form-item label="密码" prop="password">
        <el-input v-model="form.password" type="password" placeholder="请输入密码" />
      </el-form-item>
      <el-form-item label="确认密码" prop="confirmPassword">
        <el-input v-model="form.confirmPassword" type="password" placeholder="请再次输入密码" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" native-type="submit" @click="onSubmit">注册</el-button>
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
import { ref, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { register } from '../api/user'

const router = useRouter()
const formRef = ref()
const form = ref({ username: '', email: '', password: '', confirmPassword: '' })
const error = ref('')
const success = ref('')
const countdown = ref(3)
let timer = null
onUnmounted(() => {
  if (timer) clearInterval(timer)
})

const validateConfirmPassword = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请再次输入密码'))
  } else if (value !== form.value.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, message: '用户名至少2位', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

const onSubmit = () => {
  formRef.value.validate(async valid => {
    if (valid) {
      try {
        await register({
          username: form.value.username,
          email: form.value.email,
          password: form.value.password
        })
        error.value = ''
        countdown.value = 3
        success.value = `注册成功，${countdown.value}秒后跳转到登录页面...`
        timer && clearInterval(timer)
        timer = setInterval(() => {
          countdown.value--
          if (countdown.value > 0) {
            success.value = `注册成功，${countdown.value}秒后跳转到登录页面...`
          } else {
            clearInterval(timer)
            router.push('/login')
          }
        }, 1000)
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
        error.value = errMsg || '注册失败';
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
.error {
  color: #f56c6c;
  margin-top: 10px;
  white-space: pre-line;
}
</style>
