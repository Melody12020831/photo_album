<template>
  <div class="page-container">
    <div class="top-bar">
      <el-switch
        v-model="isDark"
        inline-prompt
        :active-icon="Moon"
        :inactive-icon="Sunny"
        style="--el-switch-on-color: #4c4d4f; --el-switch-off-color: #d4b483"
        @change="toggleTheme"
      />
    </div>

    <div class="content-card">
      <div class="card-header">
        <div class="header-left">
          <h2>标签管理</h2>
          <p>管理您的分类关键词</p>
        </div>
        <div class="header-right">
          <div class="input-wrapper">
             <el-input 
               v-model="newTag" 
               placeholder="新建标签..." 
               class="sketch-input"
               @keyup.enter="onCreateTag"
             >
               <template #append>
                 <el-button @click="onCreateTag" class="sketch-btn-append">
                   <el-icon><Plus /></el-icon>
                 </el-button>
               </template>
             </el-input>
          </div>
        </div>
      </div>

      <el-table 
        :data="tags" 
        style="width: 100%" 
        class="sketch-table"
        :row-style="{ background: 'transparent' }"
        :header-cell-style="{ background: 'transparent', color: 'var(--accent-color)', fontWeight: 'normal' }"
      >
        <el-table-column label="预览" width="180">
          <template #default="scope">
            <!-- 统一的标签样式 -->
            <span class="sketch-tag">
              {{ scope.row.tag }}
            </span>
          </template>
        </el-table-column>
        
        <el-table-column prop="tag" label="名称" />
        
        <el-table-column label="操作" align="right">
          <template #default="scope">
            <div class="action-row">
              <el-input 
                v-model="scope.row.editName" 
                size="small" 
                placeholder="重命名" 
                class="edit-input"
              />
              <el-button link class="icon-btn success" @click="onUpdateTag(scope.row)">
                <el-icon><Check /></el-icon>
              </el-button>
              <el-popconfirm title="确定删除该标签吗？" @confirm="onDeleteTag(scope.row)">
                <template #reference>
                  <el-button link class="icon-btn danger">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </template>
              </el-popconfirm>
            </div>
          </template>
        </el-table-column>
      </el-table>
      
      <el-empty v-if="tags.length === 0" description="暂无标签，创建第一个吧！" :image-size="100" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { Plus, Check, Delete, Moon, Sunny } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const tags = ref([])
const newTag = ref('')
const isDark = ref(false)

// 页面挂载时初始化，获取标签并设置主题
onMounted(() => {
  fetchTags()
  const storedTheme = localStorage.getItem('theme')
  if (storedTheme) {
    isDark.value = storedTheme === 'dark'
  } else {
    isDark.value = window.matchMedia('(prefers-color-scheme: dark)').matches
  }
  applyTheme(isDark.value)
})

// 切换明暗主题
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

// 获取当前用户的所有标签
async function fetchTags() {
  const token = sessionStorage.getItem('token')
  if (!token) return
  try {
    const res = await axios.get('/api/user_tags/', {
      headers: { Authorization: `Token ${token}` }
    })
    tags.value = (res.data.tags || []).map(tag => ({ tag, editName: tag }))
  } catch(e){}
}

// 创建新标签
async function onCreateTag() {
  const val = newTag.value.trim()
  if (!val) return
  const token = sessionStorage.getItem('token')
  try {
    await axios.post('/api/user_tags/', { tag: val }, { headers: { Authorization: `Token ${token}` } })
    newTag.value = ''
    fetchTags()
    ElMessage.success('已创建')
  } catch(e){ ElMessage.error('创建失败') }
}

// 更新（重命名）标签
async function onUpdateTag(row) {
  const token = sessionStorage.getItem('token')
  try {
    await axios.put('/api/user_tags/', { old_tag: row.tag, new_tag: row.editName }, {
      headers: { Authorization: `Token ${token}` }
    })
    fetchTags()
    ElMessage.success('已更新')
  } catch(e){ ElMessage.error('更新失败') }
}

// 删除标签
async function onDeleteTag(row) {
  const token = sessionStorage.getItem('token')
  try {
    await axios.delete('/api/user_tags/', {
      headers: { Authorization: `Token ${token}` },
      data: { tag: row.tag }
    })
    fetchTags()
    ElMessage.success('已删除')
  } catch(e){ ElMessage.error('删除失败') }
}
</script>

<style scoped>
.page-container {
  --bg-color: #fdfaf4;
  --text-color: #4a4a4a;
  --card-bg: #ffffff;
  --accent-color: #8c7b75;
  --border-color: #ebeef5;
  --tag-bg: #f2efe9;
  --tag-text: #5e524e;
  
  min-height: 100vh;
  background-color: var(--bg-color);
  padding: 40px 20px;
  display: flex;
  justify-content: center;
  transition: all 0.3s;
  color: var(--text-color);
}
:global(.dark) .page-container {
  --bg-color: #1a1a1a;
  --text-color: #e0e0e0;
  --card-bg: #2c2c2c;
  --accent-color: #d4b483;
  --border-color: #444;
  --tag-bg: #3a3a3a;
  --tag-text: #ccc;
}

.top-bar { position: absolute; top: 20px; right: 20px; z-index: 20; }

.content-card {
  width: 100%;
  max-width: 700px;
  background: var(--card-bg);
  border-radius: 12px;
  padding: 32px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.03);
  border: 1px solid rgba(0,0,0,0.03);
}
:global(.dark) .content-card {
  box-shadow: 0 4px 24px rgba(0,0,0,0.3);
  border: 1px solid rgba(255,255,255,0.05);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 2px dashed var(--border-color);
  flex-wrap: wrap;
  gap: 16px;
}

.header-left h2 { margin: 0 0 6px 0; font-size: 1.6rem; color: var(--text-color); }
.header-left p { margin: 0; color: var(--accent-color); font-size: 0.9rem; }

.input-wrapper { width: 240px; }

/* 输入框样式统一 */
.sketch-input :deep(.el-input__wrapper) {
  box-shadow: none;
  border: 1px solid var(--border-color);
  background-color: var(--bg-color);
}
.sketch-input :deep(.el-input__inner) { color: var(--text-color); }
.sketch-btn-append {
  background-color: var(--accent-color) !important;
  color: #fff !important;
  border: none !important;
}
:global(.dark) .sketch-btn-append { color: #222 !important; }

/* 标签样式统一：像贴纸/便签 */
.sketch-tag {
  display: inline-block;
  padding: 4px 12px;
  background-color: var(--tag-bg);
  color: var(--tag-text);
  border-radius: 4px;
  font-size: 0.9rem;
  border: 1px solid var(--border-color);
}

/* 表格样式 */
.sketch-table {
  --el-table-bg-color: transparent;
  --el-table-tr-bg-color: transparent;
  --el-table-header-bg-color: transparent;
  --el-table-text-color: var(--text-color);
  --el-table-border-color: var(--border-color);
  --el-table-row-hover-bg-color: rgba(0,0,0,0.02);
}
:global(.dark) .sketch-table {
  --el-table-row-hover-bg-color: rgba(255,255,255,0.05);
}

.action-row {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
}

.edit-input :deep(.el-input__wrapper) {
  background: transparent;
  box-shadow: none;
  border-bottom: 1px solid var(--border-color);
  padding: 0;
  border-radius: 0;
}
.edit-input :deep(.el-input__inner) { color: var(--text-color); }

.icon-btn { font-size: 1.1rem; padding: 4px; }
.icon-btn.success { color: #67c23a; }
.icon-btn.danger { color: #f56c6c; }
</style>