
<template>
  <main style="display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 60vh;">
    <h1 style="margin-bottom: 32px;">欢迎来到照片相册系统！</h1>
    <div style="margin-top: 40px; display: flex; gap: 16px; justify-content: center; flex-wrap: wrap;">
      <el-button type="primary" @click="$router.push('/register')">注册</el-button>
      <el-button type="success" @click="$router.push('/login')">登录</el-button>
      <el-button type="info" @click="$router.push('/recover')">找回账号</el-button>
      <el-button type="warning" @click="$router.push('/upload')">上传图片</el-button>
      <el-button type="default" @click="goProfile">个人中心</el-button>
      <el-button type="primary" @click="$router.push('/photos')">我的照片墙</el-button>
    </div>
  </main>
</template>

<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()
function goProfile() {
  const token = localStorage.getItem('token')
  if (token) {
    router.push('/profile')
  } else {
    router.push('/login')
  }
}
</script>
