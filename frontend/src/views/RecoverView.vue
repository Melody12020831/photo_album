<template>
  <div class="page-container" :class="{ 'dark': isDark }">
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
        <h2>账号找回</h2>
        <p>找回您的速写本通行证</p>
      </div>
      
      <el-form :model="form" :rules="rules" ref="formRef" label-position="top" size="large" @submit.prevent="onSubmit">
        <el-form-item label="注册邮箱" prop="email">
          <el-input v-model="form.email" placeholder="请输入您的邮箱" :prefix-icon="Message" class="theme-input" />
        </el-form-item>
        
        <el-button type="primary" class="submit-btn" :loading="isLoading" @click="onSubmit">发送找回邮件</el-button>
      </el-form>
      
      <div class="card-footer">
        <el-button link class="link-btn" @click="$router.push('/login')">返回登录</el-button>
        <el-divider direction="vertical" />
        <el-button link class="link-btn" @click="$router.push('/')">回到首页</el-button>
      </div>

      <div v-if="success || error" class="status-msg" :class="{ 'error': error, 'success': success }">
        {{ error || success }}
      </div>
    </div>
    
    <div class="bg-shape shape-1"></div>
    <div class="bg-shape shape-2"></div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { Message, Moon, Sunny } from '@element-plus/icons-vue'

const formRef = ref()
const form = ref({ email: '' })
const msg = ref('')
const error = ref('')
const success = ref('')
const isLoading = ref(false)
const isDark = ref(false)

const rules = {
  email: [{ required: true, message: '请输入邮箱', trigger: 'blur' }, { type: 'email', message: '格式不正确', trigger: 'blur' }]
}


// 组件挂载时初始化主题
onMounted(() => {
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


// 提交找回账号表单，发送找回邮件
const onSubmit = () => {
  formRef.value.validate(async valid => {
    if (valid) {
      isLoading.value = true
      success.value = '';
      error.value = '';
      try {
        const res = await axios.post('/api/recover/', { email: form.value.email })
        success.value = res.data.msg || '如果该邮箱已注册，找回信息已发送，请查收邮件。'
      } catch (e) {
        error.value = e.response?.data?.detail || e.message || '找回失败'
      } finally {
        isLoading.value = false
      }
    }
  })
}
</script>

<style scoped>
/* 复用统一配色 */
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

.top-bar { position: absolute; top: 20px; right: 20px; z-index: 20; }

.auth-card {
  width: 100%;
  max-width: 400px;
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

.theme-input :deep(.el-input__wrapper) { background-color: transparent; box-shadow: 0 0 0 1px #dcdfe6; }
.dark .theme-input :deep(.el-input__wrapper) { box-shadow: 0 0 0 1px #555; }
.theme-input :deep(.el-input__inner) { color: var(--text-color); }

.submit-btn {
  width: 100%;
  background-color: var(--accent-color);
  border-color: var(--accent-color);
  font-weight: 600;
}
.submit-btn:hover { background-color: var(--accent-hover); border-color: var(--accent-hover); }
.dark .submit-btn { color: #333; }

.card-footer { margin-top: 24px; text-align: center; font-size: 0.9rem; }
.link-btn { color: var(--accent-color); }
.link-btn:hover { color: var(--accent-hover); }

.status-msg { margin-top: 16px; text-align: center; font-size: 0.9rem; padding: 8px; border-radius: 4px; }
.status-msg.error { background: #fef0f0; color: #f56c6c; }
.status-msg.success { background: #f0f9eb; color: #67c23a; }
.dark .status-msg.error { background: rgba(245, 108, 108, 0.2); }
.dark .status-msg.success { background: rgba(103, 194, 58, 0.2); }

.bg-shape { position: absolute; border-radius: 50%; filter: blur(80px); z-index: 1; }
.shape-1 { width: 400px; height: 400px; background: var(--shape-1); top: -100px; left: -100px; }
.shape-2 { width: 300px; height: 300px; background: var(--shape-2); bottom: -50px; right: -50px; }
</style>