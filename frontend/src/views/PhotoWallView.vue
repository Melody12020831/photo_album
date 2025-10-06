<template>
  <div class="photo-wall">
    <h2>我的照片墙</h2>
    <el-row :gutter="16">
      <el-col v-for="photo in photos" :key="photo.id" :span="32" style="margin-bottom: 32px;">
        <el-card shadow="hover" style="min-height: 340px; min-width: 800px; padding-bottom: 16px;">
          <img :src="fixImageUrl(photo.image)" alt="photo" style="width: 100%; max-height: 200px; object-fit: cover;" />
          <div style="margin-top: 8px;">
            <span>{{ photo.description || '无描述' }}</span>
            <br />
            <small>{{ formatDate(photo.uploaded_at) }}</small>
          </div>
          <div style="margin-top: 8px; text-align: right; display: flex; gap: 8px; justify-content: flex-end;">
            <el-button type="primary" size="small" @click="showInfo(photo)">查看信息</el-button>
            <el-button type="success" size="small" @click="showThumb(photo)">查看缩略图</el-button>
            <el-button type="danger" size="small" @click="onDelete(photo.id)">删除</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-dialog v-model="thumbDialogVisible" title="缩略图预览" width="350px" :before-close="() => thumbDialogVisible = false">
      <div v-if="currentThumb">
        <img :src="fixImageUrl(currentThumb)" alt="thumb" style="max-width: 100%; max-height: 300px; display: block; margin: 0 auto;" />
      </div>
    </el-dialog>

    <el-dialog v-model="infoDialogVisible" title="图片信息" width="500px" :before-close="() => infoDialogVisible = false">
      <template #default>
        <div v-if="currentPhoto">
          <div v-if="currentPhoto.thumbnail">
            <img :src="fixImageUrl(currentPhoto.thumbnail)" alt="thumb" style="max-width: 100%; max-height: 120px; margin-bottom: 8px;" />
          </div>
          <ul style="padding-left: 0; list-style: none;">
            <li><b>描述：</b>{{ currentPhoto.description || '无' }}</li>
            <li><b>上传时间：</b>{{ formatDate(currentPhoto.uploaded_at) }}</li>
            <li><b>拍摄时间：</b>{{ (currentPhoto.tags && currentPhoto.tags.length) ? formatExifDate(currentPhoto.tags[0]) : (currentPhoto.taken_at ? formatTakenAt(currentPhoto.taken_at) : (currentPhoto.exif && currentPhoto.exif['EXIF DateTimeOriginal'] ? formatExifDate(currentPhoto.exif['EXIF DateTimeOriginal']) : '无')) }}</li>
            <li><b>地点：</b>{{ currentPhoto.location || '无' }}</li>
            <li><b>分辨率：</b>{{ currentPhoto.resolution || '无' }}</li>
            <li><b>标签：</b>
              <span v-if="currentPhoto.tags && currentPhoto.tags.length">{{ currentPhoto.tags.join(', ') }}</span>
              <span v-else>无</span>
            </li>
            <li><b>EXIF：</b>
              <el-popover placement="right" width="400" trigger="click">
                <template #reference>
                  <el-button size="small">查看全部EXIF</el-button>
                </template>
                <div style="max-height: 200px; overflow: auto;">
                  <ul style="padding-left: 0; list-style: none;">
                    <li v-for="(val, key) in currentPhoto.exif" :key="key"><b>{{ key }}:</b> {{ val }}</li>
                  </ul>
                </div>
              </el-popover>
            </li>
          </ul>
        </div>
      </template>
    </el-dialog>

    <el-empty v-if="photos.length === 0" description="暂无照片" />
  </div>
</template>

<script setup>
const thumbDialogVisible = ref(false)
const currentThumb = ref(null)

function showThumb(photo) {
  if (photo.thumbnail) {
    currentThumb.value = photo.thumbnail
    thumbDialogVisible.value = true
  } else {
    currentThumb.value = null
    thumbDialogVisible.value = false
    window.$message && window.$message.warning('该图片无缩略图')
  }
}
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { deletePhoto } from '../api/photo'

const photos = ref([])
const infoDialogVisible = ref(false)
const currentPhoto = ref(null)

function showInfo(photo) {
  currentPhoto.value = photo
  infoDialogVisible.value = true
}

function fixImageUrl(url) {
  if (!url) return '';
  // 只保留 /media/photos/xxx.png 及其后缀
  const idx = url.indexOf('/media/photos/');
  return idx !== -1 ? url.slice(idx) : url;
}


function formatDate(dateStr) {
  // 兼容 ISO 字符串
  if (!dateStr) return '';
  const d = new Date(dateStr);
  if (!isNaN(d)) return d.toLocaleString();
  return dateStr;
}

// 拍摄时间格式化，优先用 taken_at 字段，否则用 exif 的原始时间
function formatTakenAt(takenAt) {
  // takenAt 可能是 ISO 字符串
  if (!takenAt) return '';
  const d = new Date(takenAt);
  if (!isNaN(d)) {
    // yyyy/M/d HH:mm:ss
    const yyyy = d.getFullYear();
    const m = d.getMonth() + 1;
    const day = d.getDate();
    const hh = d.getHours().toString().padStart(2, '0');
    const mm = d.getMinutes().toString().padStart(2, '0');
    const ss = d.getSeconds().toString().padStart(2, '0');
    return `${yyyy}/${m}/${day} ${hh}:${mm}:${ss}`;
  }
  return takenAt;
}

function formatExifDate(exifDate) {
  // exifDate 形如 '2025:10:06 20:25:47'，转为 '2025/10/6 20:25:47'
  if (!exifDate) return '';
  const match = exifDate.match(/(\d{4}):(\d{1,2}):(\d{1,2}) (\d{2}:\d{2}:\d{2})/);
  if (match) {
    const [, y, m, d, t] = match;
    return `${y}/${parseInt(m)}/${parseInt(d)} ${t}`;
  }
  return exifDate;
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