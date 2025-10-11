<template>
  <div class="photo-wall">
    <h2>我的照片墙</h2>
    <el-form :inline="true" style="margin-bottom: 24px;" @submit.prevent="onSearch">
      <el-form-item label="标签">
        <el-input v-model="searchTags" placeholder="多个标签用逗号分隔" style="width: 200px;" />
      </el-form-item>
      <el-form-item label="上传日期">
        <el-date-picker
          v-model="searchUploadDateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          style="width: 240px;"
        />
      </el-form-item>
      <el-form-item label="拍摄日期">
        <el-date-picker v-model="searchDate" type="date" placeholder="选择日期" style="width: 180px;" />
      </el-form-item>
      <el-form-item label="拍摄地点">
        <el-input v-model="searchLocation" placeholder="如: 北京" style="width: 180px;" />
      </el-form-item>
      <el-form-item label="分辨率">
        <el-select v-model="resolutionType" placeholder="选择类型" style="width: 120px;">
          <el-option label="精确尺寸" value="size" />
          <el-option label="宽高比" value="ratio" />
          <el-option label="总像素" value="megapixel" />
        </el-select>
        <template v-if="resolutionType === 'size'">
          <el-input v-model="searchResolution" placeholder="如: 4000x3000" style="width: 140px; margin-left: 8px;" />
        </template>
        <template v-else-if="resolutionType === 'ratio'">
          <el-select v-model="searchRatio" placeholder="选择宽高比" style="width: 120px; margin-left: 8px;">
            <el-option label="16:9" value="16:9" />
            <el-option label="4:3" value="4:3" />
            <el-option label="1:1" value="1:1" />
            <el-option label="3:2" value="3:2" />
            <el-option label="自定义" value="custom" />
          </el-select>
          <el-input v-if="searchRatio === 'custom'" v-model="searchRatioCustom" placeholder="自定义(如 5:4)" style="width: 100px; margin-left: 8px;" @input="onRatioCustomInput" />
        </template>
        <template v-else-if="resolutionType === 'megapixel'">
          <el-select v-model="searchMegapixel" placeholder="选择总像素" style="width: 120px; margin-left: 8px;">
            <el-option label=">5MP" value=">5" />
            <el-option label=">12MP" value=">12" />
            <el-option label=">24MP" value=">24" />
            <el-option label="自定义" value="custom" />
          </el-select>
          <el-input v-if="searchMegapixel === 'custom'" v-model="searchMegapixelCustom" placeholder="自定义(如 >8)" style="width: 100px; margin-left: 8px;" @input="onMegapixelCustomInput" />
        </template>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="onSearch">筛选</el-button>
        <el-button @click="onReset">重置</el-button>
      </el-form-item>
    </el-form>
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
const searchTags = ref('')
const searchUploadDateRange = ref(null)
const searchDate = ref(null)
const infoDialogVisible = ref(false)
const currentPhoto = ref(null)
const searchLocation = ref('')
const searchResolution = ref('')
const resolutionType = ref('size')
const searchRatio = ref('')
const searchRatioCustom = ref('')
const searchMegapixel = ref('')
const searchMegapixelCustom = ref('')
function onRatioCustomInput(val) {
  if (val) searchRatio.value = val
}

function onMegapixelCustomInput(val) {
  if (val) searchMegapixel.value = val
}

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

async function fetchPhotos(params = {}) {
  const token = localStorage.getItem('token')
  if (!token) return
  try {
    const query = Object.entries(params)
      .filter(([key, value]) => value) // 过滤掉值为空的参数
      .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
      .join('&');
      
    const url = `/api/photos/${query ? '?' + query : ''}`; // 动态构建 URL
    
    console.log('正在请求URL:', url); // 增加一个日志，方便调试

    const res = await axios.get(url, {
      headers: { Authorization: `Token ${token}` }
    })
    photos.value = res.data.photos || []
  } catch (e) {
    console.error('获取照片失败:', e); // 增加错误日志
    photos.value = []
  }
}

function formatDateParam(dateObj) {
  if (!dateObj) return '';
  // Element Plus 日期选择器返回 Date 对象
  const yyyy = dateObj.getFullYear();
  const mm = (dateObj.getMonth() + 1).toString().padStart(2, '0');
  const dd = dateObj.getDate().toString().padStart(2, '0');
  return `${yyyy}-${mm}-${dd}`;
}

function onSearch() {
  const params = {
    tags: searchTags.value,
    taken_date: searchDate.value ? formatDateParam(searchDate.value) : '',
    location: searchLocation.value
  }
  if (searchUploadDateRange.value && searchUploadDateRange.value.length === 2) {
    params.upload_date_start = formatDateParam(searchUploadDateRange.value[0]);
    params.upload_date_end = formatDateParam(searchUploadDateRange.value[1]);
  }
  if (resolutionType.value === 'size') {
    params.resolution = searchResolution.value
  } else if (resolutionType.value === 'ratio') {
    params.ratio = searchRatio.value === 'custom' ? searchRatioCustom.value : searchRatio.value
  } else if (resolutionType.value === 'megapixel') {
    params.megapixel = searchMegapixel.value === 'custom' ? searchMegapixelCustom.value : searchMegapixel.value
  }
  console.log('筛选参数:', params)
  fetchPhotos(params)
}

function onReset() {
  searchTags.value = ''
  searchUploadDateRange.value = null
  searchDate.value = null
  searchLocation.value = ''
  searchResolution.value = ''
  resolutionType.value = 'size'
  searchRatio.value = ''
  searchRatioCustom.value = ''
  searchMegapixel.value = ''
  searchMegapixelCustom.value = ''
  fetchPhotos()
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