<script setup>
import { RouterLink, RouterView, useRouter } from 'vue-router'
import { ref, onMounted } from 'vue'

const router = useRouter()
const token = ref(sessionStorage.getItem('token'))
const username = ref(sessionStorage.getItem('username'))

const updateAuthStatus = () => {
  token.value = sessionStorage.getItem('token')
  username.value = sessionStorage.getItem('username')
}

const logout = () => {
  sessionStorage.removeItem('token')
  sessionStorage.removeItem('username')
  updateAuthStatus()
  router.push('/login')
}

onMounted(() => {
  updateAuthStatus()
  window.addEventListener('storage', updateAuthStatus)
  // Custom event to handle login/logout from other components
  window.addEventListener('auth-change', updateAuthStatus)
})
</script>

<template>
  <div id="app-layout">
    <header class="main-header">
      <div class="header-content">
        <div class="logo-container">
          <img alt="Vue logo" class="logo" src="@/assets/logo.jpg" width="40" height="40" />
          <span class="site-title">Photo Album</span>
        </div>
        <nav>
          <RouterLink to="/">Home</RouterLink>
          <RouterLink to="/photos">照片墙</RouterLink>
          <template v-if="!token">
            <RouterLink to="/login">登录</RouterLink>
            <RouterLink to="/register">注册</RouterLink>
          </template>
          <template v-else>
            <RouterLink to="/profile">个人中心 ({{ username }})</RouterLink>
            <a href="#" @click.prevent="logout">退出登录</a>
          </template>
        </nav>
      </div>
    </header>
    <main class="main-content">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
#app-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: var(--color-background);
}

.main-header {
  background-color: var(--color-background-soft);
  border-bottom: 1px solid var(--color-border);
  padding: 0 2rem;
  height: 60px;
  display: flex;
  align-items: center;
  position: sticky;
  top: 0;
  z-index: 1000;
  width: 100%;
}

.header-content {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.logo {
  display: block;
}

.site-title {
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--color-heading);
}

nav {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  font-size: 1rem;
}

nav a {
  color: var(--color-text);
  text-decoration: none;
  transition: color 0.3s;
}

nav a:hover,
nav a.router-link-exact-active {
  color: var(--color-tint);
}

.main-content {
  flex-grow: 1;
  width: 100%;
}
</style>
