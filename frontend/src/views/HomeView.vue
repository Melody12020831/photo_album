<script setup>
import TheWelcome from '../components/TheWelcome.vue'
import { ref } from 'vue';
import axios from 'axios';

const message = ref('点击按钮');

const fetchData = async () => {
  try {
    // Vite 代理会自动将这个请求转发到 http://backend:8000/api/test/
    const response = await axios.get('/api/test/');
    message.value = response.data.message;
  } catch (error) {
    console.error('获取数据失败:', error);
    message.value = '获取数据失败!';
  }
};
</script>

<template>
  <main>
    <TheWelcome />
    <h1>{{ message }}</h1>
    <el-button type="primary" @click="fetchData">从后端获取数据</el-button>
  </main>
</template>
