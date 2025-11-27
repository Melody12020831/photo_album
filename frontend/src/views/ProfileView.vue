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

    <div class="profile-card" v-if="user">
      <div class="profile-header">
        <div class="avatar-circle">
          {{ user.username.charAt(0).toUpperCase() }}
        </div>
        <h2 class="username">{{ user.username }}</h2>
        <p class="email">{{ user.email }}</p>
      </div>

      <div class="profile-actions">
        <el-button class="action-btn primary-btn" @click="$router.push('/photos')">
          <el-icon class="btn-icon"><Picture /></el-icon>
          我的相册
        </el-button>
        
        <el-button class="action-btn logout-btn" @click="logout">
          <el-icon class="btn-icon"><SwitchButton /></el-icon>
          退出登录
        </el-button>
      </div>
    </div>
    
    <div v-else class="empty-state">
       <p>尚未登录</p>
       <el-button class="action-btn primary-btn" @click="goLogin">去登录</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Moon, Sunny, Picture, SwitchButton } from '@element-plus/icons-vue'

const router = useRouter()
const user = ref(null)
const isDark = ref(false)


// 组件挂载时初始化用户信息和主题
onMounted(() => {
  getUserInfo()
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


// 获取当前用户信息
function getUserInfo() {
  const username = sessionStorage.getItem('username')
  const email = sessionStorage.getItem('email')
  if (username && email) {
    user.value = { username, email }
  } else {
    user.value = null
  }
}


// 退出登录，清除用户信息
function logout() {
  sessionStorage.removeItem('token')
  sessionStorage.removeItem('username')
  sessionStorage.removeItem('email')
  user.value = null
  router.push('/login')
}


// 跳转到登录页
function goLogin() {
  router.push('/login')
}
</script>

<style scoped>
.page-container {
  --bg-color: #fdfaf4;
  --text-color: #4a4a4a;
  --card-bg: #ffffff;
  --accent-color: #8c7b75;
  --border-color: #ebeef5;
  --btn-text: #fff;
  
  min-height: 100vh;
  background-color: var(--bg-color);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
  color: var(--text-color);
}
.page-container.dark {
  --bg-color: #1a1a1a;
  --text-color: #e0e0e0;
  --card-bg: #2c2c2c;
  --accent-color: #d4b483;
  --border-color: #444;
  --btn-text: #333;
}

.top-bar { position: absolute; top: 20px; right: 20px; z-index: 20; }

.profile-card {
  width: 100%;
  max-width: 360px;
  background: var(--card-bg);
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0,0,0,0.04);
  padding: 40px 30px;
  text-align: center;
  border: 1px solid rgba(0,0,0,0.02);
}
.dark .profile-card {
  box-shadow: 0 8px 30px rgba(0,0,0,0.4);
  border: 1px solid rgba(255,255,255,0.05);
}

.avatar-circle {
  width: 88px;
  height: 88px;
  margin: 0 auto 20px;
  background: var(--accent-color);
  color: #fff;
  font-size: 2.5rem;
  font-weight: 600;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  font-family: serif;
}
.dark .avatar-circle { color: #2c2c2c; }

.username {
  font-size: 1.6rem;
  font-weight: 700;
  margin: 0 0 8px;
  color: var(--text-color);
}
.email {
  font-size: 0.95rem;
  color: var(--accent-color);
  margin: 0 0 40px;
  opacity: 0.8;
}

.profile-actions {
  display: flex;
  flex-direction: column;
  gap: 16px;
  width: 100%;
}

.action-btn {
  width: 100%;
  height: 44px;
  font-size: 1rem;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  margin: 0;
}
.btn-icon { margin-right: 8px; font-size: 1.1em; }

.primary-btn {
  background-color: var(--accent-color);
  border: 1px solid var(--accent-color);
  color: var(--btn-text);
}
.primary-btn:hover {
  filter: brightness(1.1);
  border-color: var(--accent-color);
  color: var(--btn-text);
}

.logout-btn {
  background-color: transparent;
  border: 1px solid #ffcccc;
  color: #e57373;
}
.logout-btn:hover {
  background-color: #fff5f5;
  border-color: #ffb3b3;
  color: #f56c6c;
}
.dark .logout-btn {
  border-color: rgba(229, 115, 115, 0.3);
  color: #ef9a9a;
}
.dark .logout-btn:hover {
  background-color: rgba(229, 115, 115, 0.1);
}

.empty-state p { margin-bottom: 20px; color: var(--text-color); }
</style>