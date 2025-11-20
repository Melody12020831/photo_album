<template>
  <div class="sketchbook-wrapper">

    <div v-if="isLoading" class="sketch-loader-wrapper">
      <div class="sketch-loader">
        <p class="loader-text">正在翻开作品集
          <span class="loader-dots" aria-hidden="true">
            <span class="dot">.</span>
            <span class="dot">.</span>
            <span class="dot">.</span>
          </span>
        </p>
      </div>
    </div>

    <div class="sketchbook-container" v-if="!isLoading">
      
      <div class="sketchbook-page page-left">
        <h2 class="page-title">创作索引</h2>
        <p class="page-subtitle">查找我的灵感</p>
        
        <el-form :inline="false" label-position="top" class="sketch-form" @submit.prevent="onSearch">
          <el-form-item label="标签笔记">
            <el-select v-model="searchTags" multiple filterable placeholder="选择“铅笔”标签" style="width: 100%;" > <el-option v-for="tag in allUserTags" :key="tag" :label="tag" :value="tag" /> </el-select>
          </el-form-item>
          <el-form-item label="描述关键词">
            <el-input v-model="searchDescription" placeholder="如：海边的日落" style="width: 100%;" />
          </el-form-item>
          <el-form-item label="上传日期范围">
            <el-date-picker
              v-model="searchUploadDateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              style="width: 100%;"
            />
          </el-form-item>
          <el-form-item label="拍摄日期">
            <el-date-picker v-model="searchDate" type="date" placeholder="选择日期" style="width: 100%;" />
          </el-form-item>
          <el-form-item label="拍摄地点">
            <el-input v-model="searchLocation" placeholder="如: 北京" style="width: 100%;" />
          </el-form-item>
          
          <el-form-item label="分辨率筛选" class="compact-item">
            <div class="compact-row">
              <el-select v-model="resolutionType" placeholder="类型" style="width: 100px;">
                <el-option label="精确尺寸" value="size" />
                <el-option label="宽高比" value="ratio" />
                <el-option label="总像素" value="megapixel" />
              </el-select>

              <template v-if="resolutionType === 'size'">
                <el-input v-model="searchResolution" placeholder="如: 4000x3000" style="width: 100px;" />
              </template>

              <template v-else-if="resolutionType === 'ratio'">
                <el-select v-model="searchRatio" placeholder="宽高比" style="width: 100px;">
                  <el-option label="16:9" value="16:9" />
                  <el-option label="4:3" value="4:3" />
                  <el-option label="1:1" value="1:1" />
                  <el-option label="3:2" value="3:2" />
                  <el-option label="自定义" value="custom" />
                </el-select>
                <el-input v-if="searchRatio === 'custom'" v-model="searchRatioCustom" placeholder="自定义(如 5:4)" style="width: 80px;" @input="onRatioCustomInput" />
              </template>

              <template v-else-if="resolutionType === 'megapixel'">
                <el-select v-model="searchMegapixel" placeholder="总像素" style="width: 100px;">
                  <el-option label=">5MP" value=">5" />
                  <el-option label=">12MP" value=">12" />
                  <el-option label=">24MP" value=">24" />
                  <el-option label="自定义" value="custom" />
                </el-select>
                <el-input v-if="searchMegapixel === 'custom'" v-model="searchMegapixelCustom" placeholder="自定义(如 >8)" style="width: 80px;" @input="onMegapixelCustomInput" />
              </template>
            </div>
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="onSearch" class="sketch-button">筛选</el-button>
            <el-button @click="onReset" class="sketch-button sketch-button-alt">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
      
      <div class="sketchbook-spine"></div>

      <div class="sketchbook-page page-right">
        <div class="page-right-content">
          <div class="control-bar">
            <template v-if="selectMode">
              <span class="batch-text">已选中 {{ selectedPhotoIds.length }} 张</span>
              <el-button type="primary" @click="confirmBatchSelect" class="sketch-button">选择完毕</el-button>
              <el-button @click="exitSelectMode" class="sketch-button sketch-button-alt" style="margin-left: 8px;">取消</el-button>
            </template>
            
            <template v-if="batchEditMode.active">
              <span class="batch-text" style="color: #409eff; font-weight: bold;">
                已选中 {{ batchSelectedPhotoIds.length }} 张图片
              </span>
              <el-button type="success" @click="batchDownload" :disabled="batchSelectedPhotoIds.length === 0" class="sketch-button">
                批量下载 ({{ batchSelectedPhotoIds.length }})
              </el-button>
              <el-button type="danger" @click="batchDelete" :disabled="batchSelectedPhotoIds.length === 0" class="sketch-button">
                批量删除 ({{ batchSelectedPhotoIds.length }})
              </el-button>
              <el-button type="warning" @click="openBatchEditTagsDialog" :disabled="batchSelectedPhotoIds.length === 0" class="sketch-button">
                修改标签 ({{ batchSelectedPhotoIds.length }})
              </el-button>
              <el-button @click="exitBatchEditMode" class="sketch-button sketch-button-alt">取消批量操作</el-button>
            </template>

            <template v-if="!selectMode && !batchEditMode.active">
              <el-button type="success" @click="enterSelectMode" :disabled="photos.length === 0" class="sketch-button">轮播播放</el-button>
              <el-button type="primary" @click="openSmartSearchDialog" class="sketch-button">智能搜索</el-button>
              <el-button type="warning" @click="router.push('/upload')" class="sketch-button">上传图片</el-button>
              <el-button type="success" @click="router.push('/tags')" class="sketch-button">标签管理</el-button>
              <el-button type="info" @click="enterBatchEditMode" :disabled="photos.length === 0" class="sketch-button">批量操作</el-button>
            </template>

            <!-- 每行显示照片数量选择器 -->
            <div class="layout-control" v-if="!selectMode && !batchEditMode.active">
              <span class="layout-label">每行显示：</span>
              <el-radio-group v-model="photosPerRow" size="small">
                <el-radio-button :label="2">2张</el-radio-button>
                <el-radio-button :label="3">3张</el-radio-button>
                <el-radio-button :label="4">4张</el-radio-button>
                <el-radio-button :label="5">5张</el-radio-button>
              </el-radio-group>
            </div>
          </div>
          
          <div v-if="photos.length > 0" class="photo-grid">
            <div v-for="(photo, idx) in photos" :key="photo.id" class="photo-card">
              
              <div class="washi-tape"></div>

              <div class="photo-container"
                @mouseenter="(e) => onPhotoHover(e, photo)"
                @mouseleave="onPhotoLeave"
                @mousemove="(e) => onPhotoMove(e, photo)"
              >
                <div v-if="selectMode" class="photo-select-check" @click.stop="toggleSelectPhoto(photo.id)">
                  <span v-if="selectedPhotoIds.includes(photo.id)" class="photo-check-mark">✔</span>
                </div>
                <div v-if="batchEditMode.active" class="photo-batch-check" @click.stop="toggleBatchSelectPhoto(photo.id)">
                  <span v-if="batchSelectedPhotoIds.includes(photo.id)" class="photo-check-mark">✔</span>
                </div>

                <img :src="fixImageUrl(photo.thumbnail || photo.image)" alt="photo"
                  class="photo-img"
                  @click="handlePhotoClick(photo, idx)"
                />
                
                <div
                  class="magnifying-loupe"
                  v-if="loupe.visible && loupe.photoId === photo.id"
                  :style="loupe.style"
                ></div>
              </div>

              <div class="photo-info">
                <span class="photo-title">{{ photo.description || '无描述' }}</span>
                <br />
                <small class="photo-meta">{{ formatDate(photo.uploaded_at) }}</small>
              </div>

              <div class="photo-actions">
                <el-button text size="small" @click="showInfo(photo)">信息</el-button>
                <el-button text size="small" @click="showThumb(photo)">缩略图</el-button>
                <el-button text size="small" @click="openEditDialog(photo)">编辑</el-button>
                <el-button text size="small" @click="openImageEditor(photo)">P.S.</el-button>
                <el-button text size="small" @click="downloadPhoto(photo)">下载</el-button>
                <el-button text size="small" @click="onDelete(photo.id)" style="color: #F56C6C;">删除</el-button>
              </div>
            </div>
          </div>
          
          <el-empty v-if="photos.length === 0" description="速写本还是空的..." />

        </div>
      </div>

    </div> <el-dialog v-model="smartSearchDialogVisible" title="智能搜索" width="500px" :close-on-click-modal="false" class="sketch-dialog">
      <template #default>
        <div>
          <el-input type="textarea" v-model="smartSearchInput" :rows="3" placeholder="请输入自然语言描述，如：去年夏天在海边拍的照片" />
        </div>
      </template>
      <template #footer>
        <el-button @click="smartSearchDialogVisible = false" class="sketch-button sketch-button-alt">取消</el-button>
        <el-button type="primary" :loading="smartSearchLoading" @click="submitSmartSearch" class="sketch-button">搜索</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="batchEditTagsDialogVisible" title="批量修改标签" width="600px" :close-on-click-modal="false" class="sketch-dialog">
      <template #default>
        <div>
          <p style="margin-bottom: 12px; color: var(--pencil-text);">
            已选中 <strong style="color: #409eff;">{{ batchSelectedPhotoIds.length }}</strong> 张图片
          </p>
          <el-alert 
            title="提示" 
            type="info" 
            :closable="false"
            style="margin-bottom: 16px;"
          >
            <template #default>
              <div style="font-size: 13px;">
                <p style="margin: 4px 0;">• <strong>添加标签</strong>：选择的标签会添加到所有图片（不会删除原有标签）</p>
                <p style="margin: 4px 0;">• <strong>替换标签</strong>：会清空所有图片的原有标签，仅保留您选择的标签</p>
              </div>
            </template>
          </el-alert>
          
          <el-form label-width="100px" label-position="top" class="sketch-form-inset">
            <el-form-item label="操作模式">
              <el-radio-group v-model="batchEditMode.mode">
                <el-radio label="add">添加标签</el-radio>
                <el-radio label="replace">替换标签</el-radio>
              </el-radio-group>
            </el-form-item>
            
            <el-form-item label="选择标签">
              <div style="display: flex; gap: 8px; width: 100%;">
                <el-select
                  v-model="batchEditMode.tags"
                  multiple
                  placeholder="请选择标签"
                  style="flex: 1;"
                  :loading="tagLoading"
                  filterable
                  allow-create
                  default-first-option
                >
                  <el-option
                    v-for="tag in allUserTags"
                    :key="tag"
                    :label="tag"
                    :value="tag"
                  />
                </el-select>
                <el-button @click="createNewTagForBatchEdit" class="sketch-button sketch-button-alt">新建标签</el-button>
              </div>
              <div v-if="allUserTags.length === 0" style="font-size: 12px; color: #909399; margin-top: 4px;">
                暂无标签，请先创建
              </div>
            </el-form-item>
          </el-form>
        </div>
      </template>
      <template #footer>
        <el-button @click="batchEditTagsDialogVisible = false" class="sketch-button sketch-button-alt">取消</el-button>
        <el-button 
          type="primary" 
          @click="confirmBatchEditTags"
          :loading="batchEditLoading"
          :disabled="batchEditMode.tags.length === 0"
          class="sketch-button"
        >
          确认修改
        </el-button>
      </template>
    </el-dialog>
    
    <el-dialog v-model="batchCarouselVisible" title="图片集合轮播" width="900px" :close-on-click-modal="false" class="sketch-dialog">
      <template #default>
        <div style="margin-bottom: 16px; display: flex; align-items: center; gap: 16px; padding: 12px; background: #f5f5f5; border-radius: 8px;">
          <el-switch 
            v-model="carouselAutoplay" 
            active-text="自动播放"
          />
          <template v-if="carouselAutoplay">
            <span style="color: #666;">切换间隔：</span>
            <el-button size="small" @click="carouselIntervalTemp = Math.max(0.01, carouselIntervalTemp - 1)">-</el-button>
            <el-input-number 
              v-model="carouselIntervalTemp" 
              :min="0.01" 
              :max="60" 
              :step="0.01"
              :precision="2"
              :controls="false"
              style="width: 100px;"
            />
            <el-button size="small" @click="carouselIntervalTemp = Math.min(60, carouselIntervalTemp + 1)">+</el-button>
            <span style="color: #666;">秒</span>
            <el-button type="primary" size="small" @click="applyCarouselInterval">确认</el-button>
          </template>
        </div>
        
        <div ref="batchCarouselWrapper" 
             @wheel="handleBatchCarouselWheel"
             @touchstart="handleTouchStart"
             @touchmove="handleTouchMove"
             @touchend="handleTouchEnd">
          <el-carousel 
            v-if="batchCarouselVisible"
            ref="batchCarouselRef" 
            height="500px" 
            arrow="always" 
            :autoplay="false">
            <el-carousel-item v-for="photo in batchCarouselPhotos" :key="photo.id">
              <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%;">
                <img :src="fixImageUrl(photo.image)" alt="原图" style="max-height: 400px; border-radius: 8px; box-shadow: 0 2px 24px #000a;" />
                <div class="carousel-info">
                  <h4>{{ photo.description || '无描述' }}</h4>
                  <p><b>拍摄时间：</b>{{ photo.taken_at ? formatTakenAt(photo.taken_at) : (photo.exif?.['EXIF DateTimeOriginal'] ? formatExifDate(photo.exif['EXIF DateTimeOriginal']) : '无') }}</p>
                  <p><b>标签：</b>
                    <span v-if="photo.tags && photo.tags.length">{{ photo.tags.join(', ') }}</span>
                    <span v-else>无</span>
                  </p>
                </div>
              </div>
            </el-carousel-item>
          </el-carousel>
        </div>
      </template>
      <template #footer>
        <el-button @click="batchCarouselVisible = false" class="sketch-button sketch-button-alt">关闭</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="previewDialogVisible" fullscreen custom-class="photo-preview-dialog" :show-close="false">
      <template #default>
        <div style="position: absolute; top: 20px; left: 20px; z-index: 10; display: flex; align-items: center; gap: 12px; padding: 12px; background: rgba(245, 245, 245, 0.95); border-radius: 8px;">
          <el-switch 
            v-model="previewAutoplay" 
            active-text="自动播放"
          />
          <template v-if="previewAutoplay">
            <span style="color: #666;">切换间隔：</span>
            <el-button size="small" @click="previewIntervalTemp = Math.max(0.01, previewIntervalTemp - 1)">-</el-button>
            <el-input-number 
              v-model="previewIntervalTemp" 
              :min="0.01" 
              :max="60" 
              :step="0.01"
              :precision="2"
              :controls="false"
              style="width: 100px;"
            />
            <el-button size="small" @click="previewIntervalTemp = Math.min(60, previewIntervalTemp + 1)">+</el-button>
            <span style="color: #666;">秒</span>
            <el-button type="primary" size="small" @click="applyPreviewInterval">确认</el-button>
          </template>
        </div>
        
        <div class="photo-preview-wrapper"
          @touchstart="onTouchStart"
          @touchmove="onTouchMove"
          @touchend="onTouchEnd"
        >
          <img :src="fixImageUrl(currentPreviewPhoto?.image)" alt="原图" class="photo-preview-img" />
          <div class="photo-preview-info">
            <h3><b>描述：</b>{{ currentPreviewPhoto?.description || '无描述' }}</h3>
            <p><b>拍摄时间：</b>{{ currentPreviewPhoto?.taken_at ? formatTakenAt(currentPreviewPhoto.taken_at) : (currentPreviewPhoto?.exif?.['EXIF DateTimeOriginal'] ? formatExifDate(currentPreviewPhoto.exif['EXIF DateTimeOriginal']) : '无') }}</p>
            <p><b>标签：</b>
              <span v-if="currentPreviewPhoto?.tags && currentPreviewPhoto.tags.length">{{ currentPreviewPhoto.tags.join(', ') }}</span>
              <span v-else>无</span>
            </p>
            <div style="margin-top: 16px; display: flex; justify-content: center; gap: 24px;">
              <el-button type="primary" @click="showPrev" class="sketch-button">上一张</el-button>
              <el-button type="primary" @click="showNext" class="sketch-button">下一张</el-button>
              <el-button type="info" @click="closePreview" class="sketch-button sketch-button-alt">关闭</el-button>
            </div>
          </div>
        </div>
      </template>
    </el-dialog>

    <el-dialog v-model="thumbDialogVisible" title="缩略图预览" width="350px" class="sketch-dialog" :before-close="() => thumbDialogVisible = false">
      <div v-if="currentThumb">
        <img :src="fixImageUrl(currentThumb)" alt="thumb" style="max-width: 100%; max-height: 300px; display: block; margin: 0 auto; border: 1px solid #ddd;" />
      </div>
    </el-dialog>

    <el-dialog v-model="infoDialogVisible" title="图片信息" width="500px" class="sketch-dialog" :before-close="() => infoDialogVisible = false">
      <template #default>
        <div v-if="currentPhoto" class="photo-info-list">
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
                  <el-button size="small" class="sketch-button sketch-button-alt">查看全部EXIF</el-button>
                </template>
                <div style="max-height: 200px; overflow: auto; background: #fff; padding: 10px;">
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

    <el-dialog v-model="editDialogVisible" title="编辑图片信息" width="500px" class="sketch-dialog">
      <el-form v-if="editingPhoto" :model="editForm" label-width="80px" label-position="top" class="sketch-form-inset">
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
        <el-button @click="editDialogVisible = false" class="sketch-button sketch-button-alt">取消</el-button>
        <el-button type="primary" @click="savePhotoChanges" :loading="editLoading" class="sketch-button">保存</el-button>
      </template>
    </el-dialog>
    
    <el-dialog v-model="imageEditorVisible" title="编辑图片" width="90vw" top="3vh" :before-close="handleCloseImageEditor" @opened="initializeEditor" class="sketch-dialog editor-dialog">
      <div id="tui-image-editor-container" style="height: 80vh;"></div>
      <template #footer>
        <div class="dialog-footer">
            <el-button type="info" @click="instructionsVisible = true" style="float: left;" class="sketch-button sketch-button-alt">操作说明</el-button>
            <div>
                <el-button @click="handleCloseImageEditor" class="sketch-button sketch-button-alt">取消</el-button>
                <el-button type="primary" @click="saveEditedImage" :loading="isSavingImage" class="sketch-button">保存</el-button>
            </div>
        </div>
      </template>
    </el-dialog>

    <el-dialog v-model="instructionsVisible" title="图片编辑器操作指南" width="600px" class="sketch-dialog">
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
            <el-button type="primary" @click="instructionsVisible = false" class="sketch-button">我明白了</el-button>
        </template>
    </el-dialog>

  </div> </template>


<style>
  @import url('https://fonts.googleapis.com/css2?family=Caveat:wght@400;700&display=swap');
</style>


<script setup>
// [新] 导入 isLoading 依赖
import { ref, onMounted, nextTick, watch } from 'vue' // 确保导入了 ref, onMounted, nextTick, watch
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus';
import { Loading } from '@element-plus/icons-vue'; // 您的代码中导入了
import { deletePhoto } from '../api/photo'
import ImageEditor from 'tui-image-editor';
import 'tui-image-editor/dist/tui-image-editor.css';
import { useRouter } from 'vue-router'

// --- [新] 放大镜 (Loupe) 逻辑 ---
const loupe = ref({
  visible: false,
  photoId: null,
  style: {}
})
const loupeSize = 150 // 放大镜直径 (px)
const zoomLevel = 3   // 放大倍数

// --- [新] 照片网格布局控制 ---
const photosPerRow = ref(3) // 默认每行显示3张照片

const router = useRouter()

// 计算放大镜样式
function onPhotoHover(e, photo) {
  const imgEl = e.currentTarget.querySelector('.photo-img')
  if (!imgEl) return
  
  loupe.value.visible = true
  loupe.value.photoId = photo.id
  updateLoupe(e, imgEl, photo)
}

function onPhotoLeave() {
  loupe.value.visible = false
  loupe.value.photoId = null
}

function onPhotoMove(e, photo) {
  if (!loupe.value.visible) return
  const container = e.currentTarget
  const imgEl = container.querySelector('.photo-img')
  if (!imgEl) return
  updateLoupe(e, imgEl, photo)
}

function updateLoupe(e, imgEl, photo) {
  const containerRect = e.currentTarget.getBoundingClientRect() // photo-container
  const imgRect = imgEl.getBoundingClientRect()
  
  // 鼠标相对于 container 的位置
  const x = e.clientX - containerRect.left
  const y = e.clientY - containerRect.top

  // 鼠标相对于 img 的位置 (用于计算 background-position)
  const imgX = e.clientX - imgRect.left
  const imgY = e.clientY - imgRect.top

  // 计算背景图位置
  // (图片内坐标 * 放大倍数) - (放大镜半径)
  const bgX = -(imgX * zoomLevel - loupeSize / 2)
  const bgY = -(imgY * zoomLevel - loupeSize / 2)

  loupe.value.style = {
    // 放大镜中心对准鼠标
    left: `${x - loupeSize / 2}px`,
    top: `${y - loupeSize / 2}px`,
    
    // 放大镜内图像
    backgroundImage: `url(${fixImageUrl(photo.image)})`,
    backgroundSize: `${imgRect.width * zoomLevel}px ${imgRect.height * zoomLevel}px`,
    backgroundPosition: `${bgX}px ${bgY}px`
  }
}

// --- 智能搜索相关 (原样) ---
const smartSearchDialogVisible = ref(false)
const smartSearchInput = ref('')
const smartSearchLoading = ref(false)
function openSmartSearchDialog() {
  smartSearchDialogVisible.value = true
  smartSearchInput.value = ''
}
async function submitSmartSearch() {
  if (!smartSearchInput.value.trim()) return
  smartSearchLoading.value = true
  try {
    const token = sessionStorage.getItem('token')
    const res = await axios.post('/api/search/mcp', { query: smartSearchInput.value }, {
      headers: { Authorization: `Token ${token}` }
    })
    if (res.data && res.data.photos) {
      photos.value = res.data.photos
      smartSearchDialogVisible.value = false
      ElMessage.success(`搜索完成！找到 ${res.data.photos.length} 张相关照片`)
    } else if (res.data && res.data.error) {
      ElMessage.error(res.data.error)
    }
  } catch (e) {
    ElMessage.error('智能搜索失败，请稍后再试')
  } finally {
    smartSearchLoading.value = false
  }
}

// --- 集合轮播 (原样) ---
const batchCarouselRef = ref(null)
const batchCarouselWrapper = ref(null)
const carouselAutoplay = ref(false)
const carouselInterval = ref(3) 
const carouselIntervalTemp = ref(3)
let carouselAutoplayTimer = null 
function startCarouselAutoplay() {
  stopCarouselAutoplay()
  if (carouselAutoplay.value && batchCarouselVisible.value && batchCarouselRef.value) {
    carouselAutoplayTimer = setInterval(() => {
      if (batchCarouselRef.value) {
        batchCarouselRef.value.next()
      }
    }, carouselInterval.value * 1000)
  }
}
function stopCarouselAutoplay() {
  if (carouselAutoplayTimer) {
    clearInterval(carouselAutoplayTimer)
    carouselAutoplayTimer = null
  }
}
function applyCarouselInterval() {
  carouselInterval.value = carouselIntervalTemp.value
  ElMessage.success(`已设置切换间隔为 ${carouselIntervalTemp.value} 秒`)
}
watch(carouselAutoplay, (newVal) => {
  if (newVal) {
    carouselIntervalTemp.value = carouselInterval.value
  }
})
watch([carouselAutoplay, carouselInterval], () => {
  if (carouselAutoplay.value) {
    startCarouselAutoplay()
  } else {
    stopCarouselAutoplay()
  }
})
function handleBatchCarouselWheel(e) {
  if (!batchCarouselVisible.value || !batchCarouselRef.value) return
  if (e.deltaY > 0) batchCarouselRef.value.next()
  if (e.deltaY < 0) batchCarouselRef.value.prev()
}
let touchStartX = 0
let touchStartY = 0
let touchEndX = 0
let touchEndY = 0
let isSwiping = false
function handleTouchStart(e) {
  if (!batchCarouselVisible.value) return
  touchStartX = e.touches[0].clientX
  touchStartY = e.touches[0].clientY
  touchEndX = touchStartX
  touchEndY = touchStartY
  isSwiping = false
}
function handleTouchMove(e) {
  if (!batchCarouselVisible.value) return
  touchEndX = e.touches[0].clientX
  touchEndY = e.touches[0].clientY
  
  const deltaX = touchEndX - touchStartX
  const deltaY = touchEndY - touchStartY
  
  if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > 10) {
    isSwiping = true
    e.preventDefault() 
  }
}
function handleTouchEnd(e) {
  if (!batchCarouselVisible.value || !batchCarouselRef.value) return
  
  const deltaX = touchEndX - touchStartX
  const deltaY = touchEndY - touchStartY
  
  if (isSwiping && Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > 50) {
    if (deltaX > 0) {
      batchCarouselRef.value.prev()
    } else {
      batchCarouselRef.value.next()
    }
    e.preventDefault()
  }
  
  touchStartX = 0
  touchStartY = 0
  touchEndX = 0
  touchEndY = 0
  isSwiping = false
}

// --- 集合轮播选择模式 (原样) ---
const selectMode = ref(false)
function enterSelectMode() {
  selectMode.value = true
  selectedPhotoIds.value = []
}
function exitSelectMode() {
  selectMode.value = false
  selectedPhotoIds.value = []
}
function toggleSelectPhoto(id) {
  const idx = selectedPhotoIds.value.indexOf(id)
  if (idx === -1) selectedPhotoIds.value.push(id)
  else selectedPhotoIds.value.splice(idx, 1)
}
function confirmBatchSelect() {
  batchCarouselPhotos.value = photos.value.filter(p => selectedPhotoIds.value.includes(p.id))
  batchCarouselVisible.value = true
  selectMode.value = false
}

// --- 批量编辑模式 (原样) ---
const batchEditMode = ref({
  active: false,
  mode: 'add', 
  tags: []
})
const batchSelectedPhotoIds = ref([])
const batchEditTagsDialogVisible = ref(false)
const batchEditLoading = ref(false)
const tagLoading = ref(false)
function enterBatchEditMode() {
  batchEditMode.value.active = true
  batchSelectedPhotoIds.value = []
}
function exitBatchEditMode() {
  batchEditMode.value.active = false
  batchSelectedPhotoIds.value = []
}
function toggleBatchSelectPhoto(id) {
  const idx = batchSelectedPhotoIds.value.indexOf(id)
  if (idx === -1) {
    batchSelectedPhotoIds.value.push(id)
  } else {
    batchSelectedPhotoIds.value.splice(idx, 1)
  }
}

// --- 处理图片点击 (原样) ---
function handlePhotoClick(photo, idx) {
  if (selectMode.value) {
    toggleSelectPhoto(photo.id)
  } else if (batchEditMode.value.active) {
    toggleBatchSelectPhoto(photo.id)
  } else {
    openPreview(idx)
  }
}

// --- 批量编辑标签 (原样) ---
function openBatchEditTagsDialog() {
  if (batchSelectedPhotoIds.value.length === 0) {
    ElMessage.warning('请先选择要编辑的图片')
    return
  }
  batchEditMode.value.mode = 'add'
  batchEditMode.value.tags = []
  batchEditTagsDialogVisible.value = true
}
async function createNewTagForBatchEdit() {
  try {
    const { value } = await ElMessageBox.prompt('请输入新的标签名', '新建标签', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputPattern: /\S/,
      inputErrorMessage: '标签名不能为空'
    })

    if (value) {
      const token = sessionStorage.getItem('token')
      const res = await axios.post('/api/user_tags/', { tag: value }, {
        headers: { Authorization: `Token ${token}` }
      })

      ElMessage.success(res.data.msg || '标签创建成功')
      
      await fetchAllUserTags()
      
      if (!batchEditMode.value.tags.includes(value)) {
        batchEditMode.value.tags.push(value)
      }
    }
  } catch (error) {
    if (error !== 'cancel') {
      const errorMsg = error.response?.data?.error || '创建失败'
      ElMessage.error(errorMsg)
    }
  }
}
async function confirmBatchEditTags() {
  if (batchSelectedPhotoIds.value.length === 0) {
    ElMessage.warning('请先选择要编辑的图片')
    return
  }
  
  if (batchEditMode.value.tags.length === 0) {
    ElMessage.warning('请选择至少一个标签')
    return
  }

  const mode = batchEditMode.value.mode
  const modeText = mode === 'add' ? '添加' : '替换'
  
  try {
    await ElMessageBox.confirm(
      `确定要为选中的 ${batchSelectedPhotoIds.value.length} 张图片${modeText}标签吗？`,
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    batchEditLoading.value = true
    const token = sessionStorage.getItem('token')
    
    let successCount = 0
    let failCount = 0

    for (const photoId of batchSelectedPhotoIds.value) {
      try {
        const photo = photos.value.find(p => p.id === photoId)
        if (!photo) continue

        let newTags = []
        if (mode === 'add') {
          newTags = [...new Set([...photo.tags, ...batchEditMode.value.tags])]
        } else {
          newTags = [...batchEditMode.value.tags]
        }

        await axios.post('/api/update_photo_tags/', {
          photo_id: photoId,
          tags: newTags
        }, {
          headers: { Authorization: `Token ${token}` }
        })

        photo.tags = newTags
        successCount++

      } catch (error) {
        failCount++
        console.error(`更新图片 ${photoId} 失败:`, error)
      }
    }

    batchEditLoading.value = false
    batchEditTagsDialogVisible.value = false

    if (successCount > 0) {
      ElMessage.success(`成功${modeText} ${successCount} 张图片的标签` + (failCount > 0 ? `，失败 ${failCount} 张` : ''))
    } else {
      ElMessage.error('所有图片标签更新失败')
    }

    exitBatchEditMode()

  } catch (error) {
    if (error !== 'cancel') {
      batchEditLoading.value = false
    }
  }
}

// --- 批量删除 (原样) ---
async function batchDelete() {
  if (batchSelectedPhotoIds.value.length === 0) {
    ElMessage.warning('请先选择要删除的图片')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${batchSelectedPhotoIds.value.length} 张图片吗？此操作不可恢复！`,
      '批量删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    const token = sessionStorage.getItem('token')
    let successCount = 0
    let failCount = 0

    for (const photoId of batchSelectedPhotoIds.value) {
      try {
        await deletePhoto(photoId)
        successCount++
      } catch (error) {
        failCount++
        console.error(`删除图片 ${photoId} 失败:`, error)
      }
    }

    if (successCount > 0) {
      ElMessage.success(`成功删除 ${successCount} 张图片` + (failCount > 0 ? `，失败 ${failCount} 张` : ''))
      fetchPhotos()
    } else {
      ElMessage.error('所有图片删除失败')
    }

    exitBatchEditMode()

  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量删除失败:', error)
    }
  }
}

// --- 下载 (原样) ---
async function downloadPhoto(photo) {
  try {
    const imageUrl = fixImageUrl(photo.image)
    const filename = photo.description ? `${photo.description}.jpg` : `photo_${photo.id}.jpg`
    
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)
    
    if (isMobile) {
      const link = document.createElement('a')
      link.href = imageUrl
      link.download = filename
      link.target = '_blank'
      
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      
      ElMessage.success('开始下载图片')
    } else {
      try {
        if ('showSaveFilePicker' in window) {
          const response = await fetch(imageUrl)
          const blob = await response.blob()
          
          const fileHandle = await window.showSaveFilePicker({
            suggestedName: filename,
            types: [{
              description: '图片文件',
              accept: {
                'image/jpeg': ['.jpg', '.jpeg'],
                'image/png': ['.png'],
                'image/gif': ['.gif'],
                'image/webp': ['.webp']
              }
            }]
          })
          
          const writable = await fileHandle.createWritable()
          await writable.write(blob)
          await writable.close()
          
          ElMessage.success('图片已保存')
        } else {
          const link = document.createElement('a')
          link.href = imageUrl
          link.download = filename
          link.target = '_blank'
          
          document.body.appendChild(link)
          link.click()
          document.body.removeChild(link)
          
          ElMessage.success('开始下载图片')
        }
      } catch (err) {
        if (err.name === 'AbortError') {
          ElMessage.info('已取消下载')
        } else {
          console.warn('使用降级下载方案:', err)
          const link = document.createElement('a')
          link.href = imageUrl
          link.download = filename
          link.target = '_blank'
          
          document.body.appendChild(link)
          link.click()
          document.body.removeChild(link)
          
          ElMessage.success('开始下载图片')
        }
      }
    }
  } catch (error) {
    console.error('下载图片失败:', error)
    ElMessage.error('下载图片失败')
  }
}

// --- 批量下载 (原样) ---
async function batchDownload() {
  if (batchSelectedPhotoIds.value.length === 0) {
    ElMessage.warning('请先选择要下载的图片')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要下载选中的 ${batchSelectedPhotoIds.value.length} 张图片吗？`,
      '批量下载确认',
      {
        confirmButtonText: '确定下载',
        cancelButtonText: '取消',
        type: 'info',
      }
    )

    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)
    
    ElMessage.info(`开始下载 ${batchSelectedPhotoIds.value.length} 张图片，请稍候...`)
    
    let successCount = 0
    let failCount = 0

    if (isMobile) {
      for (let i = 0; i < batchSelectedPhotoIds.value.length; i++) {
        const photoId = batchSelectedPhotoIds.value[i]
        const photo = photos.value.find(p => p.id === photoId)
        
        if (photo) {
          try {
            const imageUrl = fixImageUrl(photo.image)
            const filename = photo.description 
              ? `${photo.description}_${photo.id}.jpg` 
              : `photo_${photo.id}.jpg`
            
            const link = document.createElement('a')
            link.href = imageUrl
            link.download = filename
            link.target = '_blank'
            
            document.body.appendChild(link)
            link.click()
            document.body.removeChild(link)
            
            successCount++
            
            if (i < batchSelectedPhotoIds.value.length - 1) {
              await new Promise(resolve => setTimeout(resolve, 500))
            }
          } catch (error) {
            failCount++
            console.error(`下载图片 ${photoId} 失败:`, error)
          }
        } else {
          failCount++
        }
      }
    } else {
      const supportsSaveFilePicker = 'showSaveFilePicker' in window
      const supportsDirectoryPicker = 'showDirectoryPicker' in window
      
      if (batchSelectedPhotoIds.value.length === 1 && supportsSaveFilePicker) {
        const photoId = batchSelectedPhotoIds.value[0]
        const photo = photos.value.find(p => p.id === photoId)
        
        if (photo) {
          try {
            const imageUrl = fixImageUrl(photo.image)
            const filename = photo.description 
              ? `${photo.description}_${photo.id}.jpg` 
              : `photo_${photo.id}.jpg`
            
            const response = await fetch(imageUrl)
            const blob = await response.blob()
            
            const fileHandle = await window.showSaveFilePicker({
              suggestedName: filename,
              types: [{
                description: '图片文件',
                accept: {
                  'image/jpeg': ['.jpg', '.jpeg'],
                  'image/png': ['.png'],
                  'image/gif': ['.gif'],
                  'image/webp': ['.webp']
                }
              }]
            })
            
            const writable = await fileHandle.createWritable()
            await writable.write(blob)
            await writable.close()
            
            successCount = 1
            ElMessage.success('图片已保存')
          } catch (err) {
            if (err.name === 'AbortError') {
              ElMessage.info('已取消下载')
              return
            }
            failCount = 1
            console.error(`保存图片失败:`, err)
          }
        }
      } else if (supportsDirectoryPicker && batchSelectedPhotoIds.value.length > 1) {
        try {
          const dirHandle = await window.showDirectoryPicker({
            mode: 'readwrite',
            startIn: 'downloads'
          })
          
          ElMessage.info('正在保存图片到选定文件夹...')
          
          for (const photoId of batchSelectedPhotoIds.value) {
            const photo = photos.value.find(p => p.id === photoId)
            
            if (photo) {
              try {
                const imageUrl = fixImageUrl(photo.image)
                const filename = photo.description 
                  ? `${photo.description}_${photo.id}.jpg` 
                  : `photo_${photo.id}.jpg`
                
                const response = await fetch(imageUrl)
                const blob = await response.blob()
                
                const fileHandle = await dirHandle.getFileHandle(filename, { create: true })
                const writable = await fileHandle.createWritable()
                await writable.write(blob)
                await writable.close()
                
                successCount++
              } catch (error) {
                failCount++
                console.error(`保存图片 ${photoId} 失败:`, error)
              }
            } else {
              failCount++
            }
          }
        } catch (err) {
          if (err.name === 'AbortError') {
            ElMessage.info('已取消下载')
            return
          }
          console.error('选择文件夹失败:', err)
          ElMessage.error('选择文件夹失败，将使用默认下载方式')
          
          // 降级
          for (let i = 0; i < batchSelectedPhotoIds.value.length; i++) {
            const photoId = batchSelectedPhotoIds.value[i]
            const photo = photos.value.find(p => p.id === photoId)
            
            if (photo) {
              try {
                const imageUrl = fixImageUrl(photo.image)
                const filename = photo.description 
                  ? `${photo.description}_${photo.id}.jpg` 
                  : `photo_${photo.id}.jpg`
                
                const link = document.createElement('a')
                link.href = imageUrl
                link.download = filename
                link.target = '_blank'
                
                document.body.appendChild(link)
                link.click()
                document.body.removeChild(link)
                
                successCount++
                
                if (i < batchSelectedPhotoIds.value.length - 1) {
                  await new Promise(resolve => setTimeout(resolve, 300))
                }
              } catch (error) {
                failCount++
                console.error(`下载图片 ${photoId} 失败:`, error)
              }
            } else {
              failCount++
            }
          }
        }
      } else {
        // 不支持文件夹API：传统下载
        for (let i = 0; i < batchSelectedPhotoIds.value.length; i++) {
          const photoId = batchSelectedPhotoIds.value[i]
          const photo = photos.value.find(p => p.id === photoId)
          
          if (photo) {
            try {
              const imageUrl = fixImageUrl(photo.image)
              const filename = photo.description 
                ? `${photo.description}_${photo.id}.jpg` 
                : `photo_${photo.id}.jpg`
              
              const link = document.createElement('a')
              link.href = imageUrl
              link.download = filename
              link.target = '_blank'
              
              document.body.appendChild(link)
              link.click()
              document.body.removeChild(link)
              
              successCount++
              
              if (i < batchSelectedPhotoIds.value.length - 1) {
                await new Promise(resolve => setTimeout(resolve, 300))
              }
            } catch (error) {
              failCount++
              console.error(`下载图片 ${photoId} 失败:`, error)
            }
          } else {
            failCount++
          }
        }
      }
    }

    if (successCount > 0) {
      ElMessage.success(`成功下载 ${successCount} 张图片` + (failCount > 0 ? `，失败 ${failCount} 张` : ''))
    } else if (failCount > 0) {
      ElMessage.error('所有图片下载失败')
    }

  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量下载失败:', error)
    }
  }
}

// --- 集合轮播 (原样) ---
const selectedPhotoIds = ref([])
const batchCarouselVisible = ref(false)
const batchCarouselPhotos = ref([])

function openBatchCarousel() {
  batchCarouselVisible.value = true
  batchCarouselPhotos.value = photos.value.filter(p => selectedPhotoIds.value.includes(p.id))
}


// --- 全屏预览 (原样) ---
const previewDialogVisible = ref(false)
const currentPreviewIndex = ref(0)
const currentPreviewPhoto = ref(null)
const previewAutoplay = ref(false)
const previewInterval = ref(3) 
const previewIntervalTemp = ref(3)
let previewAutoplayTimer = null
function applyPreviewInterval() {
  previewInterval.value = previewIntervalTemp.value
  ElMessage.success(`已设置切换间隔为 ${previewIntervalTemp.value} 秒`)
}
function openPreview(idx) {
  currentPreviewIndex.value = idx
  updatePreviewPhoto()
  previewDialogVisible.value = true
}
function closePreview() {
  previewDialogVisible.value = false
  stopPreviewAutoplay()
}
function startPreviewAutoplay() {
  stopPreviewAutoplay()
  if (previewAutoplay.value && previewDialogVisible.value) {
    previewAutoplayTimer = setInterval(() => {
      if (currentPreviewIndex.value < photos.value.length - 1) {
        showNext()
      } else {
        currentPreviewIndex.value = 0
        updatePreviewPhoto()
      }
    }, previewInterval.value * 1000)
  }
}
function stopPreviewAutoplay() {
  if (previewAutoplayTimer) {
    clearInterval(previewAutoplayTimer)
    previewAutoplayTimer = null
  }
}
watch(previewAutoplay, (newVal) => {
  if (newVal) {
    previewIntervalTemp.value = previewInterval.value
  }
})
watch([previewAutoplay, previewInterval], () => {
  if (previewAutoplay.value) {
    startPreviewAutoplay()
  } else {
    stopPreviewAutoplay()
  }
})
watch(previewDialogVisible, (newVal) => {
  if (!newVal) {
    stopPreviewAutoplay()
  }
})
function showPrev() {
  if (currentPreviewIndex.value > 0) {
    currentPreviewIndex.value--;
    updatePreviewPhoto();
  } else {
    currentPreviewIndex.value = photos.value.length - 1;
    updatePreviewPhoto();
    ElMessage.info('已经从最后一张返回至第一张');
  }
}
function showNext() {
  if (currentPreviewIndex.value < photos.value.length - 1) {
    currentPreviewIndex.value++;
    updatePreviewPhoto();
  } else {
    currentPreviewIndex.value = 0;
    updatePreviewPhoto();
    ElMessage.info('已经是最后一张，已返回第一张');
  }
}
function updatePreviewPhoto() {
  currentPreviewPhoto.value = photos.value[currentPreviewIndex.value] || null;
}
function handleWheel(e) {
  if (!previewDialogVisible.value) return;
  if (e.deltaY > 0) showNext();
  if (e.deltaY < 0) showPrev();
}
let previewTouchStartX = 0
let previewTouchStartY = 0
let previewTouchEndX = 0
let previewTouchEndY = 0
let previewIsSwiping = false
function onTouchStart(e) {
  if (!previewDialogVisible.value) return
  previewTouchStartX = e.touches[0].clientX
  previewTouchStartY = e.touches[0].clientY
  previewTouchEndX = previewTouchStartX
  previewTouchEndY = previewTouchStartY
  previewIsSwiping = false
}
function onTouchMove(e) {
  if (!previewDialogVisible.value) return
  
  previewTouchEndX = e.touches[0].clientX
  previewTouchEndY = e.touches[0].clientY
  
  const deltaX = previewTouchEndX - previewTouchStartX
  const deltaY = previewTouchEndY - previewTouchStartY
  
  if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > 10) {
    previewIsSwiping = true
    e.preventDefault()
  }
}
function onTouchEnd(e) {
  if (!previewDialogVisible.value) return
  
  const deltaX = previewTouchEndX - previewTouchStartX
  const deltaY = previewTouchEndY - previewTouchStartY
  
  if (previewIsSwiping && Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > 50) {
    if (deltaX > 0) {
      showPrev()
    } else {
      showNext()
    }
    e.preventDefault()
  }
  
  previewTouchStartX = 0
  previewTouchStartY = 0
  previewTouchEndX = 0
  previewTouchEndY = 0
  previewIsSwiping = false
}
onMounted(() => {
  window.addEventListener('wheel', handleWheel);
});
import { onUnmounted } from 'vue';
onUnmounted(() => {
  window.removeEventListener('wheel', handleWheel);
});

// --- 核心数据 (原样) ---
const photos = ref([])
// [修改] isLoading 默认值
const isLoading = ref(true) // 确保 onMounted 时为 true

// --- 弹窗控制 (原样) ---
const thumbDialogVisible = ref(false)
const infoDialogVisible = ref(false)
const editDialogVisible = ref(false);
const imageEditorVisible = ref(false);
const instructionsVisible = ref(false);

// --- 当前操作对象 (原样) ---
const currentThumb = ref(null)
const currentPhoto = ref(null)
const editingPhoto = ref(null);

// --- 表单和加载状态 (原样) ---
const editLoading = ref(false);
const editForm = ref({
  description: '',
  tags: []
});
const allUserTags = ref([]);

// --- 筛选器状态 (原样) ---
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

// --- 图片编辑器状态 (原样) ---
const imageEditorInstance = ref(null);
const currentEditingPhoto = ref(null);
const isSavingImage = ref(false);


// --- 缩略图预览 (原样) ---
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

// --- 图片编辑器功能 (原样) ---
async function openImageEditor(photo) {
  currentEditingPhoto.value = photo;
  const fixedUrl = fixImageUrl(photo.image);
  imageEditorVisible.value = true;
  await nextTick();

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

    imageEditorInstance.value.on('imageLoaded', (sizeValue) => {
      setTimeout(() => {
        window.dispatchEvent(new Event('resize'));
      }, 200);
    });

    imageEditorInstance.value.on('loadError', (error) => {
      console.error('❌ [事件] 图片加载失败:', error);
      ElMessage.error('图片加载失败');
    });
    
    let checkCount = 0;
    const checkInterval = setInterval(() => {
      try {
        const imageName = imageEditorInstance.value.getImageName();
        const canvasSize = imageEditorInstance.value.getCanvasSize();
        
        if (canvasSize && canvasSize.width > 0 && canvasSize.height > 0) {
          clearInterval(checkInterval);
          
          setTimeout(() => {
            try {
              window.dispatchEvent(new Event('resize'));
              
              if (imageEditorInstance.value.ui) {
                imageEditorInstance.value.ui.activeMenuEvent();
              }
              
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
    
    await nextTick();
    const resizeTimes = [100, 300, 500, 1000, 1500, 2000];
    resizeTimes.forEach(delay => {
      setTimeout(() => {
        window.dispatchEvent(new Event('resize'));
        
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

// --- initializeEditor (原样) ---
async function initializeEditor() {
  if (!currentEditingPhoto.value) return;

  const container = document.querySelector('#tui-image-editor-container');
  if (!container) {
    console.error('❌ 找不到编辑器容器');
    ElMessage.error('编辑器容器未找到');
    return;
  }
  
  if (imageEditorInstance.value) {
    imageEditorInstance.value.destroy();
    imageEditorInstance.value = null;
  }
  
  try {
    imageEditorInstance.value = new ImageEditor(container, {
      includeUI: {
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

    const imageUrl = fixImageUrl(currentEditingPhoto.value.image);
    const imageName = currentEditingPhoto.value.description || 'image';
    
    await imageEditorInstance.value.loadImageFromURL(imageUrl, imageName);
    
    imageEditorInstance.value.clearUndoStack();

    console.log('✅ 编辑器和图片加载成功！');
    
    await nextTick();
    
    setTimeout(() => {
      enableMouseWheelZoom();
      fixZoomButtons();
      window.dispatchEvent(new Event('resize'));
    }, 300); 

  } catch (error) {
    console.error('❌ 创建或加载图片到编辑器失败:', error);
    if (error && error.message && error.message.includes('filetype')) {
        ElMessage.error('加载图片失败：不支持的文件类型。');
    } else {
        ElMessage.error('创建编辑器或加载图片时出错。');
    }
  }
}

// --- 滚轮缩放 (原样) ---
function enableMouseWheelZoom() {
  if (!imageEditorInstance.value) return;
  
  try {
    const canvas = imageEditorInstance.value._graphics.getCanvas();
    const fabric = window.fabric;
    
    if (!fabric) {
      console.warn('⚠️ Fabric.js 未加载');
      return;
    }
    
    canvas.on('mouse:wheel', (opt) => {
      const delta = opt.e.deltaY;
      let zoom = canvas.getZoom();
      
      zoom = zoom - delta / 1000;
      
      if (zoom > 5) zoom = 5;
      if (zoom < 0.5) zoom = 0.5;
      
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

// --- 修复缩放按钮 (原样) ---
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

// --- 保存编辑 (原样) ---
async function saveEditedImage() {
  if (!imageEditorInstance.value || !currentEditingPhoto.value) {
    ElMessage.warning('没有可保存的内容');
    return;
  }

  isSavingImage.value = true;
  const token = sessionStorage.getItem('token');
  
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

// --- 编辑标签和描述 (原样) ---
function openEditDialog(photo) {
  editingPhoto.value = photo;
  editForm.value.description = photo.description || '';
  editForm.value.tags = [...(photo.tags || [])];
  editDialogVisible.value = true;
}

async function fetchAllUserTags() {
  const token = sessionStorage.getItem('token');
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
  const token = sessionStorage.getItem('token');
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

// --- 辅助函数 (原样) ---
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
  const idx = processedUrl.indexOf('/media/');
  let relativePath = idx !== -1 ? processedUrl.slice(idx) : processedUrl;
  if (!relativePath.startsWith('/')) {
    relativePath = '/' + relativePath;
  }
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

// --- 数据获取与筛选 (原样) ---
async function fetchPhotos(params = {}) {
  console.log('[DEBUG] fetchPhotos 开始执行')
  const token = sessionStorage.getItem('token')
  console.log('[DEBUG] token 状态:', token ? '存在' : '不存在')
  if (!token) {
    console.log('[DEBUG] 无 token，设置 isLoading = false')
    isLoading.value = false
    return
  }
  console.log('[DEBUG] 开始加载照片，设置 isLoading = true')
  isLoading.value = true // [修改] 确保在开始时设置为 true
  try {
    const query = Object.entries(params)
      .filter(([, value]) => value)
      .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
      .join('&');
    const url = `/api/photos/${query ? '?' + query : ''}`;
    console.log('[DEBUG] 请求 URL:', url)
    const res = await axios.get(url, {
      headers: { Authorization: `Token ${token}` }
    })
    console.log('[DEBUG] 获取到照片数量:', res.data.photos?.length || 0)
    photos.value = res.data.photos || []
    console.log('[DEBUG] photos.value 已更新:', photos.value.length)
  } catch (e) {
    console.error('[DEBUG] 获取照片失败:', e);
    photos.value = []
  } finally {
    // [新] 增加一点延迟，让加载动画更自然
    console.log('[DEBUG] 设置 isLoading = false (带500ms延迟)')
    setTimeout(() => {
      isLoading.value = false
    }, 500); // 至少显示 500ms 的加载
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

// --- 删除 (原样) ---
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

    const token = sessionStorage.getItem('token');
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


// --- 生命周期钩子 (原样) ---
onMounted(() => {
    console.log('[DEBUG] PhotoWallView onMounted 执行')
    console.log('[DEBUG] isLoading 初始值:', isLoading.value)
    console.log('[DEBUG] photos 初始值:', photos.value)
    fetchPhotos();
    fetchAllUserTags();
});

</script>


<style>
/* --- [新] CSS 变量定义 --- */
:root {
  --paper-bg: #fdfaf4; /* 纸张基底色 (米白色) */
  --paper-lines: #ede8e0; /* 纸张线条色 (淡褐色) */
  --pencil-text: #4a4a4a; /* 铅笔字颜色 (石墨灰) */
  --handwriting-font: 'Caveat', cursive; /* 手写字体 */
  --spine-color: #58493a; /* 书脊颜色 (深棕色) */
  --washi-tape-bg: rgba(255, 248, 220, 0.7); /* 和纸胶带背景 (半透明淡黄) */

  /* 模拟纸张纹理和横线 (用于右页) */
  --paper-texture-lines: 
    linear-gradient(
      to bottom,
      transparent 9px,
      var(--paper-lines) 9px,
      var(--paper-lines) 10px,
      transparent 10px
    );
  --paper-background-full: var(--paper-bg);
  --paper-background-lines: repeating-linear-gradient(
      var(--paper-bg), 
      var(--paper-bg) 23px, 
      var(--paper-lines) 24px
  );
}

/* --- [新] 弹窗 (Dialog) 拟物化 --- */
.sketch-dialog .el-dialog {
  background: var(--paper-bg) !important;
  border: 1px solid #dcdcdc;
  box-shadow: 5px 5px 15px rgba(0,0,0,0.15);
  border-radius: 2px !important;
}
.sketch-dialog .el-dialog__title {
  font-family: var(--handwriting-font);
  font-size: 2.5rem;
  color: var(--pencil-text);
}
.sketch-dialog .el-dialog__body {
  background: repeating-linear-gradient(
    var(--paper-bg), 
    var(--paper-bg) 23px, 
    rgba(237, 232, 224, 0.5) 24px
  );
  color: var(--pencil-text);
}
/* 弹窗内的表单 */
.sketch-form-inset .el-form-item__label {
  font-family: var(--handwriting-font);
  font-size: 0.75rem; /* 缩小表单弹窗内标签字体 */
  color: var(--pencil-text);
  line-height: 1.2;
}

/* --- [新] 全屏预览 (photo-preview-dialog) 拟物化 --- */
.photo-preview-dialog {
  /* 从纯黑变为纸张的半透明
  background: rgba(0,0,0,0.95) !important; */
  background: rgba(253, 250, 244, 0.9) !important;
  backdrop-filter: blur(5px);
}
/* 继承自原版 scoped style */
.photo-preview-dialog .el-dialog__body {
  padding: 0;
}
.photo-preview-wrapper {
  position: relative;
  width: 100vw;
  height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  /* 背景色由 .photo-preview-dialog 控制 */
}
.photo-preview-info {
  font-family: var(--handwriting-font);
  color: var(--pencil-text); /* 从 #fff 改为铅笔色 */
  background: rgba(255, 255, 255, 0.7); /* 从黑色透明改为白色透明 */
  padding: 24px 32px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);
}
.photo-preview-info h3, .photo-preview-info p {
  color: var(--pencil-text);
  margin: 8px 0;
}
.photo-preview-img {
  max-width: 90vw;
  max-height: 70vh;
  box-shadow: 0 5px 25px rgba(0,0,0,0.2) !important; /* 阴影更重 */
  border: 10px solid #fff; /* 像一张实体照片 */
  border-radius: 8px;
  margin-bottom: 32px;
}

/* --- [新] Element Plus 组件拟物化 (输入框, 按钮) --- */

/* 拟物化按钮 (全局) */
.sketch-button {
  font-family: var(--handwriting-font) !important;
  font-size: 1.2rem !important;
  font-weight: 700 !important;
  border-radius: 3px !important;
  border: 1px solid rgba(0,0,0,0.1) !important;
  box-shadow: 1px 1px 3px rgba(0,0,0,0.1) !important;
  transition: all 0.2s ease !important;
  padding: 16px 20px !important;
}
.sketch-button:hover {
  transform: translateY(-1px);
  box-shadow: 2px 2px 5px rgba(0,0,0,0.15) !important;
}
.sketch-button.el-button--primary {
  background: #007aff !important;
  color: #fff !important;
}
.sketch-button.sketch-button-alt {
  background: #f0f0f0 !important;
  color: var(--pencil-text) !important;
  border-color: #ccc !important;
}
.sketch-button.el-button--danger {
  background: #f56c6c !important;
}

/* 拟物化输入框 (全局) */
.sketch-form .el-input__wrapper,
.sketch-dialog .el-input__wrapper,
.sketch-form .el-select__wrapper,
.sketch-dialog .el-select__wrapper,
.sketch-form .el-textarea__inner,
.sketch-dialog .el-textarea__inner,
.sketch-form .el-date-editor {
  background: #fff !important;
  border: none !important;
  border-bottom: 2px dashed var(--paper-lines) !important;
  box-shadow: none !important;
  border-radius: 0 !important;
  padding-left: 5px !important;
}
.sketch-form .el-input__wrapper:hover,
.sketch-dialog .el-input__wrapper:hover,
.sketch-form .el-select__wrapper:hover,
.sketch-dialog .el-select__wrapper:hover,
.sketch-form .el-textarea__inner:hover,
.sketch-dialog .el-textarea__inner:hover,
.sketch-form .el-date-editor:hover {
  border-bottom-color: #409eff !important;
}
.sketch-form .el-input__inner,
.sketch-dialog .el-input__inner,
.sketch-form .el-textarea__inner,
.sketch-dialog .el-textarea__inner {
  font-family: var(--handwriting-font);
  font-size: 1.3rem;
  color: var(--pencil-text);
}
/* 标签表单项 */
.sketch-form .el-form-item__label,
.sketch-form-inset .el-form-item__label {
  font-family: var(--handwriting-font);
  font-size: 1.5rem;
  color: var(--pencil-text);
  line-height: 1.2;
}
.compact-row {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
}
.compact-item :deep(.el-select),
.compact-item :deep(.el-input) {
  display: inline-block;
}

/* TUI 编辑器弹窗 */
.editor-dialog .el-dialog__body {
  background: #f0f0f0 !important; /* 编辑器需要一个中性背景 */
}

/* 继承自原版的 TUI 编辑器样式 */
#tui-image-editor-container {
    height: 100%;
    min-height: 500px;
}
</style>


<style scoped>
/* --- [新] 加载动画 --- */
.sketch-loader-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100vh;
  background: var(--paper-bg);
}
.loader-text {
  font-family: var(--handwriting-font);
  font-size: 1.8rem;
  color: var(--pencil-text);
  margin-top: 12px;
}
.sketch-loader {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 0;
}

/* 文本点动画（1 -> 2 -> 3 点循环） */
.loader-text {
  font-family: var(--handwriting-font);
  font-size: 1.8rem;
  color: var(--pencil-text);
  margin: 0;
}
.loader-dots {
  display: inline-block;
  margin-left: 6px;
  font-weight: bold;
}
.loader-dots .dot {
  opacity: 0;
  display: inline-block;
  transform: translateY(0);
}
.loader-dots .dot:nth-child(1) { animation: dot1 0.6s infinite; }
.loader-dots .dot:nth-child(2) { animation: dot2 0.6s infinite; }
.loader-dots .dot:nth-child(3) { animation: dot3 0.6s infinite; }

@keyframes dot1 {
  0% { opacity: 0; }
  24% { opacity: 0; }
  25% { opacity: 1; }
  94% { opacity: 1; }
 100% { opacity: 0; }
}
@keyframes dot2 {
  0% { opacity: 0; }
  49% { opacity: 0; }
  50% { opacity: 1; }
  94% { opacity: 1; }
 100% { opacity: 0; }
}
@keyframes dot3 {
  0% { opacity: 0; }
  74% { opacity: 0; }
  75% { opacity: 1; }
  94% { opacity: 1; }
 100% { opacity: 0; }
}


/* --- [新] 速写本布局 --- */
.sketchbook-wrapper {
  width: 100%;
  height: calc(100vh - 60px); /* 减去顶部导航栏的高度 */
  background: #d3c7b1; /* 桌子背景 */
  padding: 20px 0;
  overflow: hidden; /* 禁止外层滚动 */
  display: flex;
  align-items: center;
  justify-content: center;
}
.sketchbook-container {
  display: flex;
  width: 95vw;
  max-width: 1800px;
  height: calc(100vh - 100px); /* 固定高度，减去导航栏和padding */
  background: var(--paper-bg);
  box-shadow: 0 10px 30px rgba(0,0,0,0.3);
  border: 1px solid #ccc;
  border-radius: 2px;
  overflow: hidden; /* 容器本身不滚动 */
}

.sketchbook-spine {
  width: 20px;
  background: var(--spine-color);
  box-shadow: inset 0 0 10px rgba(0,0,0,0.5);
}

.sketchbook-page {
  padding: 24px;
  position: relative;
}

/* 左页 (控制面板) */
.page-left {
  flex: 0 0 280px; /* 缩小左侧边栏宽度 */
  background: var(--paper-bg);
  border-right: 1px dashed #ccc;
  overflow-y: auto; /* 左侧可以独立滚动 */
  height: 100%; /* 占满容器高度 */
}
.page-title {
  font-family: var(--handwriting-font);
  font-size: 1.5rem; /* 缩小标题 */
  color: var(--pencil-text);
  margin-top: 0;
  margin-bottom: 0;
}
.page-subtitle {
  font-family: var(--handwriting-font);
  font-size: 0.8rem; /* 缩小副标题 */
  color: #888;
  margin-top: 0;
  margin-bottom: 16px; /* 减小间距 */
  border-bottom: 1px solid var(--paper-lines);
  padding-bottom: 8px;
}
.sketch-form {
  margin-bottom: 0;
}
.sketch-form .el-form-item {
  margin-bottom: 16px; /* 减小表单项间距 */
}
/* 使用 :deep() 确保能作用到 Element Plus 组件内部生成的 label 元素 */
.sketch-form :deep(.el-form-item__label),
.sketch-form-inset :deep(.el-form-item__label) {
  font-size: 0.75rem !important; /* 缩小标签字体并加 !important 覆盖默认样式 */
  padding-bottom: 4px;
  font-family: var(--handwriting-font);
}

/* 输入框和选择框内的文字大小 - 缩小到约一半 */
.sketch-form :deep(.el-input__inner) {
  font-size: 0.65rem; /* 输入框内文字大小 (约为之前的一半) */
}

.sketch-form :deep(.el-select__placeholder) {
  font-size: 0.65rem; /* 选择框占位符大小 */
}

.sketch-form :deep(.el-input__inner::placeholder) {
  font-size: 0.65rem; /* 输入框占位符大小 */
}

.sketch-form :deep(.el-select .el-input__inner) {
  font-size: 0.65rem; /* 选择框文字大小 */
}

.sketch-form :deep(.el-date-editor .el-input__inner) {
  font-size: 0.65rem; /* 日期选择器文字大小 */
}

.sketch-form :deep(.el-tag) {
  font-size: 0.6rem; /* 标签文字大小 */
}

.sketch-form :deep(.el-select__tags-text) {
  font-size: 0.65rem; /* 多选标签文字 */
}

/* 右页 (照片) */
.page-right {
  flex: 1;
  background: var(--paper-background-lines);
  overflow-y: auto; /* 右侧可以独立滚动 */
  height: 100%; /* 占满容器高度 */
}
.page-right-content {
  padding: 10px;
  min-height: 100%; /* 确保内容至少占满高度 */
}

.control-bar {
  margin-bottom: 24px;
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
  padding-bottom: 16px;
  border-bottom: 2px dashed var(--paper-lines);
}

.batch-text {
  font-family: var(--handwriting-font);
  font-size: 1.5rem;
  color: var(--pencil-text);
}

/* 布局控制器 */
.layout-control {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 8px;
}

.layout-label {
  font-family: var(--handwriting-font);
  font-size: 1.3rem;
  color: var(--pencil-text);
}

/* --- [新] 照片网格布局 --- */
.photo-grid {
  display: grid;
  grid-template-columns: repeat(v-bind(photosPerRow), 1fr); /* 动态列数 */
  gap: 24px;
}

/* --- [新] 拟物化照片卡片 --- */
.photo-card {
  position: relative;
  background: #fff;
  border: 1px solid #eee;
  box-shadow: 3px 3px 8px rgba(0,0,0,0.1);
  padding: 10px;
  padding-bottom: 15px;
  transition: transform 0.2s, box-shadow 0.2s;
  
  /* 随机轻微旋转，模拟不规则粘贴 */
  transform: rotate(-0.5deg);
}
.photo-card:nth-child(2n) { transform: rotate(0.8deg); }
.photo-card:nth-child(3n) { transform: rotate(-0.3deg); }
.photo-card:nth-child(4n) { transform: rotate(0.6deg); }

.photo-card:hover {
  transform: scale(1.03) rotate(0deg) !important;
  box-shadow: 5px 5px 15px rgba(0,0,0,0.15);
  z-index: 5;
}

/* [新] 和纸胶带 (Washi Tape) 效果 */
.washi-tape {
  content: '';
  position: absolute;
  top: -10px;
  left: 50%;
  transform: translateX(-50%) rotate(1deg);
  width: 120px;
  height: 25px;
  background: var(--washi-tape-bg);
  box-shadow: 0 1px 1px rgba(0,0,0,0.1);
  border-left: 2px dashed rgba(255, 255, 255, 0.5);
  border-right: 2px dashed rgba(255, 255, 255, 0.5);
  z-index: 2;
  opacity: 0.8;
  pointer-events: none;
}
.photo-card:nth-child(2n) .washi-tape { transform: translateX(-50%) rotate(-1.5deg); }
.photo-card:nth-child(3n) .washi-tape { width: 100px; }

/* [新] 照片容器 (用于放大镜) */
.photo-container {
  position: relative;
  overflow: hidden; /* 必须，用于剪切放大镜 */
  background: #f0f0f0;
}
.photo-img {
  width: 100%;
  height: 200px;
  object-fit: cover;
  cursor: pointer;
  display: block;
  transition: filter 0.2s;
}
.photo-card:hover .photo-img {
  filter: brightness(1.05);
}

/* [新] 放大镜 (Loupe) 样式 */
.magnifying-loupe {
  position: absolute;
  width: 150px; /* 匹配 JS loupeSize */
  height: 150px; /* 匹配 JS loupeSize */
  border-radius: 50%;
  border: 4px solid #fff;
  box-shadow: 0 0 10px rgba(0,0,0,0.3), inset 0 0 5px rgba(0,0,0,0.1);
  pointer-events: none;
  background-repeat: no-repeat;
  z-index: 10;
  backdrop-filter: blur(1px);
  /* backgroundImage, backgroundSize, backgroundPosition 
    由 JavaScript 动态设置
  */
}


/* [新] 拟物化照片信息 (铅笔注释) */
.photo-info {
  margin-top: 12px;
  padding: 0 5px;
  text-align: left;
}
.photo-title {
  font-family: var(--handwriting-font);
  font-size: 1.6rem;
  font-weight: 700;
  color: var(--pencil-text);
  display: block;
  line-height: 1.2;
}
.photo-meta {
  font-family: var(--handwriting-font);
  font-size: 1.1rem;
  color: #777;
}

/* [新] 拟物化照片操作 (文本按钮) */
.photo-actions {
  margin-top: 12px;
  text-align: right;
  display: flex;
  gap: 4px;
  justify-content: flex-end;
  flex-wrap: wrap;
}
.photo-actions .el-button {
  font-family: var(--handwriting-font);
  font-size: 1.1rem;
  font-weight: 700;
  color: #666;
  padding: 4px 8px;
}
.photo-actions .el-button:hover {
  color: #007aff;
  background: rgba(0, 122, 255, 0.05);
}


/* --- 选择覆盖层 (继承自原版) --- */
.photo-select-check,
.photo-batch-check {
  position: absolute;
  left: 10px;
  top: 10px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 3; /* 高于图片，但低于胶带 (如果胶带在角落) */
  cursor: pointer;
  border: 2px solid #fff;
  transition: all 0.3s;
}
.photo-select-check {
  background: rgba(0,0,0,0.25);
}
.photo-batch-check {
  background: rgba(64, 158, 255, 0.3);
  border-color: #409eff;
}
.photo-batch-check:hover {
  background: rgba(64, 158, 255, 0.5);
  transform: scale(1.1);
}
.photo-check-mark {
  color: #fff; /* 原版 #42b983 在白色边框上不明显，改为 #fff */
  font-size: 20px;
  font-weight: bold;
  text-shadow: 0 1px 2px rgba(0,0,0,0.5);
}

/* --- 轮播弹窗内的信息 (拟物化) --- */
.carousel-info {
  font-family: var(--handwriting-font);
  color: var(--pencil-text);
  margin-top: 16px;
  text-align: center;
  background: rgba(255,255,255,0.7);
  padding: 10px 20px;
  border-radius: 4px;
}
.carousel-info h4 {
  font-size: 1.8rem;
  margin: 5px 0;
}
.carousel-info p {
  font-size: 1.2rem;
  margin: 5px 0;
}

/* --- 图片信息弹窗 (拟物化) --- */
.photo-info-list ul {
  padding-left: 0;
  list-style: none;
  font-family: var(--handwriting-font);
  font-size: 1.4rem;
  color: var(--pencil-text);
}
.photo-info-list li {
  margin-bottom: 12px;
  line-height: 1.4;
}

/* --- TUI 编辑器操作指南 (继承自原版) --- */
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