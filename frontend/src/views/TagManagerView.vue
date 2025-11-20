<template>
  <div class="tag-manager">
    <h2>标签管理</h2>
    <el-form @submit.prevent="onCreateTag" :inline="true" style="margin-bottom: 16px;">
      <el-form-item label="新建标签">
        <el-input v-model="newTag" placeholder="输入新标签名" style="width: 200px;" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="onCreateTag">新建</el-button>
      </el-form-item>
    </el-form>
    <el-table :data="tags" style="width: 100%">
      <el-table-column prop="tag" label="标签名" />
      <el-table-column label="操作">
        <template #default="scope">
          <el-input v-model="scope.row.editName" placeholder="修改标签名" style="width: 120px; margin-right: 8px;" />
          <el-button type="success" size="small" @click="onUpdateTag(scope.row)">修改</el-button>
          <el-button type="danger" size="small" @click="onDeleteTag(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const tags = ref([])
const newTag = ref('')

async function fetchTags() {
  const token = sessionStorage.getItem('token')
  if (!token) return
  const res = await axios.get('/api/user_tags/', {
    headers: { Authorization: `Token ${token}` }
  })
  tags.value = (res.data.tags || []).map(tag => ({ tag, editName: tag }))
}

async function onCreateTag() {
  const tagName = newTag.value.trim()
  if (!tagName) return
  const token = sessionStorage.getItem('token')
  await axios.post('/api/user_tags/', { tag: tagName }, {
    headers: { Authorization: `Token ${token}` }
  })
  newTag.value = ''
  fetchTags()
}

async function onUpdateTag(row) {
  const token = sessionStorage.getItem('token')
  await axios.put('/api/user_tags/', { old_tag: row.tag, new_tag: row.editName }, {
    headers: { Authorization: `Token ${token}` }
  })
  fetchTags()
}

async function onDeleteTag(row) {
  const token = sessionStorage.getItem('token')
  await axios.delete('/api/user_tags/', {
    headers: { Authorization: `Token ${token}` },
    data: { tag: row.tag }
  })
  fetchTags()
}

onMounted(fetchTags)
</script>

<style scoped>
.tag-manager {
  max-width: 600px;
  margin: 32px auto;
  background: #fff;
  padding: 32px;
  border-radius: 8px;
  box-shadow: 0 12px 40px rgba(0,0,0,0.35); /* stronger shadow for contrast on dark background */
}

.tag-manager h2 {
  color: #222; /* darker title for readability */
  font-size: 1.6rem;
  font-weight: 700;
  margin: 0 0 16px 0;
}

/* Increase contrast for Element Plus labels/inputs inside this panel */
.tag-manager :deep(.el-form-item__label) {
  color: #444;
  font-size: 0.95rem;
}
.tag-manager :deep(.el-input__inner) {
  font-size: 0.95rem;
}
.tag-manager :deep(.el-table) {
  font-size: 0.95rem;
}

.tag-manager .el-button {
  min-width: 64px;
}
</style>
