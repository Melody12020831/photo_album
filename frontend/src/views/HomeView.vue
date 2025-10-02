
<template>
  <main style="display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 60vh;">
    <h1 style="margin-bottom: 32px;">欢迎来到照片相册系统！</h1>
    <div style="margin-top: 40px; display: flex; gap: 16px; justify-content: center;">
      <el-button type="primary" @click="$router.push('/register')">注册</el-button>
      <el-button type="success" @click="$router.push('/login')">登录</el-button>
      <el-button type="info" @click="$router.push('/recover')">找回账号</el-button>
    </div>
  </main>
</template>
