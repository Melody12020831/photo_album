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
        <h2>欢迎回来</h2>
        <p>登录以访问您的光影集</p>
      </div>
      
      <el-form :model="form" :rules="rules" ref="formRef" size="large" @submit.prevent="onSubmit" class="auth-form">
        <el-form-item prop="username">
          <el-input 
            v-model="form.username" 
            placeholder="用户名" 
            :prefix-icon="User" 
            class="sketch-input" 
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input 
            v-model="form.password" 
            type="password" 
            placeholder="密码" 
            :prefix-icon="Lock" 
            show-password 
            class="sketch-input"
          />
        </el-form-item>
        
        <el-button type="primary" class="submit-btn" :loading="isLoading" @click="onSubmit">
          登 录
        </el-button>
      </el-form>
      
      <div class="card-footer">
        <el-button link class="link-btn" @click="$router.push('/register')">注册新账号</el-button>
        <span class="divider">|</span>
        <el-button link class="link-btn" @click="$router.push('/recover')">忘记密码</el-button>
      </div>
      
      <!-- 首页入口 -->
      <div class="home-link">
        <el-button link class="back-btn" @click="$router.push('/')">
          <el-icon><Back /></el-icon> 返回首页
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { login } from '../api/user'
import { User, Lock, Moon, Sunny, Back } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const formRef = ref()
const form = ref({ username: '', password: '' })
const isLoading = ref(false)
const isDark = ref(false)

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
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


// 提交登录表单，进行用户登录
const onSubmit = () => {
  formRef.value.validate(async valid => {
    if (valid) {
      isLoading.value = true
      try {
        const res = await login(form.value)
        const data = res.data || res
        sessionStorage.setItem('token', data.token)
        if (data.username) sessionStorage.setItem('username', data.username)
        if (data.email) sessionStorage.setItem('email', data.email)
        
        ElMessage.success('登录成功')
        setTimeout(() => router.push('/profile'), 500)
      } catch (e) {
        ElMessage.error(e.response?.data?.detail || '登录失败，请检查账号密码')
      } finally {
        isLoading.value = false
      }
    }
  })
}
</script>

<style scoped>
.page-container {
  --bg-color: #fdfaf4;
  --text-color: #4a4a4a;
  --card-bg: #ffffff;
  --accent-color: #8c7b75;
  --border-color: #ebeef5;
  --input-bg: #f9f9f9;
  --btn-text: #fff;
  
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--bg-color);
  transition: all 0.3s;
  color: var(--text-color);
  position: relative;
}
.page-container.dark {
  --bg-color: #1a1a1a;
  --text-color: #e0e0e0;
  --card-bg: #2c2c2c;
  --accent-color: #d4b483;
  --border-color: #444;
  --input-bg: #333;
  --btn-text: #333;
}

.top-bar { position: absolute; top: 20px; right: 20px; z-index: 20; }

.auth-card {
  width: 100%;
  max-width: 380px;
  background: var(--card-bg);
  padding: 40px 30px;
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0,0,0,0.05);
  border: 1px solid rgba(0,0,0,0.02);
}
.dark .auth-card {
  box-shadow: 0 8px 30px rgba(0,0,0,0.4);
  border: 1px solid rgba(255,255,255,0.05);
}

.card-header { text-align: center; margin-bottom: 32px; }
.card-header h2 { margin: 0 0 8px; font-size: 1.8rem; color: var(--text-color); font-weight: 600; }
.card-header p { margin: 0; color: var(--accent-color); font-size: 0.95rem; }

.auth-form .el-form-item { margin-bottom: 20px; }

/* 输入框风格 */
.sketch-input :deep(.el-input__wrapper) {
  background-color: var(--input-bg);
  box-shadow: none;
  border: 1px solid transparent;
  border-radius: 8px;
  padding: 4px 12px;
  transition: all 0.2s;
}
.sketch-input :deep(.el-input__wrapper.is-focus) {
  border-color: var(--accent-color);
  background-color: var(--card-bg);
}
.sketch-input :deep(.el-input__inner) { color: var(--text-color); }

.submit-btn {
  width: 100%;
  height: 44px;
  font-size: 1rem;
  background-color: var(--accent-color);
  border-color: var(--accent-color);
  color: var(--btn-text);
  border-radius: 8px;
  font-weight: 600;
  margin-top: 8px;
}
.submit-btn:hover {
  filter: brightness(1.1);
  border-color: var(--accent-color);
  background-color: var(--accent-color);
}

.card-footer {
  margin-top: 20px;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 0.9rem;
}
.divider { margin: 0 12px; color: #ccc; font-size: 0.8rem; }
.link-btn { color: #909399; font-weight: normal; }
.link-btn:hover { color: var(--accent-color); }

.home-link {
  margin-top: 30px;
  text-align: center;
  border-top: 1px dashed var(--border-color);
  padding-top: 16px;
}
.back-btn { color: var(--text-color); opacity: 0.6; }
.back-btn:hover { opacity: 1; color: var(--accent-color); }
</style>