<template>
  <div class="page-container" :class="{ 'dark': isDark }">
    <!-- 主题开关 -->
    <div class="top-bar">
      <el-switch
        v-model="isDark"
        inline-prompt
        :active-icon="Moon"
        :inactive-icon="Sunny"
        style="--el-switch-on-color: #4c4d4f; --el-switch-off-color: #d4b483"
        @change="toggleTheme"
      />
    </div>

    <div class="auth-card">
      <div class="card-header">
        <h2>创建账号</h2>
        <p>开启您的光影之旅</p>
      </div>
      
      <el-form :model="form" :rules="rules" ref="formRef" label-position="top" size="large" @submit.prevent="onSubmit">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="设置用户名" :prefix-icon="User" class="theme-input" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="example@mail.com" :prefix-icon="Message" class="theme-input" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="设置密码" :prefix-icon="Lock" show-password class="theme-input" />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="form.confirmPassword" type="password" placeholder="确认密码" :prefix-icon="Lock" class="theme-input" />
        </el-form-item>
        
        <el-button type="primary" class="submit-btn" :loading="isLoading" @click="onSubmit">立即注册</el-button>
      </el-form>
      
      <div class="card-footer">
        <span class="text-muted">已有账号？</span>
        <el-button link class="link-btn" @click="$router.push('/login')">去登录</el-button>
        <el-divider direction="vertical" />
        <el-button link class="link-btn" @click="$router.push('/')">返回主页</el-button>
      </div>

      <!-- 状态消息 -->
      <div v-if="success || error" class="status-msg" :class="{ 'error': error, 'success': success }">
        {{ error || success }}
      </div>
    </div>
    
    <!-- 背景装饰 -->
    <div class="bg-shape shape-1"></div>
    <div class="bg-shape shape-2"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { register } from '../api/user'
import { User, Lock, Message, Moon, Sunny } from '@element-plus/icons-vue'

const router = useRouter()
const formRef = ref()
const form = ref({ username: '', email: '', password: '', confirmPassword: '' })
const error = ref('')
const success = ref('')
const isLoading = ref(false)
const countdown = ref(3)
const isDark = ref(false)
let timer = null


// 组件挂载时初始化主题
onMounted(() => {
  initTheme()
})


// 组件卸载时清除定时器
onUnmounted(() => { if (timer) clearInterval(timer) })


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


// 校验确认密码是否一致
const validateConfirmPassword = (rule, value, callback) => {
  if (!value) callback(new Error('请再次输入密码'))
  else if (value !== form.value.password) callback(new Error('两次输入的密码不一致'))
  else callback()
}

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }, { min: 6, message: '至少6个字符', trigger: 'blur' }, { validator: (rule, value, callback) => { if (value && value.length < 6) { callback(new Error('用户名必须至少6个字符')); } else { callback(); } }, trigger: 'blur' } ],
  email: [{ required: true, message: '请输入邮箱', trigger: 'blur' }, { type: 'email', message: '格式不正确', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }, { min: 6, message: '至少6位', trigger: 'blur' }],
  confirmPassword: [{ required: true, validator: validateConfirmPassword, trigger: 'blur' }]
}


// 提交注册表单，注册新用户
const onSubmit = () => {
  formRef.value.validate(async valid => {
    if (valid) {
      isLoading.value = true
      try {
        await register({
          username: form.value.username,
          email: form.value.email,
          password: form.value.password
        })
        error.value = ''
        countdown.value = 3
        success.value = `注册成功，${countdown.value}秒后跳转登录...`
        timer && clearInterval(timer)
        timer = setInterval(() => {
          countdown.value--
          if (countdown.value > 0) {
            success.value = `注册成功，${countdown.value}秒后跳转登录...`
          } else {
            clearInterval(timer)
            router.push('/login')
          }
        }, 1000)
      } catch (e) {
        // 处理用户名重复等常见错误为中文
        let err = e.response?.data;
        if (err?.username && Array.isArray(err.username) && err.username.some(msg => msg.includes('already exists'))) {
          error.value = '该用户名已被注册，请更换用户名';
        } else if (err?.email && Array.isArray(err.email) && err.email.some(msg => msg.includes('already exists'))) {
          error.value = '该邮箱已被注册，请更换邮箱';
        } else if (err?.email && typeof err.email === 'string' && err.email.includes('already exists')) {
          error.value = '该邮箱已被注册，请更换邮箱';
        } else if (typeof err === 'string') {
          error.value = err;
        } else if (err?.detail) {
          error.value = err.detail;
        } else {
          error.value = '注册失败';
        }
        success.value = '';
      } finally {
        isLoading.value = false
      }
    }
  })
}
</script>

<style scoped>
/* 统一配色变量 */
.page-container {
  --bg-color: #fdfaf4;
  --text-color: #4a4a4a;
  --card-bg: rgba(255, 255, 255, 0.85);
  --accent-color: #8c7b75;
  --accent-hover: #7a6a65;
  --shape-1: #e8e0d5;
  --shape-2: #dcd0c0;
  
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--bg-color);
  position: relative;
  overflow: hidden;
  transition: all 0.3s;
}

.page-container.dark {
  --bg-color: #1a1a1a;
  --text-color: #e0e0e0;
  --card-bg: rgba(44, 44, 44, 0.85);
  --accent-color: #d4b483;
  --accent-hover: #c4a473;
  --shape-1: #2a2a2a;
  --shape-2: #333;
}

.top-bar {
  position: absolute;
  top: 20px;
  right: 20px;
  z-index: 20;
}

.auth-card {
  width: 100%;
  max-width: 420px;
  background: var(--card-bg);
  backdrop-filter: blur(10px);
  padding: 40px;
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.05);
  z-index: 10;
  border: 1px solid rgba(0,0,0,0.05);
}
.dark .auth-card {
  box-shadow: 0 10px 30px rgba(0,0,0,0.4);
  border: 1px solid rgba(255,255,255,0.05);
}

.card-header { text-align: center; margin-bottom: 30px; }
.card-header h2 { margin: 0 0 8px; font-size: 1.8rem; color: var(--text-color); font-family: "Caveat", cursive, sans-serif; }
.card-header p { color: var(--accent-color); margin: 0; font-size: 0.95rem; }

/* 表单覆盖 */
.theme-input :deep(.el-input__wrapper) {
  background-color: transparent;
  box-shadow: 0 0 0 1px #dcdfe6;
}
.dark .theme-input :deep(.el-input__wrapper) {
  box-shadow: 0 0 0 1px #555;
}
.theme-input :deep(.el-input__inner) { color: var(--text-color); }

.submit-btn {
  width: 100%;
  margin-top: 10px;
  background-color: var(--accent-color);
  border-color: var(--accent-color);
  font-weight: 600;
}
.submit-btn:hover {
  background-color: var(--accent-hover);
  border-color: var(--accent-hover);
}
.dark .submit-btn { color: #333; }

.card-footer { margin-top: 24px; text-align: center; font-size: 0.9rem; }
.text-muted { color: #909399; margin-right: 8px; }
.link-btn { color: var(--accent-color); }
.link-btn:hover { color: var(--accent-hover); }

.status-msg { margin-top: 16px; text-align: center; font-size: 0.9rem; padding: 8px; border-radius: 4px; }
.status-msg.error { background: #fef0f0; color: #f56c6c; }
.status-msg.success { background: #f0f9eb; color: #67c23a; }
.dark .status-msg.error { background: rgba(245, 108, 108, 0.2); }
.dark .status-msg.success { background: rgba(103, 194, 58, 0.2); }

.bg-shape {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  z-index: 1;
}
.shape-1 { width: 400px; height: 400px; background: var(--shape-1); top: -100px; left: -100px; }
.shape-2 { width: 300px; height: 300px; background: var(--shape-2); bottom: -50px; right: -50px; }
</style>