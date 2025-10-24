<template>
  <div class="photo-wall">
    <h2>我的照片墙</h2>
    <el-form :inline="true" style="margin-bottom: 24px;" @submit.prevent="onSearch">
      <el-form-item label="标签">
        <el-select v-model="searchTags" multiple filterable placeholder="请选择标签进行检索" style="width: 240px;" > <el-option v-for="tag in allUserTags" :key="tag" :label="tag" :value="tag" /> </el-select>
      </el-form-item>
      <el-form-item label="描述">
        <el-input v-model="searchDescription" placeholder="图片描述关键词" style="width: 200px;" />
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
            <el-button type="warning" size="small" @click="openEditDialog(photo)">编辑标签和描述</el-button>
            <el-button size="small" @click="openImageEditor(photo)">编辑图片</el-button>
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

    <el-dialog v-model="editDialogVisible" title="编辑图片信息" width="500px">
      <el-form v-if="editingPhoto" :model="editForm" label-width="80px">
        <el-form-item label="描述">
          <el-input v-model="editForm.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="标签">
          <el-select
            v-model="editForm.tags"
            multiple
            filterable
            allow-create
            default-first-option
            placeholder="选择或创建新标签"
            style="width: 100%"
          >
            <el-option
              v-for="tag in allUserTags"
              :key="tag"
              :label="tag"
              :value="tag"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="savePhotoChanges" :loading="editLoading">保存</el-button>
      </template>
    </el-dialog>
    
    <el-dialog v-model="imageEditorVisible" title="编辑图片" width="90vw" top="3vh" :before-close="handleCloseImageEditor" @opened="initializeEditor">
      <div id="tui-image-editor-container" style="height: 80vh;"></div>
      <template #footer>
        <div class="dialog-footer">
            <el-button type="info" @click="instructionsVisible = true" style="float: left;">操作说明</el-button>
            <div>
                <el-button @click="handleCloseImageEditor">取消</el-button>
                <el-button type="primary" @click="saveEditedImage" :loading="isSavingImage">保存</el-button>
            </div>
        </div>
      </template>
    </el-dialog>

    <el-dialog v-model="instructionsVisible" title="图片编辑器操作指南" width="600px">
        <div class="instructions-content">
            <h4>顶部工具栏 (从左到右)</h4>
            <ul>
                <li><b>放大 (Zoom In):</b> 放大画布视图。</li>
                <li><b>缩小 (Zoom Out):</b> 缩小画布视图。</li>
                <li><b>Tips:</b> 也可以通过鼠标滚轮进行缩放。</li>
                <li><b>撤销 (Undo):</b> 撤销上一步操作。</li>
                <li><b>重做 (Redo):</b> 重复上一步被撤销的操作。</li>
                <li><b>重置 (Reset):</b> 清除所有编辑，恢复到初始状态。</li>
                <li><b>删除选中对象 (Delete):</b> 删除当前选中的对象（如文本框、绘画笔迹）。</li>
                <li><b>全部删除 (Delete All):</b> 删除所有添加的对象。</li>
            </ul>
            <h4>底部功能菜单</h4>
            <ul>
                <li><b>Crop (裁剪):</b> 提供自由裁剪和固定比例（方形、3:2、4:3、16:9等）裁剪。</li>
                <li><b>Flip (翻转):</b> 提供水平和垂直翻转功能。</li>
                <li><b>Rotate (旋转):</b> 提供顺时针/逆时针90度旋转和角度微调功能。</li>
                <li><b>Filter (滤镜):</b> 应用各种预设滤镜，如灰度、棕褐色调、反色、亮度调整等。</li>
                <li><b>Draw (绘画):</b> 在图片上进行自由绘画或画直线，可自定义颜色和笔触粗细。</li>
                <li><b>Text (文字):</b> 在图片上添加文字，可自定义字体、颜色、大小和样式。</li>
            </ul>
            <h4>右上角按钮</h4>
            <ul>
                <li><b>Load:</b> 从你的电脑重新选择一张图片来替换当前正在编辑的图片。</li>
                <li><b>Download:</b> 将当前编辑好的图片（画布状态）下载到你的电脑。</li>
            </ul>
            <h4>弹窗底部按钮</h4>
             <ul>
                <li><b>取消:</b> 关闭编辑器，不保存任何修改。</li>
                <li><b>保存:</b> 将编辑后的图片上传到服务器，替换原始图片。</li>
            </ul>
        </div>
        <template #footer>
            <el-button type="primary" @click="instructionsVisible = false">我明白了</el-button>
        </template>
    </el-dialog>

    <el-empty v-if="photos.length === 0" description="暂无照片" />
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus';
import { deletePhoto } from '../api/photo'
import ImageEditor from 'tui-image-editor';
import 'tui-image-editor/dist/tui-image-editor.css';


// --- 核心数据 ---
const photos = ref([])

// --- 弹窗控制 ---
const thumbDialogVisible = ref(false)
const infoDialogVisible = ref(false)
const editDialogVisible = ref(false);
const imageEditorVisible = ref(false);
const instructionsVisible = ref(false);

// --- 当前操作对象 ---
const currentThumb = ref(null)
const currentPhoto = ref(null)
const editingPhoto = ref(null);

// --- 表单和加载状态 ---
const editLoading = ref(false);
const editForm = ref({
  description: '',
  tags: []
});
const allUserTags = ref([]);

// --- 筛选器状态 ---
const searchTags = ref([])
const searchDescription = ref('')
const searchUploadDateRange = ref(null)
const searchDate = ref(null)
const searchLocation = ref('')
const searchResolution = ref('')
const resolutionType = ref('size')
const searchRatio = ref('')
const searchRatioCustom = ref('')
const searchMegapixel = ref('')
const searchMegapixelCustom = ref('')

// --- 图片编辑器状态 ---
const imageEditorInstance = ref(null);
const currentEditingPhoto = ref(null);
const isSavingImage = ref(false);


// --- 缩略图预览 ---
function showThumb(photo) {
  if (photo.thumbnail) {
    currentThumb.value = photo.thumbnail
    thumbDialogVisible.value = true
  } else {
    ElMessage.warning('该图片无缩略图')
  }
}

function handleCloseImageEditor() {
  if (imageEditorInstance.value) {
    imageEditorInstance.value.destroy();
    imageEditorInstance.value = null;
  }
  imageEditorVisible.value = false;
}

// --- 图片编辑器功能 ---
async function openImageEditor(photo) {
  currentEditingPhoto.value = photo;
  
  const fixedUrl = fixImageUrl(photo.image);
  
  imageEditorVisible.value = true;
  await nextTick();

  // 销毁旧实例
  if (imageEditorInstance.value) {
    imageEditorInstance.value.destroy();
    imageEditorInstance.value = null;
  }
  
  const container = document.querySelector('#tui-image-editor-container');
  if (!container) {
    console.error('❌ 找不到编辑器容器');
    ElMessage.error('编辑器容器未找到');
    return;
  }
  
  try {
    // 创建编辑器实例
    imageEditorInstance.value = new ImageEditor(container, {
      includeUI: {
        loadImage: {
          path: fixedUrl,
          name: photo.description || 'image'
        },
        menu: ['crop', 'flip', 'rotate', 'filter', 'draw', 'text'],
        initMenu: 'filter',
        uiSize: {
          width: '100%',
          height: '80vh',
        },
        menuBarPosition: 'bottom',
      },
      cssMaxWidth: null,
      cssMaxHeight: null,
      usageStatistics: false,
      selectionStyle: {
        cornerSize: 20,
        rotatingPointOffset: 70,
      },
    });

    // 监听事件
    imageEditorInstance.value.on('imageLoaded', (sizeValue) => {
      setTimeout(() => {
        window.dispatchEvent(new Event('resize'));
      }, 200);
    });

    imageEditorInstance.value.on('loadError', (error) => {
      console.error('❌ [事件] 图片加载失败:', error);
      ElMessage.error('图片加载失败');
    });
    
    // 轮询检查 + 强制激活 UI
    let checkCount = 0;
    const checkInterval = setInterval(() => {
      try {
        const imageName = imageEditorInstance.value.getImageName();
        const canvasSize = imageEditorInstance.value.getCanvasSize();
        
        if (canvasSize && canvasSize.width > 0 && canvasSize.height > 0) {
          clearInterval(checkInterval);
          
          // 关键修复：强制激活编辑器 UI
          setTimeout(() => {
            try {
              // 方法1: 触发编辑器内部的 resize
              window.dispatchEvent(new Event('resize'));
              
              // 方法2: 尝试访问编辑器的 UI 对象，激活它
              if (imageEditorInstance.value.ui) {
                imageEditorInstance.value.ui.activeMenuEvent();
              }
              
              // 方法3: 手动调整画布尺寸
              if (imageEditorInstance.value._graphics) {
                const canvas = imageEditorInstance.value._graphics.getCanvas();
                if (canvas) {
                  canvas.renderAll();
                }
              }
              
            } catch (activateError) {
              console.warn('⚠️ [激活] UI 激活过程出错（可能正常）:', activateError);
            }
          }, 500);
        }
        
        checkCount++;
      } catch (error) {
        clearInterval(checkInterval);
      }
    }, 200);
    
    // 多次延迟 resize
    await nextTick();
    const resizeTimes = [100, 300, 500, 1000, 1500, 2000];
    resizeTimes.forEach(delay => {
      setTimeout(() => {
        window.dispatchEvent(new Event('resize'));
        
        // 在每次 resize 时也尝试激活 UI
        if (delay >= 1000 && imageEditorInstance.value?.ui) {
          try {
            imageEditorInstance.value.ui.activeMenuEvent();
            console.log(`🔄 [定时 ${delay}ms] UI 已重新激活`);
          } catch (e) {
            // 忽略错误
          }
        }
      }, delay);
    });
    
  } catch (error) {
    console.error('❌ 创建编辑器失败:', error);
    ElMessage.error('创建编辑器失败: ' + error.message);
  }
}

// async function initializeEditor() {
//   // 确保有图片正在编辑
//   if (!currentEditingPhoto.value) return;

//   // 获取 DOM 容器
//   const container = document.querySelector('#tui-image-editor-container');
//   if (!container) {
//     console.error('❌ 找不到编辑器容器');
//     ElMessage.error('编辑器容器未找到');
//     return;
//   }
  
//   // 如果存在旧实例，先销毁
//   if (imageEditorInstance.value) {
//     imageEditorInstance.value.destroy();
//     imageEditorInstance.value = null;
//   }
  
//   try {
//     // 创建编辑器实例
//     imageEditorInstance.value = new ImageEditor(container, {
//       includeUI: {
//         menu: ['crop', 'flip', 'rotate', 'filter', 'draw', 'text'],
//         initMenu: 'filter',
//         uiSize: {
//           width: '100%',
//           height: '80vh', // 关键：恢复为 80vh，直接使用视窗高度
//         },
//         menuBarPosition: 'bottom',
//       },
//       cssMaxWidth: null,   // 恢复为 null，让编辑器内部处理
//       cssMaxHeight: null,  // 恢复为 null，让编辑器内部处理
//       usageStatistics: false,
//       selectionStyle: {
//         cornerSize: 20,
//         rotatingPointOffset: 70,
//       },
//     });

//     // 关键：在实例创建后异步加载图片
//     // 这比在配置中指定 path 更可靠
//     const imageUrl = fixImageUrl(currentEditingPhoto.value.image);
//     const imageName = currentEditingPhoto.value.description || 'image';
    
//     // loadImageFromURL 会返回一个 Promise，可以捕获加载错误
//     await imageEditorInstance.value.loadImageFromURL(imageUrl, imageName);
    
//     // 图片加载成功后，清除之前的操作栈（如果有）
//     imageEditorInstance.value.clearUndoStack();

//     console.log('✅ 编辑器和图片加载成功！');
    
//     // 主动触发一次 resize，以确保画布尺寸正确
//     // 此时触发通常是有效的，因为图片已加载完成
//     window.dispatchEvent(new Event('resize'));

//   } catch (error) {
//     console.error('❌ 创建或加载图片到编辑器失败:', error);
//     if (error && error.message && error.message.includes('filetype')) {
//         ElMessage.error('加载图片失败：不支持的文件类型。');
//     } else {
//         ElMessage.error('创建编辑器或加载图片时出错。');
//     }
//   }
// }

async function initializeEditor() {
  // 确保有图片正在编辑
  if (!currentEditingPhoto.value) return;

  // 获取 DOM 容器
  const container = document.querySelector('#tui-image-editor-container');
  if (!container) {
    console.error('❌ 找不到编辑器容器');
    ElMessage.error('编辑器容器未找到');
    return;
  }
  
  // 如果存在旧实例，先销毁
  if (imageEditorInstance.value) {
    imageEditorInstance.value.destroy();
    imageEditorInstance.value = null;
  }
  
  try {
    // 创建编辑器实例
    imageEditorInstance.value = new ImageEditor(container, {
      includeUI: {
        menu: ['crop', 'flip', 'rotate', 'filter', 'draw', 'text'],
        initMenu: 'filter',
        uiSize: {
          width: '100%',
          height: '80vh', // 关键：恢复为 80vh，直接使用视窗高度
        },
        menuBarPosition: 'bottom',
      },
      cssMaxWidth: null,   // 恢复为 null，让编辑器内部处理
      cssMaxHeight: null,  // 恢复为 null，让编辑器内部处理
      usageStatistics: false,
      selectionStyle: {
        cornerSize: 20,
        rotatingPointOffset: 70,
      },
    });

    // 关键：在实例创建后异步加载图片
    // 这比在配置中指定 path 更可靠
    const imageUrl = fixImageUrl(currentEditingPhoto.value.image);
    const imageName = currentEditingPhoto.value.description || 'image';
    
    // loadImageFromURL 会返回一个 Promise，可以捕获加载错误
    await imageEditorInstance.value.loadImageFromURL(imageUrl, imageName);
    
    // 图片加载成功后，清除之前的操作栈（如果有）
    imageEditorInstance.value.clearUndoStack();

    console.log('✅ 编辑器和图片加载成功！');
    
    // 等待 DOM 更新和渲染完成
    await nextTick();
    
    // 延迟执行初始化功能，确保编辑器完全就绪
    setTimeout(() => {
      // 添加鼠标滚轮缩放功能
      enableMouseWheelZoom();
      
      // 修复 Zoom In/Out 按钮
      fixZoomButtons();

      window.dispatchEvent(new Event('resize'));
    }, 300); // 延迟确保稳定性

  } catch (error) {
    console.error('❌ 创建或加载图片到编辑器失败:', error);
    if (error && error.message && error.message.includes('filetype')) {
        ElMessage.error('加载图片失败：不支持的文件类型。');
    } else {
        ElMessage.error('创建编辑器或加载图片时出错。');
    }
  }
}

// ✨ 新增：鼠标滚轮缩放功能（以鼠标位置为中心）
function enableMouseWheelZoom() {
  if (!imageEditorInstance.value) return;
  
  try {
    const canvas = imageEditorInstance.value._graphics.getCanvas();
    const fabric = window.fabric;
    
    if (!fabric) {
      console.warn('⚠️ Fabric.js 未加载');
      return;
    }
    
    // 添加鼠标滚轮事件监听
    canvas.on('mouse:wheel', (opt) => {
      const delta = opt.e.deltaY;
      let zoom = canvas.getZoom();
      
      // 计算新的缩放级别
      zoom = zoom - delta / 1000;
      
      // 限制缩放范围
      if (zoom > 5) zoom = 5;
      if (zoom < 0.5) zoom = 0.5;
      
      // 以鼠标指针位置为中心缩放
      const point = new fabric.Point(opt.e.offsetX, opt.e.offsetY);
      canvas.zoomToPoint(point, zoom);
      
      opt.e.preventDefault();
      opt.e.stopPropagation();
      
      canvas.renderAll();
    });
    
    console.log('✅ 鼠标滚轮缩放功能已启用');
  } catch (error) {
    console.error('⚠️ 启用滚轮缩放失败:', error);
  }
}

// ✨ 新增：修复 Zoom In/Out 按钮
function fixZoomButtons() {
  if (!imageEditorInstance.value) return;
  
  try {
    const canvas = imageEditorInstance.value._graphics.getCanvas();
    const fabric = window.fabric;
    
    if (!fabric) {
      console.warn('⚠️ Fabric.js 未加载');
      return;
    }
    
    const zoomInBtn = document.querySelector('.tie-btn-zoomIn');
    const zoomOutBtn = document.querySelector('.tie-btn-zoomOut');
    
    if (zoomInBtn) {
      const newZoomInBtn = zoomInBtn.cloneNode(true);
      zoomInBtn.parentNode.replaceChild(newZoomInBtn, zoomInBtn);
      
      newZoomInBtn.addEventListener('click', () => {
        let zoom = canvas.getZoom();
        zoom = zoom * 1.1;
        if (zoom > 5) zoom = 5;
        
        const center = canvas.getCenter();
        canvas.zoomToPoint(new fabric.Point(center.left, center.top), zoom);
        canvas.renderAll();
        console.log('🔍 Zoom In:', zoom.toFixed(2) + 'x');
      });
      
      console.log('✅ Zoom In 按钮已修复');
    }
    
    if (zoomOutBtn) {
      const newZoomOutBtn = zoomOutBtn.cloneNode(true);
      zoomOutBtn.parentNode.replaceChild(newZoomOutBtn, zoomOutBtn);
      
      newZoomOutBtn.addEventListener('click', () => {
        let zoom = canvas.getZoom();
        zoom = zoom / 1.1;
        if (zoom < 0.5) zoom = 0.5;
        
        const center = canvas.getCenter();
        canvas.zoomToPoint(new fabric.Point(center.left, center.top), zoom);
        canvas.renderAll();
        console.log('🔍 Zoom Out:', zoom.toFixed(2) + 'x');
      });
      
      console.log('✅ Zoom Out 按钮已修复');
    }
  } catch (error) {
    console.error('⚠️ 修复 Zoom 按钮失败:', error);
  }
}

async function saveEditedImage() {
  if (!imageEditorInstance.value || !currentEditingPhoto.value) {
    ElMessage.warning('没有可保存的内容');
    return;
  }

  isSavingImage.value = true;
  const token = localStorage.getItem('token');
  
  try {
    const base64String = imageEditorInstance.value.toDataURL();
    
    const res = await fetch(base64String);
    const blob = await res.blob();
    const file = new File([blob], currentEditingPhoto.value.image.split('/').pop(), { type: blob.type });

    const formData = new FormData();
    formData.append('image', file);
    
    const response = await axios.post(`/api/photos/${currentEditingPhoto.value.id}/edit-image/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        'Authorization': `Token ${token}`
      }
    });

    const index = photos.value.findIndex(p => p.id === currentEditingPhoto.value.id);
    if (index !== -1) {
      photos.value[index].image = `${response.data.image}?t=${new Date().getTime()}`;
    }

    ElMessage.success('图片更新成功！');
    handleCloseImageEditor();
  } catch (error) {
    console.error('图片保存失败:', error);
    ElMessage.error('图片保存失败，详情请查看控制台。');
  } finally {
    isSavingImage.value = false;
  }
}

// --- 编辑标签和描述功能 ---
function openEditDialog(photo) {
  editingPhoto.value = photo;
  editForm.value.description = photo.description || '';
  editForm.value.tags = [...(photo.tags || [])];
  editDialogVisible.value = true;
}

async function fetchAllUserTags() {
  const token = localStorage.getItem('token');
  if (!token) return;
  try {
    const res = await axios.get('/api/user_tags/', {
      headers: { Authorization: `Token ${token}` }
    });
    allUserTags.value = res.data.tags || [];
  } catch (e) {
    console.error('获取用户标签失败:', e);
  }
}

async function savePhotoChanges() {
  if (!editingPhoto.value) return;
  editLoading.value = true;
  const token = localStorage.getItem('token');
  try {
    const url = `/api/photos/${editingPhoto.value.id}/update/`;
    const payload = {
      description: editForm.value.description,
      tags: editForm.value.tags
    };
    const res = await axios.patch(url, payload, {
      headers: { Authorization: `Token ${token}` }
    });

    const index = photos.value.findIndex(p => p.id === editingPhoto.value.id);
    if (index !== -1) {
      photos.value[index].description = res.data.description;
      photos.value[index].tags = res.data.tags;
    }

    ElMessage.success('更新成功');
    editDialogVisible.value = false;
  } catch (e) {
    const errorMsg = e.response?.data ? JSON.stringify(e.response.data) : '更新失败';
    ElMessage.error(errorMsg);
  } finally {
    editLoading.value = false;
  }
}

// --- 辅助函数 ---
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
  
  // 移除所有可能的域名前缀
  let processedUrl = url;
  const prefixesToRemove = [
    'http://backend:8000',
    'https://backend:8000',
    'http://localhost:8000',
    'https://localhost:8000',
    'http://localhost:5173',
    'https://localhost:5173',
  ];
  
  for (const prefix of prefixesToRemove) {
    if (processedUrl.startsWith(prefix)) {
      processedUrl = processedUrl.replace(prefix, '');
      break;
    }
  }
  
  // 提取 /media/ 路径
  const idx = processedUrl.indexOf('/media/');
  let relativePath = idx !== -1 ? processedUrl.slice(idx) : processedUrl;
  
  // 确保路径以 / 开头
  if (!relativePath.startsWith('/')) {
    relativePath = '/' + relativePath;
  }
  
  // 返回相对路径，让 Vite 代理处理
  return relativePath;
}

function formatDate(dateStr) {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  return !isNaN(d) ? d.toLocaleString() : dateStr;
}

function formatTakenAt(takenAt) {
  if (!takenAt) return '';
  const d = new Date(takenAt);
  if (!isNaN(d)) {
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
  if (!exifDate) return '';
  const match = exifDate.match(/(\d{4}):(\d{1,2}):(\d{1,2}) (\d{2}:\d{2}:\d{2})/);
  if (match) {
    const [, y, m, d, t] = match;
    return `${y}/${parseInt(m)}/${parseInt(d)} ${t}`;
  }
  return exifDate;
}

// --- 数据获取与筛选 ---
async function fetchPhotos(params = {}) {
  const token = localStorage.getItem('token')
  if (!token) return
  try {
    const query = Object.entries(params)
      .filter(([, value]) => value)
      .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
      .join('&');
    const url = `/api/photos/${query ? '?' + query : ''}`;
    const res = await axios.get(url, {
      headers: { Authorization: `Token ${token}` }
    })
    photos.value = res.data.photos || []
  } catch (e) {
    console.error('获取照片失败:', e);
    photos.value = []
  }
}

function formatDateParam(dateObj) {
  if (!dateObj) return '';
  const yyyy = dateObj.getFullYear();
  const mm = (dateObj.getMonth() + 1).toString().padStart(2, '0');
  const dd = dateObj.getDate().toString().padStart(2, '0');
  return `${yyyy}-${mm}-${dd}`;
}

function onSearch() {
  const params = {
    tags: searchTags.value.join(','), 
    description: searchDescription.value,
    taken_date: searchDate.value ? formatDateParam(searchDate.value) : '',
    location: searchLocation.value
  };
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
  fetchPhotos(params)
}

function onReset() {
  searchTags.value = []
  searchDescription.value = ''
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
  try {
    await ElMessageBox.confirm(
      '确定要删除这张图片吗？此操作不可撤销。',
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    );

    const token = localStorage.getItem('token');
    if (!token) return;

    await deletePhoto(photoId, token);
    photos.value = photos.value.filter(p => p.id !== photoId);
    ElMessage.success('删除成功');

  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error);
      ElMessage.error('删除失败');
    }
  }
}


// --- 生命周期钩子 ---
onMounted(() => {
    fetchPhotos();
    fetchAllUserTags();
});

</script>

<style>
#tui-image-editor-container {
    height: 100%;
    min-height: 500px;
}
</style>

<style scoped>
.photo-wall {
  max-width: 900px;
  margin: 0 auto;
  padding: 32px 0;
}

.dialog-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
}

.instructions-content h4 {
    margin-top: 16px;
    margin-bottom: 8px;
    padding-bottom: 4px;
    border-bottom: 1px solid #eee;
}

.instructions-content ul {
    padding-left: 20px;
    list-style-type: disc;
}
.instructions-content li {
    margin-bottom: 8px;
}
</style>