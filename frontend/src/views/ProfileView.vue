<template>
  <div class="profile-container">
    <h2>个人中心</h2>
    <div v-if="user">
      <el-descriptions title="用户信息" :column="1" border>
        <el-descriptions-item label="用户名">{{ user.username }}</el-descriptions-item>
        <el-descriptions-item label="邮箱">{{ user.email }}</el-descriptions-item>
      </el-descriptions>
      <el-button type="danger" style="margin-top: 24px;" @click="logout">退出登录</el-button>
    </div>
    <div v-else>
      <el-alert title="未登录，请先登录。" type="warning" show-icon />
      <el-button type="primary" style="margin-top: 16px;" @click="goLogin">去登录</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const user = ref(null)

function getUserInfo() {
  // 从 sessionStorage 获取用户信息（关闭网页后自动退出登录）
  const username = sessionStorage.getItem('username')
  const email = sessionStorage.getItem('email')
  if (username && email) {
    user.value = { username, email }
  } else {
    user.value = null
  }
}

function logout() {
  sessionStorage.removeItem('token')
  sessionStorage.removeItem('username')
  sessionStorage.removeItem('email')
  user.value = null
  router.push('/login')
}

function goLogin() {
  router.push('/login')
}

onMounted(() => {
  getUserInfo()
})
</script>

<style scoped>
.profile-container {
  max-width: 400px;
  margin: 40px auto;
  padding: 24px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
</style>
