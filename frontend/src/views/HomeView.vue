<template>
  <div class="home-container" :class="{ 'dark': isDark }">
    <div class="top-bar">
      <div class="theme-switch-wrapper">
        <el-switch
          v-model="isDark"
          inline-prompt
          :active-icon="Moon"
          :inactive-icon="Sunny"
          style="--el-switch-on-color: #4c4d4f; --el-switch-off-color: #d4b483"
          @change="toggleTheme"
        />
      </div>
    </div>

    <div class="hero-content">
      <h1 class="title">光影 · 拾遗</h1>
      <p class="subtitle">翻开这本速写册，记录生活的每一笔光影。</p>
      
      <div class="nav-row">
        <template v-if="!isLoggedIn">
          <div class="nav-card" @click="$router.push('/login')">
            <el-icon class="icon"><User /></el-icon>
            <h3>登录</h3>
            <p>进入空间</p>
          </div>
          <div class="nav-card highlight" @click="$router.push('/register')">
            <el-icon class="icon"><Edit /></el-icon>
            <h3>注册</h3>
            <p>开启旅程</p>
          </div>
        </template>

        <div class="nav-card" @click="$router.push('/photos')">
          <el-icon class="icon"><Picture /></el-icon>
          <h3>照片墙</h3>
          <p>浏览作品</p>
        </div>
        
        <template v-if="isLoggedIn">
          <div class="nav-card" @click="$router.push('/upload')">
            <el-icon class="icon"><UploadFilled /></el-icon>
            <h3>上传</h3>
            <p>添加回忆</p>
          </div>
          <div class="nav-card" @click="goProfile">
            <el-icon class="icon"><Avatar /></el-icon>
            <h3>我的</h3>
            <p>个人中心</p>
          </div>
        </template>
      </div>
    </div>
    
    <div class="bg-shape shape-1"></div>
    <div class="bg-shape shape-2"></div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { User, Edit, Picture, UploadFilled, Avatar, Moon, Sunny } from '@element-plus/icons-vue'

const router = useRouter()
const isLoggedIn = ref(false)
const isDark = ref(false)


// 组件挂载时初始化登录状态和主题
onMounted(() => {
  isLoggedIn.value = !!sessionStorage.getItem('token')
  initTheme()
})


// 初始化主题（深色/浅色）
function initTheme() {
  const storedTheme = localStorage.getItem('theme')
  if (storedTheme) {
    isDark.value = storedTheme === 'dark'
  } else {
    const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    isDark.value = systemDark
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


// 跳转到个人中心或登录页
function goProfile() {
  if (isLoggedIn.value) {
    router.push('/profile')
  } else {
    router.push('/login')
  }
}


// 监听系统主题变化，自动切换主题（若未手动设置）
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
  if (!localStorage.getItem('theme')) {
    isDark.value = e.matches
    applyTheme(e.matches)
  }
})
</script>

<style scoped>
.home-container {
  --bg-color: #fdfaf4;
  --text-color: #4a4a4a;
  --card-bg: rgba(255, 255, 255, 0.6);
  --card-border: rgba(0, 0, 0, 0.05);
  --card-hover-shadow: rgba(0, 0, 0, 0.1);
  --accent-color: #8c7b75;
  --highlight-bg: linear-gradient(135deg, #d4b483 0%, #8c7b75 100%);
  --highlight-text: #fff;
  --shape-color-1: #e8e0d5;
  --shape-color-2: #dcd0c0;
  
  /* [新] 使用 fixed + inset-0 强制占满视口，无滚动条 */
  position: fixed; 
  inset: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--bg-color);
  color: var(--text-color);
  transition: background-color 0.3s ease, color 0.3s ease;
}

.home-container.dark {
  --bg-color: #1a1a1a;
  --text-color: #e0e0e0;
  --card-bg: rgba(40, 40, 40, 0.6);
  --card-border: rgba(255, 255, 255, 0.05);
  --card-hover-shadow: rgba(0, 0, 0, 0.5);
  --accent-color: #d4b483;
  --highlight-bg: linear-gradient(135deg, #4c4d4f 0%, #2c3e50 100%);
  --shape-color-1: #2a2a2a;
  --shape-color-2: #333333;
}

.top-bar {
  position: absolute;
  top: 20px;
  right: 20px;
  z-index: 20;
}

.hero-content {
  z-index: 10;
  text-align: center;
  width: 100%;
  max-width: 1200px;
  padding: 0 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.title {
  font-size: 3.5rem;
  font-weight: 800;
  margin-bottom: 12px;
  color: var(--text-color);
  letter-spacing: 2px;
  font-family: "Caveat", cursive, sans-serif;
}

.subtitle {
  font-size: 1.1rem;
  color: var(--text-color);
  opacity: 0.8;
  margin-bottom: 50px;
  font-weight: 400;
}

.nav-row {
  display: flex;
  flex-direction: row;
  gap: 24px;
  justify-content: center;
  flex-wrap: wrap;
  width: 100%;
}

.nav-card {
  background: var(--card-bg);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 24px 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.02);
  border: 1px solid var(--card-border);
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 140px;
  height: 140px;
  justify-content: center;
}

.nav-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 32px var(--card-hover-shadow);
  border-color: var(--accent-color);
}

.nav-card .icon {
  font-size: 36px;
  color: var(--accent-color);
  margin-bottom: 12px;
  transition: transform 0.3s ease;
}

.nav-card:hover .icon {
  transform: scale(1.1);
}

.nav-card h3 {
  margin: 0 0 4px 0;
  font-size: 1.1rem;
  color: var(--text-color);
}

.nav-card p {
  margin: 0;
  font-size: 0.8rem;
  color: var(--text-color);
  opacity: 0.6;
}

.nav-card.highlight {
  background: var(--highlight-bg);
  border: none;
}
.nav-card.highlight h3,
.nav-card.highlight p,
.nav-card.highlight .icon {
  color: var(--highlight-text);
}

.bg-shape {
  position: absolute;
  border-radius: 40% 60% 70% 30% / 40% 50% 60% 50%;
  filter: blur(80px);
  opacity: 0.6;
  z-index: 1;
}
.shape-1 { width: 50vh; height: 50vh; background: var(--shape-color-1); top: -10vh; left: -10vw; }
.shape-2 { width: 40vh; height: 40vh; background: var(--shape-color-2); bottom: -10vh; right: -5vw; }
</style>