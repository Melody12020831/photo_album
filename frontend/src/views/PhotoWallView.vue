<template>
  <div class="photo-wall">
    <h2>我的照片墙</h2>
    <el-row :gutter="16">
      <el-col v-for="photo in photos" :key="photo.id" :span="6" style="margin-bottom: 24px;">
        <el-card shadow="hover">
          <img :src="fixImageUrl(photo.image)" alt="photo" style="width: 100%; max-height: 200px; object-fit: cover;" />
          <div style="margin-top: 8px;">
            <span>{{ photo.description || '无描述' }}</span>
            <br />
            <small>{{ formatDate(photo.uploaded_at) }}</small>
          </div>
          <div style="margin-top: 8px; text-align: right;">
            <el-button type="danger" size="small" @click="onDelete(photo.id)">删除</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
    <el-empty v-if="photos.length === 0" description="暂无照片" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { deletePhoto } from '../api/photo'

const photos = ref([])

function fixImageUrl(url) {
  if (!url) return '';
  // 只保留 /media/photos/xxx.png 及其后缀
  const idx = url.indexOf('/media/photos/');
  return idx !== -1 ? url.slice(idx) : url;
}

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleString()
}

async function fetchPhotos() {
  const token = localStorage.getItem('token')
  if (!token) return
  try {
    const res = await axios.get('/api/photos/', {
      headers: { Authorization: `Token ${token}` }
    })
    photos.value = res.data.photos || []
  } catch (e) {
    photos.value = []
  }
}

async function onDelete(photoId) {
  const token = localStorage.getItem('token')
  if (!token) return
  if (!window.confirm('确定要删除这张图片吗？')) return
  try {
    await deletePhoto(photoId, token)
    photos.value = photos.value.filter(p => p.id !== photoId)
  } catch (e) {
    window.alert('删除失败')
  }
}

onMounted(fetchPhotos)
</script>

<style scoped>
.photo-wall {
  max-width: 900px;
  margin: 0 auto;
  padding: 32px 0;
}
</style>
