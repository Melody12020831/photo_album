<template>
  <!-- 绑定主题属性到最外层 -->
  <div class="sketchbook-wrapper" :data-theme="isDark ? 'dark' : 'light'">

    <!-- 加载界面 -->
    <div v-if="isLoading" class="sketch-loader-wrapper">
      <div class="sketch-loader-content">
        <div class="loader-icon-box">
          <el-icon class="is-loading loader-icon"><Loading /></el-icon>
        </div>
        <p class="loader-text">
          正在翻开作品集
          <span class="loader-dots">
            <span class="dot" style="--i:1">.</span>
            <span class="dot" style="--i:2">.</span>
            <span class="dot" style="--i:3">.</span>
          </span>
        </p>
      </div>
    </div>

    <div class="sketchbook-container" v-if="!isLoading">
      
      <div class="sketchbook-page page-left">
        <!-- 标题栏布局 -->
        <div class="page-header-row">
          <h2 class="page-title">创作索引</h2>
          <el-switch
            v-model="isDark"
            inline-prompt
            :active-icon="Moon"
            :inactive-icon="Sunny"
            style="--el-switch-on-color: #4c4d4f; --el-switch-off-color: #d4b483"
            @change="toggleTheme"
            class="sketch-switch"
          />
        </div>
        <p class="page-subtitle">查找我的灵感</p>
        
        <el-form :inline="false" label-position="top" class="sketch-form" @submit.prevent="onSearch">
          <el-form-item label="标签笔记">
            <el-select v-model="searchTags" multiple filterable placeholder="选择“铅笔”标签" style="width: 100%;" > <el-option v-for="tag in allUserTags" :key="tag" :label="tag" :value="tag" /> </el-select>
          </el-form-item>
          <el-form-item label="描述关键词">
            <el-input v-model="searchDescription" placeholder="如：日落(指上传时对照片的描述)" style="width: 100%;" />
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
            <!-- 统一按钮风格 -->
            <el-button type="primary" @click="onSearch" class="sketch-sticker-button btn-blue">筛选</el-button>
            <el-button @click="onReset" class="sketch-sticker-button btn-gray">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
      
      <div class="sketchbook-spine"></div>

      <div class="sketchbook-page page-right">
        <div class="page-right-content">
          <div class="control-bar">
            <!-- 批量选择模式 -->
            <template v-if="selectMode">
              <span class="batch-text">已选中 {{ selectedPhotoIds.length }} 张</span>
              <!-- 统一按钮风格 -->
              <el-button type="primary" @click="confirmBatchSelect" class="sketch-sticker-button btn-blue">选择完毕</el-button>
              <el-button @click="exitSelectMode" class="sketch-sticker-button btn-gray" style="margin-left: 8px;">取消</el-button>
            </template>
            
            <!-- 批量编辑模式 -->
            <template v-if="batchEditMode.active">
              <span class="batch-text" style="color: #409eff; font-weight: bold;">
                已选中 {{ batchSelectedPhotoIds.length }} 张图片
              </span>
              <!-- 统一按钮风格 -->
              <el-button type="success" @click="batchDownload" :disabled="batchSelectedPhotoIds.length === 0" class="sketch-sticker-button btn-green">
                批量下载 ({{ batchSelectedPhotoIds.length }})
              </el-button>
              <el-button type="danger" @click="batchDelete" :disabled="batchSelectedPhotoIds.length === 0" class="sketch-sticker-button btn-red">
                批量删除 ({{ batchSelectedPhotoIds.length }})
              </el-button>
              <el-button type="warning" @click="openBatchEditTagsDialog" :disabled="batchSelectedPhotoIds.length === 0" class="sketch-sticker-button btn-orange">
                修改标签 ({{ batchSelectedPhotoIds.length }})
              </el-button>
              <el-button @click="exitBatchEditMode" class="sketch-sticker-button btn-gray">取消批量操作</el-button>
            </template>

            <!-- 默认模式：功能按键组 -->
            <template v-if="!selectMode && !batchEditMode.active">
              <!-- 移除 nowrap 和 overflow-x，恢复自动换行，去除滚动条 -->
              <div class="action-button-group">
                <el-button type="success" @click="enterSelectMode" :disabled="photos.length === 0" class="sketch-sticker-button btn-green">轮播播放</el-button>
                <el-button type="primary" @click="openSmartSearchDialog" class="sketch-sticker-button btn-blue">智能搜索</el-button>
                <el-button type="warning" @click="router.push('/upload')" class="sketch-sticker-button btn-orange">上传图片</el-button>
                <el-button type="success" @click="router.push('/tags')" class="sketch-sticker-button btn-lime">标签管理</el-button>
                <el-button type="info" @click="enterBatchEditMode" :disabled="photos.length === 0" class="sketch-sticker-button btn-gray">批量操作</el-button>
                
                <!-- 紧凑布局：文字在上，按钮在下。使用 margin-left: auto 将其推到最右侧 -->
                <div style="display: flex; flex-direction: column; align-items: flex-start; margin-left: auto; padding-left: 16px; border-left: 2px dashed var(--border-dashed);">
                  <span class="layout-label" style="font-size: 0.9rem; margin-bottom: 4px; line-height: 1; color: var(--pencil-text);">每行显示：</span>
                  <el-radio-group v-model="photosPerRow" size="small" class="sketch-radio-group">
                    <el-radio-button :label="2">2张</el-radio-button>
                    <el-radio-button :label="3">3张</el-radio-button>
                    <el-radio-button :label="4">4张</el-radio-button>
                    <el-radio-button :label="5">5张</el-radio-button>
                  </el-radio-group>
                </div>
              </div>
            </template>

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

    </div>

    <!-- 弹窗部分 -->
    <el-dialog v-model="smartSearchDialogVisible" title="智能搜索" width="500px" :close-on-click-modal="false" class="sketch-dialog">
      <template #default>
        <div>
          <el-input type="textarea" v-model="smartSearchInput" :rows="3" placeholder="请输入自然语言描述，如：去年夏天在海边拍的照片" />
        </div>
      </template>
      <template #footer>
        <el-button @click="smartSearchDialogVisible = false" class="sketch-sticker-button btn-gray">取消</el-button>
        <el-button type="primary" :loading="smartSearchLoading" @click="submitSmartSearch" class="sketch-sticker-button btn-blue">搜索</el-button>
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
                <el-button @click="createNewTagForBatchEdit" class="sketch-sticker-button btn-gray" size="small">新建标签</el-button>
              </div>
            </el-form-item>
          </el-form>
        </div>
      </template>
      <template #footer>
        <el-button @click="batchEditTagsDialogVisible = false" class="sketch-sticker-button btn-gray">取消</el-button>
        <el-button 
          type="primary" 
          @click="confirmBatchEditTags"
          :loading="batchEditLoading"
          :disabled="batchEditMode.tags.length === 0"
          class="sketch-sticker-button btn-blue"
        >
          确认修改
        </el-button>
      </template>
    </el-dialog>
    
    <!-- 统一按钮风格 -->
    <el-dialog 
      v-model="batchCarouselVisible" 
      fullscreen 
      :show-close="false" 
      custom-class="carousel-fullscreen-dialog"
      class="carousel-fullscreen-dialog"
      @opened="onCarouselDialogOpened"
      @closed="onCarouselDialogClosed"
    >
      <template #default>
        <!-- 顶部控制栏 -->
        <transition name="slide-down">
          <div v-show="showUI" class="fullscreen-top-bar">
            <div class="top-bar-content">
              <el-switch v-model="carouselAutoplay" active-text="自动播放" />
              <template v-if="carouselAutoplay">
                <span style="color: var(--pencil-text); margin-left: 8px;">间隔：</span>
                <el-input-number 
                  v-model="carouselIntervalTemp" 
                  :min="0.01" :max="60" :step="0.01" :precision="2" :controls="false" size="small" style="width: 60px;"
                />
                <span style="color: var(--pencil-text);">秒</span>
                <el-button type="primary" size="small" @click="applyCarouselInterval" circle style="margin-left:4px;">ok</el-button>
              </template>
              <div class="top-bar-right">
                <!-- 统一按钮风格 -->
                <el-button @click="toggleUI" type="info" text bg size="small" class="sketch-sticker-button btn-gray" style="padding: 4px 12px !important;">
                  <el-icon><Hide /></el-icon> 折叠
                </el-button>
                <el-button @click="batchCarouselVisible = false" type="danger" text bg size="small" class="sketch-sticker-button btn-red" style="padding: 4px 12px !important;">关闭</el-button>
              </div>
            </div>
          </div>
        </transition>

        <transition name="fade">
          <div v-show="!showUI" class="floating-show-ui-btn" @click="toggleUI" title="展开信息">
            <el-icon><View /></el-icon>
          </div>
        </transition>

        <div ref="batchCarouselWrapper" 
             class="carousel-wrapper-fullscreen"
             :class="{ 'ui-hidden-mode': !showUI }"
             @wheel="handleBatchCarouselWheel"
             @touchstart="handleTouchStart"
             @touchmove="handleTouchMove"
             @touchend="handleTouchEnd">
          
          <!-- v-if="batchCarouselRendered" 确保弹窗动画结束后再渲染 Carousel -->
          <el-carousel 
            v-if="batchCarouselRendered && batchCarouselPhotos.length > 0"
            ref="batchCarouselRef" 
            height="100vh" 
            indicator-position="none"
            arrow="always" 
            :autoplay="false">
            <el-carousel-item v-for="photo in batchCarouselPhotos" :key="photo.id">
              <div class="carousel-item-fullscreen">
                <img :src="fixImageUrl(photo.image)" alt="原图" class="carousel-img-fullscreen" />
                
                <transition name="slide-up">
                  <div v-show="showUI" class="carousel-info-overlay">
                    <h4>{{ photo.description || '无描述' }}</h4>
                    <p class="overlay-meta">
                      <span>📅 拍摄：{{ photo.taken_at ? formatTakenAt(photo.taken_at) : (photo.exif?.['EXIF DateTimeOriginal'] ? formatExifDate(photo.exif['EXIF DateTimeOriginal']) : '无') }}</span>
                      <span v-if="photo.tags && photo.tags.length" style="margin-left: 10px;">🏷️ {{ photo.tags.join(', ') }}</span>
                    </p>
                  </div>
                </transition>
              </div>
            </el-carousel-item>
          </el-carousel>

           <!-- 加载中提示 -->
          <div v-else class="carousel-loading">
            <el-icon class="is-loading" style="font-size: 40px; color: #fff;"><Loading /></el-icon>
          </div>

        </div>
      </template>
    </el-dialog>

    <!-- 单图预览 - 全屏沉浸模式 -->
    <el-dialog v-model="previewDialogVisible" fullscreen custom-class="photo-preview-dialog" class="photo-preview-dialog" :show-close="false">
       <template #default>
        <transition name="slide-down">
          <div v-show="showUI" class="fullscreen-top-bar">
            <div class="top-bar-content">
              <el-switch v-model="previewAutoplay" active-text="自动播放" />
              <template v-if="previewAutoplay">
                <span style="color: var(--pencil-text); margin-left: 8px;">间隔：</span>
                <el-input-number 
                  v-model="previewIntervalTemp" 
                  :min="0.01" :max="60" :step="0.01" :precision="2" :controls="false" size="small" style="width: 60px;"
                />
                <span style="color: var(--pencil-text);">秒</span>
                <el-button type="primary" size="small" @click="applyPreviewInterval" circle style="margin-left:4px;">ok</el-button>
              </template>
              <div class="top-bar-right">
                <el-button @click="toggleUI" type="info" text bg size="small" class="sketch-sticker-button btn-gray" style="padding: 4px 12px !important;">
                  <el-icon><Hide /></el-icon> 折叠
                </el-button>
                <el-button @click="closePreview" type="danger" text bg size="small" class="sketch-sticker-button btn-red" style="padding: 4px 12px !important;">关闭</el-button>
              </div>
            </div>
          </div>
        </transition>

        <transition name="fade">
          <div v-show="!showUI" class="floating-show-ui-btn" @click="toggleUI" title="展开信息">
            <el-icon><View /></el-icon>
          </div>
        </transition>
        
        <div class="photo-preview-wrapper"
          @touchstart="onTouchStart"
          @touchmove="onTouchMove"
          @touchend="onTouchEnd"
        >
          <!-- 左右独立导航按钮 -->
          <div class="preview-nav-btn prev-btn" :class="{ 'ui-hidden': !showUI }" @click.stop="showPrev">
            <el-icon><ArrowLeft /></el-icon>
          </div>
          <div class="preview-nav-btn next-btn" :class="{ 'ui-hidden': !showUI }" @click.stop="showNext">
            <el-icon><ArrowRight /></el-icon>
          </div>

          <img :src="fixImageUrl(currentPreviewPhoto?.image)" alt="原图" class="photo-preview-img-fullscreen" />
          
          <transition name="slide-up">
            <div v-show="showUI" class="photo-preview-info-overlay">
              <div class="info-content">
                <h3>{{ currentPreviewPhoto?.description || '无描述' }}</h3>
                <div class="info-meta-row">
                  <span>📅 {{ currentPreviewPhoto?.taken_at ? formatTakenAt(currentPreviewPhoto.taken_at) : (currentPreviewPhoto?.exif?.['EXIF DateTimeOriginal'] ? formatExifDate(currentPreviewPhoto.exif['EXIF DateTimeOriginal']) : '无') }}</span>
                  <span v-if="currentPreviewPhoto?.tags && currentPreviewPhoto.tags.length" style="margin-left: 12px;">🏷️ {{ currentPreviewPhoto.tags.join(', ') }}</span>
                </div>
              </div>
            </div>
          </transition>
        </div>
      </template>
    </el-dialog>

    <!-- 其它弹窗 -->
    <el-dialog v-model="thumbDialogVisible" title="缩略图预览" width="350px" class="sketch-dialog" :before-close="() => thumbDialogVisible = false">
      <div v-if="currentThumb">
        <img :src="fixImageUrl(currentThumb)" alt="thumb" style="max-width: 100%; max-height: 300px; display: block; margin: 0 auto; border: 1px solid var(--border-color);" />
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
            <li><b>拍摄时间：</b>{{ currentPhoto.taken_at ? formatTakenAt(currentPhoto.taken_at) : (currentPhoto.exif && currentPhoto.exif['EXIF DateTimeOriginal'] ? formatExifDate(currentPhoto.exif['EXIF DateTimeOriginal']) : '无') }}</li>
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
        <el-button @click="editDialogVisible = false" class="sketch-sticker-button btn-gray">取消</el-button>
        <el-button type="primary" @click="savePhotoChanges" :loading="editLoading" class="sketch-sticker-button btn-blue">保存</el-button>
      </template>
    </el-dialog>
    
    <!-- P.S.图片编辑器 - 全屏沉浸，无滚动条 -->
    <el-dialog 
      v-model="imageEditorVisible" 
      fullscreen 
      :show-close="false"
      custom-class="editor-dialog"
      class="editor-dialog"
      @opened="initializeEditor" 
    >
      <!-- 顶部工具栏替代默认 Header -->
      <div class="editor-top-bar">
        <span class="editor-title">P.S. 图片工坊</span>
        <div class="editor-actions">
           <el-button type="info" @click="instructionsVisible = true" class="sketch-sticker-button btn-gray" size="small">操作说明</el-button>
           <el-button @click="handleCloseImageEditor" class="sketch-sticker-button btn-red" size="small">取消</el-button>
           <el-button type="primary" @click="saveEditedImage" :loading="isSavingImage" class="sketch-sticker-button btn-blue" size="small">保存修改</el-button>
        </div>
      </div>
      
      <!-- 编辑器容器，确保全屏 -->
      <div id="tui-image-editor-container"></div>
      
    </el-dialog>

    <el-dialog v-model="instructionsVisible" title="图片编辑器操作指南" width="900px" class="sketch-dialog instructions-dialog">
        <div class="instructions-content">
            <div class="instructions-grid">
                <!-- 左列：顶部工具栏 -->
                <div class="inst-col">
                    <h4>顶部工具栏 (从左到右)</h4>
                    <ul>
                        <li><b>放大 (Zoom In):</b> 先点击后，再点击图片即可放大画布视图。</li>
                        <li><b>缩小 (Zoom Out):</b> 缩小画布视图。</li>
                        <li><b>Tips:</b> 也可以通过鼠标滚轮进行缩放。</li>
                        <li><b>撤销 (Undo):</b> 撤销上一步操作。</li>
                        <li><b>重做 (Redo):</b> 重复上一步被撤销的操作。</li>
                        <li><b>重置 (Reset):</b> 清除所有编辑，恢复到初始状态。</li>
                        <li><b>删除选中对象 (Delete):</b> 删除当前选中的对象（如文本框、绘画笔迹）。</li>
                        <li><b>全部删除 (Delete All):</b> 删除所有添加的对象。</li>
                    </ul>
                </div>

                <!-- 右列：底部菜单 + 右上角 -->
                <div class="inst-col">
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
                </div>
            </div>
        </div>
        <template #footer>
            <el-button type="primary" @click="instructionsVisible = false" class="sketch-sticker-button btn-blue">我明白了</el-button>
        </template>
    </el-dialog>

  </div> 
</template>


<style>
  @import url('https://fonts.googleapis.com/css2?family=Caveat:wght@400;700&display=swap');
</style>


<script setup>
import { ref, onMounted, nextTick, watch, onUnmounted } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus';
import { Loading, Moon, Sunny, Hide, View, ArrowLeft, ArrowRight } from '@element-plus/icons-vue';
import { deletePhoto } from '../api/photo'
import ImageEditor from 'tui-image-editor';
import 'tui-image-editor/dist/tui-image-editor.css';
import { useRouter } from 'vue-router'

// --- 1. 所有基础 Ref 定义 (按类别分组，防止引用错误) ---

// 基础状态
const photos = ref([])
const isLoading = ref(true) 
const isDark = ref(false)
const photosPerRow = ref(3)
const loupeSize = 150 
const zoomLevel = 3   
const loupe = ref({ visible: false, photoId: null, style: {} })

// 弹窗显示控制
const batchCarouselVisible = ref(false)
const batchCarouselRendered = ref(false)
const previewDialogVisible = ref(false)
const thumbDialogVisible = ref(false)
const infoDialogVisible = ref(false)
const editDialogVisible = ref(false);
const imageEditorVisible = ref(false);
const instructionsVisible = ref(false);
const batchEditTagsDialogVisible = ref(false)
const smartSearchDialogVisible = ref(false)

// 选中与编辑状态
const selectedPhotoIds = ref([])
const batchSelectedPhotoIds = ref([])
const batchEditMode = ref({ active: false, mode: 'add', tags: [] })
const editingPhoto = ref(null);
const currentThumb = ref(null)
const currentPhoto = ref(null)
const currentEditingPhoto = ref(null);

// 轮播与预览状态
const batchCarouselPhotos = ref([])
const currentPreviewIndex = ref(0)
const currentPreviewPhoto = ref(null)
const previewAutoplay = ref(false)
const previewInterval = ref(3) 
const previewIntervalTemp = ref(3)
const carouselAutoplay = ref(false)
const carouselInterval = ref(3) 
const carouselIntervalTemp = ref(3)
const batchCarouselRef = ref(null)
const batchCarouselWrapper = ref(null)
const showUI = ref(true);

// 表单与搜索
const editLoading = ref(false);
const editForm = ref({ description: '', tags: [] });
const allUserTags = ref([]);
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
const smartSearchInput = ref('')
const smartSearchLoading = ref(false)

// 编辑器与其它
const imageEditorInstance = ref(null);
const isSavingImage = ref(false);
const tagLoading = ref(false)
const router = useRouter()

// --- 2. 独立的辅助逻辑 ---

// 切换UI显示状态（轮播/预览时的控制栏显示隐藏）
function toggleUI() {
  showUI.value = !showUI.value;
}

// 监听弹窗变化，自动重置UI显示
watch([() => batchCarouselVisible.value, () => previewDialogVisible.value], ([val1, val2]) => {
  if (val1 || val2) {
    showUI.value = true;
  }
});

// 切换主题（明暗模式）
function toggleTheme() {
  updateThemeAttribute()
}

// 更新主题属性到DOM
function updateThemeAttribute() {
  const theme = isDark.value ? 'dark' : 'light';
  document.documentElement.setAttribute('data-theme', theme)
  if (isDark.value) {
    document.body.classList.add('dark-theme');
    // 同时为 Element Plus 设置暗色类
    document.documentElement.classList.add('dark');
  } else {
    document.body.classList.remove('dark-theme');
    document.documentElement.classList.remove('dark');
  }
}

// 监听系统主题变化
function handleSystemThemeChange(e) {
  isDark.value = e.matches
  updateThemeAttribute()
}

// 鼠标悬停在照片上时显示放大镜
function onPhotoHover(e, photo) {
  const imgEl = e.currentTarget.querySelector('.photo-img')
  if (!imgEl) return
  loupe.value.visible = true
  loupe.value.photoId = photo.id
  updateLoupe(e, imgEl, photo)
}

// 鼠标离开照片时隐藏放大镜
function onPhotoLeave() {
  loupe.value.visible = false
  loupe.value.photoId = null
}

// 鼠标在照片上移动时更新放大镜位置
function onPhotoMove(e, photo) {
  if (!loupe.value.visible) return
  const container = e.currentTarget
  const imgEl = container.querySelector('.photo-img')
  if (!imgEl) return
  updateLoupe(e, imgEl, photo)
}

// 更新放大镜的位置和背景
function updateLoupe(e, imgEl, photo) {
  const containerRect = e.currentTarget.getBoundingClientRect()
  const imgRect = imgEl.getBoundingClientRect()
  const x = e.clientX - containerRect.left
  const y = e.clientY - containerRect.top
  const imgX = e.clientX - imgRect.left
  const imgY = e.clientY - imgRect.top
  const bgX = -(imgX * zoomLevel - loupeSize / 2)
  const bgY = -(imgY * zoomLevel - loupeSize / 2)
  loupe.value.style = {
    left: `${x - loupeSize / 2}px`,
    top: `${y - loupeSize / 2}px`,
    backgroundImage: `url(${fixImageUrl(photo.image)})`,
    backgroundSize: `${imgRect.width * zoomLevel}px ${imgRect.height * zoomLevel}px`,
    backgroundPosition: `${bgX}px ${bgY}px`
  }
}

// 打开智能搜索对话框
function openSmartSearchDialog() {
  smartSearchDialogVisible.value = true
  smartSearchInput.value = ''
}

// 提交智能搜索请求
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

// 转播对话框打开时的回调
function onCarouselDialogOpened() {
  batchCarouselRendered.value = true;
}

// 轮播对话框关闭时的回调
function onCarouselDialogClosed() {
  batchCarouselRendered.value = false;
  stopCarouselAutoplay();
}

let carouselAutoplayTimer = null

// 启动轮播自动播放
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

// 停止轮播自动播放
function stopCarouselAutoplay() {
  if (carouselAutoplayTimer) {
    clearInterval(carouselAutoplayTimer)
    carouselAutoplayTimer = null
  }
}

// 应用轮播切换间隔设置
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

// 处理轮播中的鼠标滚轮事件
function handleBatchCarouselWheel(e) {
  if (!batchCarouselVisible.value || !batchCarouselRef.value) return
  if (e.deltaY > 0) batchCarouselRef.value.next()
  if (e.deltaY < 0) batchCarouselRef.value.prev()
}

// 触摸滑动逻辑
let touchStartX = 0
let touchStartY = 0
let touchEndX = 0
let touchEndY = 0
let isSwiping = false

// 轮播触摸开始事件
function handleTouchStart(e) {
  if (!batchCarouselVisible.value) return
  touchStartX = e.touches[0].clientX
  touchStartY = e.touches[0].clientY
  touchEndX = touchStartX
  touchEndY = touchStartY
  isSwiping = false
}

// 轮播触摸移动事件
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

// 轮播触摸结束事件
function handleTouchEnd(e) {
  if (!batchCarouselVisible.value || !batchCarouselRef.value) return
  const deltaX = touchEndX - touchStartX
  const deltaY = touchEndY - touchStartY
  if (isSwiping && Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > 50) {
    if (deltaX > 0) batchCarouselRef.value.prev()
    else batchCarouselRef.value.next()
    e.preventDefault()
  }
  touchStartX = 0; touchStartY = 0; touchEndX = 0; touchEndY = 0; isSwiping = false
}

// 进入选择模式（用于轮播播放）
const selectMode = ref(false)
function enterSelectMode() {
  selectMode.value = true
  selectedPhotoIds.value = []
}

// 退出选择模式
function exitSelectMode() {
  selectMode.value = false
  selectedPhotoIds.value = []
}

// 切换照片选中状态
function toggleSelectPhoto(id) {
  const idx = selectedPhotoIds.value.indexOf(id)
  if (idx === -1) selectedPhotoIds.value.push(id)
  else selectedPhotoIds.value.splice(idx, 1)
}

// 确认选择并开始轮播
function confirmBatchSelect() {
  batchCarouselPhotos.value = photos.value.filter(p => selectedPhotoIds.value.includes(p.id))
  if (batchCarouselPhotos.value.length === 0) {
    ElMessage.warning('请至少选择一张图片')
    return
  }
  // 不立即设置 batchCarouselRendered，等待 dialog 动画完成
  batchCarouselRendered.value = false;
  batchCarouselVisible.value = true
  selectMode.value = false
}

// 进入批量编辑模式
function enterBatchEditMode() {
  batchEditMode.value.active = true
  batchSelectedPhotoIds.value = []
}

// 退出批量编辑模式
function exitBatchEditMode() {
  batchEditMode.value.active = false
  batchSelectedPhotoIds.value = []
}

// 切换批量编辑中的照片选中状态
function toggleBatchSelectPhoto(id) {
  const idx = batchSelectedPhotoIds.value.indexOf(id)
  if (idx === -1) batchSelectedPhotoIds.value.push(id)
  else batchSelectedPhotoIds.value.splice(idx, 1)
}

// 点击照片处理（根据当前模式决定行为）
function handlePhotoClick(photo, idx) {
  if (selectMode.value) {
    toggleSelectPhoto(photo.id)
  } else if (batchEditMode.value.active) {
    toggleBatchSelectPhoto(photo.id)
  } else {
    openPreview(idx)
  }
}

// 打开批量编辑标签对话框
function openBatchEditTagsDialog() {
  if (batchSelectedPhotoIds.value.length === 0) {
    ElMessage.warning('请先选择要编辑的图片')
    return
  }
  batchEditMode.value.mode = 'add'
  batchEditMode.value.tags = []
  batchEditTagsDialogVisible.value = true
}

// 为批量编辑创建新标签
async function createNewTagForBatchEdit() {
  try {
    const { value } = await ElMessageBox.prompt('请输入新的标签名', '新建标签', {
      confirmButtonText: '确定', cancelButtonText: '取消', inputPattern: /\S/, inputErrorMessage: '标签名不能为空'
    })
    if (value) {
      const token = sessionStorage.getItem('token')
      const res = await axios.post('/api/user_tags/', { tag: value }, { headers: { Authorization: `Token ${token}` } })
      ElMessage.success(res.data.msg || '标签创建成功')
      await fetchAllUserTags()
      if (!batchEditMode.value.tags.includes(value)) batchEditMode.value.tags.push(value)
    }
  } catch (error) {
    if (error !== 'cancel') ElMessage.error(error.response?.data?.error || '创建失败')
  }
}

// 确认批量编辑标签
async function confirmBatchEditTags() {
  if (batchSelectedPhotoIds.value.length === 0) {
    ElMessage.warning('请先选择要编辑的图片')
    return
  }
  if (batchEditMode.value.tags.length === 0) {
    ElMessage.warning('请选择至少一个标签')
    return
  }
  try {
    await ElMessageBox.confirm(`确定修改?`, '确认操作', { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' })
    batchEditLoading.value = true
    const token = sessionStorage.getItem('token')
    let successCount = 0
    for (const photoId of batchSelectedPhotoIds.value) {
      const photo = photos.value.find(p => p.id === photoId)
      if (!photo) continue
      let newTags = []
      if (batchEditMode.value.mode === 'add') newTags = [...new Set([...photo.tags, ...batchEditMode.value.tags])]
      else newTags = [...batchEditMode.value.tags]
      await axios.post('/api/update_photo_tags/', { photo_id: photoId, tags: newTags }, { headers: { Authorization: `Token ${token}` } })
      photo.tags = newTags
      successCount++
    }
    batchEditLoading.value = false
    batchEditTagsDialogVisible.value = false
    ElMessage.success(`成功修改 ${successCount} 张图片的标签`)
    exitBatchEditMode()
  } catch (error) {
    if (error !== 'cancel') batchEditLoading.value = false
  }
}

// 批量删除选中的照片
async function batchDelete() {
  if (batchSelectedPhotoIds.value.length === 0) {
    ElMessage.warning('请先选择要删除的图片')
    return
  }
  try {
    await ElMessageBox.confirm('确定删除?', '批量删除确认', { confirmButtonText: '确定删除', cancelButtonText: '取消', type: 'warning' })
    const token = sessionStorage.getItem('token')

    // 批量删除选中的图片
    let successCount = 0
    for (const photoId of batchSelectedPhotoIds.value) {
      try {
        await deletePhoto(photoId)
        successCount++
      } catch (error) {}
    }
    if (successCount > 0) {
      ElMessage.success(`成功删除 ${successCount} 张图片`)
      fetchPhotos()
    }
    exitBatchEditMode()
  } catch (error) {}
}


// 下载单张图片
async function downloadPhoto(photo) {
  try {
    const imageUrl = fixImageUrl(photo.image)
    const filename = photo.description ? `${photo.description}.jpg` : `photo_${photo.id}.jpg`
    const link = document.createElement('a')
    link.href = imageUrl
    link.download = filename
    link.target = '_blank'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    ElMessage.success('开始下载图片')
  } catch (error) {
    ElMessage.error('下载图片失败')
  }
}


// 批量下载选中的图片
async function batchDownload() {
  if (batchSelectedPhotoIds.value.length === 0) {
    ElMessage.warning('请先选择要下载的图片')
    return
  }
  try {
    await ElMessageBox.confirm(`确定下载?`, '批量下载确认', { confirmButtonText: '确定下载', cancelButtonText: '取消', type: 'info' })
    ElMessage.info('开始下载...')
    for (let i = 0; i < batchSelectedPhotoIds.value.length; i++) {
      const photoId = batchSelectedPhotoIds.value[i]
      const photo = photos.value.find(p => p.id === photoId)
      if (photo) {
        const imageUrl = fixImageUrl(photo.image)
        const filename = photo.description ? `${photo.description}_${photo.id}.jpg` : `photo_${photo.id}.jpg`
        const link = document.createElement('a')
        link.href = imageUrl
        link.download = filename
        link.target = '_blank'
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        if (i < batchSelectedPhotoIds.value.length - 1) await new Promise(resolve => setTimeout(resolve, 300))
      }
    }
    ElMessage.success('下载完成')
  } catch (error) {}
}


// 预览相关逻辑
let previewAutoplayTimer = null
// 应用预览切换间隔
function applyPreviewInterval() {
  previewInterval.value = previewIntervalTemp.value
  ElMessage.success(`已设置切换间隔为 ${previewIntervalTemp.value} 秒`)
}
// 打开图片预览弹窗
function openPreview(idx) {
  currentPreviewIndex.value = idx
  updatePreviewPhoto()
  previewDialogVisible.value = true
}
// 关闭图片预览弹窗
function closePreview() {
  previewDialogVisible.value = false
  stopPreviewAutoplay()
}
// 启动自动播放
function startPreviewAutoplay() {
  stopPreviewAutoplay()
  if (previewAutoplay.value && previewDialogVisible.value) {
    previewAutoplayTimer = setInterval(() => {
      if (currentPreviewIndex.value < photos.value.length - 1) showNext()
      else currentPreviewIndex.value = 0; updatePreviewPhoto()
    }, previewInterval.value * 1000)
  }
}
// 停止自动播放
function stopPreviewAutoplay() {
  if (previewAutoplayTimer) {
    clearInterval(previewAutoplayTimer)
    previewAutoplayTimer = null
  }
}
// 监听自动播放相关变量变化
watch(previewAutoplay, (newVal) => {
  if (newVal) previewIntervalTemp.value = previewInterval.value
})
watch([previewAutoplay, previewInterval], () => {
  if (previewAutoplay.value) startPreviewAutoplay()
  else stopPreviewAutoplay()
})
watch(previewDialogVisible, (newVal) => {
  if (!newVal) stopPreviewAutoplay()
})
// 显示上一张图片
function showPrev() {
  if (currentPreviewIndex.value > 0) { currentPreviewIndex.value--; updatePreviewPhoto() }
  else { currentPreviewIndex.value = photos.value.length - 1; updatePreviewPhoto(); ElMessage.info('已返回第一张') }
}
// 显示下一张图片
function showNext() {
  if (currentPreviewIndex.value < photos.value.length - 1) { currentPreviewIndex.value++; updatePreviewPhoto() }
  else { currentPreviewIndex.value = 0; updatePreviewPhoto(); ElMessage.info('已返回第一张') }
}
// 更新当前预览图片
function updatePreviewPhoto() {
  currentPreviewPhoto.value = photos.value[currentPreviewIndex.value] || null;
}
// 处理鼠标滚轮切换图片
function handleWheel(e) {
  if (!previewDialogVisible.value) return;
  if (e.deltaY > 0) showNext();
  if (e.deltaY < 0) showPrev();
}

// 预览触摸开始事件
let previewTouchStartX = 0; let previewTouchStartY = 0; let previewTouchEndX = 0; let previewTouchEndY = 0; let previewIsSwiping = false
function onTouchStart(e) {
  if (!previewDialogVisible.value) return
  previewTouchStartX = e.touches[0].clientX; previewTouchStartY = e.touches[0].clientY
  previewTouchEndX = previewTouchStartX; previewTouchEndY = previewTouchStartY
  previewIsSwiping = false
}

// 预览触摸移动事件
function onTouchMove(e) {
  if (!previewDialogVisible.value) return
  previewTouchEndX = e.touches[0].clientX; previewTouchEndY = e.touches[0].clientY
  const deltaX = previewTouchEndX - previewTouchStartX; const deltaY = previewTouchEndY - previewTouchStartY
  if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > 10) { previewIsSwiping = true; e.preventDefault() }
}

// 预览触摸结束事件
function onTouchEnd(e) {
  if (!previewDialogVisible.value) return
  const deltaX = previewTouchEndX - previewTouchStartX; const deltaY = previewTouchEndY - previewTouchStartY
  if (previewIsSwiping && Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > 50) {
    if (deltaX > 0) showPrev()
    else showNext()
    e.preventDefault()
  }
  previewTouchStartX = 0; previewTouchStartY = 0; previewTouchEndX = 0; previewTouchEndY = 0; previewIsSwiping = false
}

// 显示图片缩略图弹窗
function showThumb(photo) {
  if (photo.thumbnail) { currentThumb.value = photo.thumbnail; thumbDialogVisible.value = true }
  else ElMessage.warning('该图片无缩略图')
}
// 关闭图片编辑器
function handleCloseImageEditor() {
  if (imageEditorInstance.value) { imageEditorInstance.value.destroy(); imageEditorInstance.value = null }
  imageEditorVisible.value = false
}


// 打开图片编辑器
async function openImageEditor(photo) {
  currentEditingPhoto.value = photo;
  const fixedUrl = fixImageUrl(photo.image);
  imageEditorVisible.value = true;
  await nextTick();
  if (imageEditorInstance.value) { imageEditorInstance.value.destroy(); imageEditorInstance.value = null }
  const container = document.querySelector('#tui-image-editor-container');
  try {
    // 获取图片原始尺寸
    const img = new Image();
    img.src = fixedUrl;
    await new Promise((resolve) => {
      img.onload = resolve;
      img.onerror = resolve;
    });
    
    // 更严格的尺寸限制，确保完全在视野内且无滚动条
    const availableHeight = window.innerHeight - 250; 
    // 左右边距 buffer 100px
    const availableWidth = window.innerWidth - 100; 
    
    // 计算缩放比例
    const scaleW = availableWidth / img.width;
    const scaleH = availableHeight / img.height;
    // 保持 <= 1，不放大
    const scale = Math.min(scaleW, scaleH, 1); 
    
    const canvasWidth = Math.floor(img.width * scale);
    const canvasHeight = Math.floor(img.height * scale);
    
    imageEditorInstance.value = new ImageEditor(container, {
      includeUI: {
        loadImage: { path: fixedUrl, name: photo.description || 'image' },
        menu: ['crop', 'flip', 'rotate', 'filter', 'draw', 'text'],
        initMenu: 'filter',
        uiSize: {
          width: `${canvasWidth}px`,
          height: `${canvasHeight}px`,
        },
        menuBarPosition: 'bottom',
      },
      cssMaxWidth: canvasWidth,
      cssMaxHeight: canvasHeight,
      selectionStyle: { cornerSize: 20, rotatingPointOffset: 70, },
      usageStatistics: false,
    });
  } catch (error) {
    console.error('编辑器错误:', error);
    ElMessage.error('创建编辑器失败: ' + error.message);
  }
}


// 空函数占位，防止引用错误
async function initializeEditor() {}
// 启用鼠标滚轮缩放（预留）
function enableMouseWheelZoom() {}
// 修复缩放按钮（预留）
function fixZoomButtons() {}


// 保存图片编辑结果到服务器
async function saveEditedImage() {
  if (!imageEditorInstance.value || !currentEditingPhoto.value) { ElMessage.warning('没有可保存的内容'); return }
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
      headers: { 'Content-Type': 'multipart/form-data', 'Authorization': `Token ${token}` }
    });
    const index = photos.value.findIndex(p => p.id === currentEditingPhoto.value.id);
    if (index !== -1) photos.value[index].image = `${response.data.image}?t=${new Date().getTime()}`;
    ElMessage.success('图片更新成功！');
    handleCloseImageEditor();
  } catch (error) {
    ElMessage.error('图片保存失败');
  } finally {
    isSavingImage.value = false;
  }
}


// 打开图片信息编辑弹窗
function openEditDialog(photo) {
  editingPhoto.value = photo;
  editForm.value.description = photo.description || '';
  editForm.value.tags = [...(photo.tags || [])];
  editDialogVisible.value = true;
}


// 获取所有用户标签
async function fetchAllUserTags() {
  const token = sessionStorage.getItem('token');
  if (!token) return;
  try {
    const res = await axios.get('/api/user_tags/', { headers: { Authorization: `Token ${token}` } });
    allUserTags.value = res.data.tags || [];
  } catch (e) { console.error('获取标签失败', e) }
}


// 保存图片信息修改
async function savePhotoChanges() {
  if (!editingPhoto.value) return;
  editLoading.value = true;
  const token = sessionStorage.getItem('token');
  try {
    const url = `/api/photos/${editingPhoto.value.id}/update/`;
    const payload = { description: editForm.value.description, tags: editForm.value.tags };
    const res = await axios.patch(url, payload, { headers: { Authorization: `Token ${token}` } });
    const index = photos.value.findIndex(p => p.id === editingPhoto.value.id);
    if (index !== -1) {
      photos.value[index].description = res.data.description;
      photos.value[index].tags = res.data.tags;
    }
    ElMessage.success('更新成功');
    editDialogVisible.value = false;
  } catch (e) { ElMessage.error('更新失败'); } finally { editLoading.value = false; }
}


// 自定义分辨率输入时同步赋值
function onRatioCustomInput(val) { if (val) searchRatio.value = val }
// 自定义像素输入时同步赋值
function onMegapixelCustomInput(val) { if (val) searchMegapixel.value = val }
// 显示图片详细信息弹窗
function showInfo(photo) { currentPhoto.value = photo; infoDialogVisible.value = true }
// 修正图片 URL，去除多余前缀
function fixImageUrl(url) {
  if (!url) return '';
  let processedUrl = url;
  const prefixesToRemove = ['http://backend:8000', 'https://backend:8000', 'http://localhost:8000', 'https://localhost:8000', 'http://localhost:5173', 'https://localhost:5173'];
  for (const prefix of prefixesToRemove) { if (processedUrl.startsWith(prefix)) { processedUrl = processedUrl.replace(prefix, ''); break; } }
  const idx = processedUrl.indexOf('/media/');
  let relativePath = idx !== -1 ? processedUrl.slice(idx) : processedUrl;
  if (!relativePath.startsWith('/')) { relativePath = '/' + relativePath; }
  return relativePath;
}
// 格式化日期显示
function formatDate(dateStr) {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  return !isNaN(d) ? d.toLocaleString() : dateStr;
}
// 格式化拍摄日期
function formatTakenAt(takenAt) {
  if (!takenAt) return '';
  const d = new Date(takenAt);
  if (!isNaN(d)) return d.toLocaleString();
  return takenAt;
}
// 格式化 EXIF 日期
function formatExifDate(exifDate) {
  if (!exifDate) return '';
  return exifDate;
}


// 获取照片列表（可带筛选参数）
async function fetchPhotos(params = {}) {
  const token = sessionStorage.getItem('token')
  if (!token) { isLoading.value = false; return }
  isLoading.value = true 
  try {
    const query = Object.entries(params)
      .filter(([, value]) => value)
      .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
      .join('&');
    const url = `/api/photos/${query ? '?' + query : ''}`;
    const res = await axios.get(url, { headers: { Authorization: `Token ${token}` } })
    photos.value = res.data.photos || []
  } catch (e) {
    console.error('获取照片失败:', e);
    photos.value = []
  } finally {
    setTimeout(() => { isLoading.value = false }, 500); 
  }
}

// 格式化日期参数为 yyyy-mm-dd
function formatDateParam(dateObj) {
  if (!dateObj) return '';
  const yyyy = dateObj.getFullYear();
  const mm = (dateObj.getMonth() + 1).toString().padStart(2, '0');
  const dd = dateObj.getDate().toString().padStart(2, '0');
  return `${yyyy}-${mm}-${dd}`;
}
// 执行搜索，筛选照片
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
  if (resolutionType.value === 'size') params.resolution = searchResolution.value
  else if (resolutionType.value === 'ratio') params.ratio = searchRatio.value === 'custom' ? searchRatioCustom.value : searchRatio.value
  else if (resolutionType.value === 'megapixel') params.megapixel = searchMegapixel.value === 'custom' ? searchMegapixelCustom.value : searchMegapixel.value
  fetchPhotos(params)
}
// 重置搜索条件
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


// 删除单张图片
async function onDelete(photoId) {
  try {
    await ElMessageBox.confirm( '确定要删除这张图片吗？此操作不可撤销。', '警告', { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning', } );
    const token = sessionStorage.getItem('token');
    if (!token) return;
    await deletePhoto(photoId, token);
    photos.value = photos.value.filter(p => p.id !== photoId);
    ElMessage.success('删除成功');
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('删除失败');
  }
}


// 组件挂载时初始化数据和主题
onMounted(() => {
    fetchPhotos();
    fetchAllUserTags();
    window.addEventListener('wheel', handleWheel);

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    isDark.value = mediaQuery.matches
    updateThemeAttribute()
    mediaQuery.addEventListener('change', handleSystemThemeChange)
});

// 组件卸载时移除监听
onUnmounted(() => {
  window.removeEventListener('wheel', handleWheel);
  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
  mediaQuery.removeEventListener('change', handleSystemThemeChange)
});

</script>


<style>
/* --- CSS 变量定义 (支持双色系统) --- */
:root {
  /* 通用/Light Mode 变量 */
  --handwriting-font: 'Caveat', cursive;
  
  /* 浅色系 (默认) */
  --paper-bg: #fdfaf4;
  --paper-lines: #ede8e0;
  --pencil-text: #4a4a4a;
  --spine-color: #58493a;
  --spine-shadow: rgba(0,0,0,0.5);
  --washi-tape-bg: rgba(255, 248, 220, 0.7);
  --table-bg: #d3c7b1;
  --card-bg: #fff;
  --card-bg-transparent: rgba(255, 255, 255, 0.7);
  --card-shadow: 3px 3px 8px rgba(0,0,0,0.1);
  --card-hover-shadow: 5px 5px 15px rgba(0,0,0,0.15);
  --border-color: #ccc;
  --border-dashed: #ccc;
  
  /* 输入框/控件 */
  --input-bg: #fff;
  --input-border-bottom: var(--paper-lines);
  --button-bg-alt: #f0f0f0;
  --button-text-alt: var(--pencil-text);

  /* 模拟纸张纹理和横线 (Light) */
  --paper-background-lines: repeating-linear-gradient(
      var(--paper-bg), 
      var(--paper-bg) 23px, 
      var(--paper-lines) 24px
  );
}

/* Dark Mode 变量覆盖 */
[data-theme='dark'] {
  --paper-bg: #2c2c2c;
  --paper-lines: #3d3d3d;
  --pencil-text: #e0e0e0;
  --spine-color: #1a120b;
  --spine-shadow: rgba(0,0,0,0.8);
  --washi-tape-bg: rgba(255, 255, 255, 0.15);
  --table-bg: #1a1a1a;
  --card-bg: #383838;
  --card-bg-transparent: rgba(56, 56, 56, 0.85);
  --card-shadow: 4px 4px 10px rgba(0,0,0,0.5);
  --card-hover-shadow: 6px 6px 18px rgba(0,0,0,0.6);
  --border-color: #444;
  --border-dashed: #555;

  --input-bg: rgba(255,255,255,0.05);
  --input-border-bottom: #555;
  --button-bg-alt: #444;
  --button-text-alt: #ccc;

  --paper-background-lines: repeating-linear-gradient(
      var(--paper-bg), 
      var(--paper-bg) 23px, 
      var(--paper-lines) 24px
  );
}

/* 解决 teleport 到 body 的弹窗无法获取 CSS 变量的问题 */
body.dark-theme {
  --paper-bg: #2c2c2c;
  --paper-lines: #3d3d3d;
  --pencil-text: #e0e0e0;
  --border-color: #444;
}

/* --- Global Dark Mode Fixes for Teleported Elements (所有弹窗强制暗色) --- */
body.dark-theme .el-message-box,
body.dark-theme .el-popover,
body.dark-theme .el-picker-panel,
body.dark-theme .el-select-dropdown,
body.dark-theme .el-dialog {
  background-color: #2c2c2c !important;
  border-color: #444 !important;
}

/* 标题和内容文字 */
body.dark-theme .el-message-box__title,
body.dark-theme .el-message-box__content,
body.dark-theme .el-popover__title,
body.dark-theme .el-picker-panel__icon-btn,
body.dark-theme .el-date-picker__header-label,
body.dark-theme .el-dialog__title,
body.dark-theme .el-dialog__body {
  color: #e0e0e0 !important;
}

/* 下拉菜单和日期选择器里的文字 */
body.dark-theme .el-select-dropdown__item,
body.dark-theme .el-date-table th,
body.dark-theme .el-date-table td.available,
body.dark-theme .el-picker-panel__content,
body.dark-theme .el-month-table td .cell,
body.dark-theme .el-year-table td .cell {
  color: #e0e0e0 !important;
}

/* 悬停高亮背景 */
body.dark-theme .el-select-dropdown__item.hover,
body.dark-theme .el-select-dropdown__item:hover,
body.dark-theme .el-date-table td.available:hover {
  background-color: #3a3a3a !important;
}

/* 弹窗内的输入框背景 */
body.dark-theme .el-message-box .el-input__wrapper,
body.dark-theme .el-message-box .el-textarea__inner {
  background-color: #1a1a1a !important;
  box-shadow: 0 0 0 1px #444 inset !important;
  color: #e0e0e0 !important;
}

/* 关闭按钮颜色 */
body.dark-theme .el-message-box__headerbtn .el-message-box__close,
body.dark-theme .el-dialog__headerbtn .el-dialog__close {
  color: #a0a0a0 !important;
}
body.dark-theme .el-message-box__headerbtn:hover .el-message-box__close,
body.dark-theme .el-dialog__headerbtn:hover .el-dialog__close {
  color: #fff !important;
}


/* 全局过渡动画 */
body, .sketchbook-wrapper, .sketchbook-container, .sketchbook-page, 
.photo-card, .photo-info, .sketch-button, .el-dialog, .el-input__wrapper {
  transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
}

/* --- 弹窗 (Dialog) 拟物化 --- */
.sketch-dialog:not(.carousel-fullscreen-dialog):not(.editor-dialog) .el-dialog {
  background: var(--paper-bg) !important;
  border: 1px solid var(--border-color);
  box-shadow: 5px 5px 15px rgba(0,0,0,0.3);
  border-radius: 2px !important;
}
.sketch-dialog .el-dialog__title {
  font-family: var(--handwriting-font);
  font-size: 2.5rem;
  color: var(--pencil-text);
}
[data-theme='dark'] .sketch-dialog .el-dialog__title {
  color: #e0e0e0 !important;
}
/* 强制覆盖普通弹窗 Body 背景和文字颜色 */
.sketch-dialog:not(.carousel-fullscreen-dialog):not(.editor-dialog) .el-dialog__body {
  background: repeating-linear-gradient(
    var(--paper-bg), 
    var(--paper-bg) 23px, 
    var(--paper-lines) 24px
  ) !important;
  color: var(--pencil-text) !important;
}
[data-theme='dark'] .sketch-dialog:not(.carousel-fullscreen-dialog):not(.editor-dialog) .el-dialog__body {
  background: repeating-linear-gradient(
    #2c2c2c, 
    #2c2c2c 23px, 
    #3a3a3a 24px
  ) !important;
  color: #e0e0e0 !important;
}

/* 专门修复 info-list 的文字颜色 */
.photo-info-list ul {
  padding-left: 0;
  list-style: none;
  font-family: var(--handwriting-font);
  font-size: 1.4rem;
  color: var(--pencil-text) !important; /* 强制使用变量颜色 */
}

[data-theme='dark'] .photo-info-list ul {
  color: #e0e0e0 !important;
}

/* 暗色主题下弹窗内的输入框和选择器 */
[data-theme='dark'] .sketch-dialog .el-input__wrapper {
  background-color: #2c2c2c !important;
  box-shadow: 0 0 0 1px #555 inset !important;
}
[data-theme='dark'] .sketch-dialog .el-input__inner {
  color: #e0e0e0 !important;
}
[data-theme='dark'] .sketch-dialog .el-textarea__inner {
  background-color: #2c2c2c !important;
  color: #e0e0e0 !important;
  border-color: #555 !important;
}
[data-theme='dark'] .sketch-dialog .el-select {
  --el-select-input-focus-border-color: #409eff;
}
[data-theme='dark'] .sketch-dialog .el-tag {
  background-color: #3a3a3a !important;
  color: #e0e0e0 !important;
  border-color: #555 !important;
}
[data-theme='dark'] .sketch-dialog .el-form-item__label {
  color: #c0c0c0 !important;
}
.photo-info-list li {
  margin-bottom: 12px;
  line-height: 1.4;
}

/* 通用全屏样式 (轮播 + 预览 + 编辑器) */
.carousel-fullscreen-dialog, 
.photo-preview-dialog,
.editor-dialog {
  overflow: hidden !important;
}

.carousel-fullscreen-dialog .el-dialog,
.photo-preview-dialog .el-dialog,
.editor-dialog .el-dialog {
  margin: 0 !important;
  padding: 0 !important;
  width: 100vw !important;
  height: 100vh !important;
  border-radius: 0 !important;
  background: transparent !important;
  box-shadow: none !important;
  border: none !important;
  display: flex;
  flex-direction: column;
}

.carousel-fullscreen-dialog .el-dialog__header,
.photo-preview-dialog .el-dialog__header,
.editor-dialog .el-dialog__header {
  display: none !important; /* 隐藏默认头部 */
}

.carousel-fullscreen-dialog .el-dialog__body,
.photo-preview-dialog .el-dialog__body,
.editor-dialog .el-dialog__body {
  padding: 0 !important;
  margin: 0 !important;
  flex: 1;
  height: 100vh !important; /* 强制高度 */
  overflow: hidden !important; /* 强制隐藏滚动条 */
  position: relative;
}

/* 轮播 & 预览特定背景 (深色) */
.carousel-fullscreen-dialog .el-dialog__body,
.photo-preview-dialog .el-dialog__body {
  background: rgba(0, 0, 0, 0.95) !important;
}

/* P.S. 编辑器特定背景 (浅色或主题色) */
.editor-dialog .el-dialog__body {
  background: #2b2b2b !important; /* 编辑器使用深灰背景更专业 */
  display: flex;
  flex-direction: column;
}

/* --- 编辑器自定义样式 --- */
.editor-top-bar {
  height: 50px;
  background: #1e1e1e;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  border-bottom: 1px solid #444;
  z-index: 200;
}
.editor-title {
  color: #fff;
  font-family: var(--handwriting-font);
  font-size: 1.5rem;
  font-weight: bold;
}
.editor-actions {
  display: flex;
  gap: 10px;
}
#tui-image-editor-container {
  width: 100% !important;
  flex: 1 !important; /* 占满剩余高度 */
  height: calc(100vh - 50px) !important; 
}
/* 隐藏 TUI Editor 默认的 Logo 或不需要的部分 */
.tui-image-editor-header-logo { display: none !important; }


/* 顶部悬浮控制栏 */
.fullscreen-top-bar {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  padding: 16px;
  background: linear-gradient(to bottom, rgba(0,0,0,0.8), transparent);
  z-index: 2002;
  display: flex;
  justify-content: center;
}
.top-bar-content {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  padding: 8px 20px;
  border-radius: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}
.top-bar-right {
  display: flex;
  gap: 8px;
  margin-left: 16px;
  padding-left: 16px;
  border-left: 1px solid rgba(255,255,255,0.2);
}

/* 全屏轮播内容样式 */
.carousel-wrapper-fullscreen {
  width: 100%;
  height: 100vh; /* 强制 100vh */
  position: relative;
  /* 移除 flex center，改用绝对定位居中图片 */
}
.carousel-item-fullscreen {
  width: 100%;
  height: 100%;
  position: relative; /* 确保子元素绝对定位相对于它 */
}
/* 强制绝对定位居中，避免父容器高度塌陷问题 */
.carousel-img-fullscreen {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  max-width: 100%;
  max-height: 100%;
  width: auto;
  height: auto;
  object-fit: contain;
  transition: transform 0.3s;
  display: block; 
}

/* --- 单图预览自定义导航按钮样式 --- */
.preview-nav-btn {
  position: fixed;
  top: 50%;
  transform: translateY(-50%);
  width: 60px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 9999; /* 提高层级 */
  transition: all 0.3s ease;
  font-size: 32px;
  border-radius: 4px;
}
.preview-nav-btn.prev-btn {
  left: 0 !important; /* 强制贴边 */
  background-color: #409eff; /* 蓝色 */
  color: white;
  border-top-right-radius: 8px;
  border-bottom-right-radius: 8px;
}
.preview-nav-btn.next-btn {
  right: 0 !important; /* 强制贴边 */
  background-color: #409eff; /* 蓝色 */
  color: white;
  border-top-left-radius: 8px;
  border-bottom-left-radius: 8px;
}

/* UI隐藏时的透明交互逻辑 */
.preview-nav-btn.ui-hidden {
  opacity: 0;
  background-color: transparent;
  color: transparent;
}
.preview-nav-btn.ui-hidden:hover {
  opacity: 1;
  background-color: rgba(64, 158, 255, 0.5); /* 半透明蓝 */
  color: white;
}

/* --- 批量轮播 Element UI 箭头覆盖样式 --- */
/* 当容器没有 ui-hidden-mode 类时（UI显示） */
.carousel-wrapper-fullscreen:not(.ui-hidden-mode) .el-carousel__arrow {
  position: fixed !important;
  top: 50% !important;
  transform: translateY(-50%) !important;
  background-color: #409eff !important;
  color: white !important;
  opacity: 1 !important;
  border-radius: 4px !important;
  width: 60px !important;
  height: 80px !important;
  font-size: 24px !important;
  z-index: 9999 !important;
}
.carousel-wrapper-fullscreen:not(.ui-hidden-mode) .el-carousel__arrow--left {
  left: 0 !important; /* 强制贴边 */
  border-top-right-radius: 8px !important;
  border-bottom-right-radius: 8px !important;
  border-top-left-radius: 0 !important;
  border-bottom-left-radius: 0 !important;
}
.carousel-wrapper-fullscreen:not(.ui-hidden-mode) .el-carousel__arrow--right {
  right: 0 !important; /* 强制贴边 */
  border-top-left-radius: 8px !important;
  border-bottom-left-radius: 8px !important;
  border-top-right-radius: 0 !important;
  border-bottom-right-radius: 0 !important;
}

/* 当容器有 ui-hidden-mode 类时（UI隐藏） */
.carousel-wrapper-fullscreen.ui-hidden-mode .el-carousel__arrow {
  position: fixed !important;
  top: 50% !important;
  transform: translateY(-50%) !important;
  background-color: transparent !important;
  color: transparent !important;
  opacity: 0 !important;
  border-radius: 0 !important;
  width: 80px !important; /* 加大触控区域 */
  height: 120px !important;
  transition: all 0.3s ease !important;
  z-index: 9999 !important;
}
.carousel-wrapper-fullscreen.ui-hidden-mode .el-carousel__arrow:hover {
  background-color: rgba(64, 158, 255, 0.5) !important;
  color: white !important;
  opacity: 1 !important;
}
.carousel-wrapper-fullscreen.ui-hidden-mode .el-carousel__arrow--left {
  left: 0 !important;
}
.carousel-wrapper-fullscreen.ui-hidden-mode .el-carousel__arrow--right {
  right: 0 !important;
}

/* 底部信息悬浮层 */
.carousel-info-overlay,
.photo-preview-info-overlay {
  position: fixed;
  bottom: 40px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(20, 20, 20, 0.85);
  backdrop-filter: blur(12px);
  padding: 16px 24px;
  border-radius: 12px;
  color: #fff;
  text-align: center;
  font-family: var(--handwriting-font);
  max-width: 80%;
  z-index: 2002;
  box-shadow: 0 4px 20px rgba(0,0,0,0.4);
  border: 1px solid rgba(255,255,255,0.1);
  transition: all 0.3s ease;
}
.carousel-info-overlay h4, .photo-preview-info-overlay h3 {
  margin: 0 0 8px 0;
  font-size: 1.6rem;
  color: #fff;
}
.carousel-info-overlay p, .info-meta-row {
  margin: 0;
  font-size: 1.1rem;
  opacity: 0.9;
  color: #ddd;
}

/* 单图预览容器 */
.photo-preview-wrapper {
  width: 100%;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}
.photo-preview-img-fullscreen {
  max-width: 100%;
  max-height: 100%;
  width: auto;
  height: auto;
  object-fit: contain;
  z-index: 1000;
  display: block;
}
.info-actions {
  margin-top: 12px;
  display: flex;
  gap: 16px;
  justify-content: center;
}

/* 悬浮唤醒按钮 */
.floating-show-ui-btn {
  position: fixed;
  top: 20px;
  right: 20px;
  width: 40px;
  height: 40px;
  background: rgba(255,255,255,0.15);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #fff;
  z-index: 2005;
  backdrop-filter: blur(5px);
  border: 1px solid rgba(255,255,255,0.2);
  transition: all 0.3s;
}
.floating-show-ui-btn:hover {
  background: rgba(255,255,255,0.3);
  transform: scale(1.1);
}

/* 动画 */
.slide-down-enter-active, .slide-down-leave-active,
.slide-up-enter-active, .slide-up-leave-active,
.fade-enter-active, .fade-leave-active {
  transition: all 0.3s ease;
}
.slide-down-enter-from, .slide-down-leave-to {
  transform: translateY(-100%);
  opacity: 0;
}
.slide-up-enter-from, .slide-up-leave-to {
  transform: translate(-50%, 100%); /* 保持居中并向下移动 */
  opacity: 0;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
  transform: scale(0.8);
}

.action-button-group {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  margin-bottom: 8px;
  align-items: center;
}
.sketch-sticker-button {
  font-family: var(--handwriting-font) !important;
  font-size: 1.2rem !important;
  font-weight: 700 !important;
  background: transparent !important;
  border-width: 2px !important;
  border-style: solid !important;
  border-radius: 255px 15px 225px 15px / 15px 225px 15px 255px !important;
  padding: 8px 20px !important;
  box-shadow: none !important;
  transition: all 0.3s ease !important;
  transform: rotate(0deg);
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
.sketch-sticker-button:hover {
  color: #fff !important;
  transform: translateY(-3px) scale(1.02) !important;
}
/* disabled 状态样式 */
.sketch-sticker-button.is-disabled {
  border-color: #ccc !important;
  color: #ccc !important;
  background: transparent !important;
  cursor: not-allowed;
  transform: none !important;
  box-shadow: none !important;
}

.btn-green { border-color: #70a472 !important; color: #70a472 !important; --hover-bg: #70a472; }
.btn-green:hover { background: var(--hover-bg) !important; box-shadow: 3px 3px 0 #4e7a50 !important; }
.btn-blue { border-color: #6c94b8 !important; color: #6c94b8 !important; --hover-bg: #6c94b8; }
.btn-blue:hover { background: var(--hover-bg) !important; box-shadow: 3px 3px 0 #4a6b8a !important; }
.btn-orange { border-color: #d68c6d !important; color: #d68c6d !important; --hover-bg: #d68c6d; }
.btn-orange:hover { background: var(--hover-bg) !important; box-shadow: 3px 3px 0 #a6654a !important; }
.btn-lime { border-color: #a8a878 !important; color: #a8a878 !important; --hover-bg: #a8a878; }
.btn-lime:hover { background: var(--hover-bg) !important; box-shadow: 3px 3px 0 #7a7a50 !important; }
.btn-gray { border-color: #888888 !important; color: #888888 !important; --hover-bg: #888888; }
.btn-gray:hover { background: var(--hover-bg) !important; box-shadow: 3px 3px 0 #555 !important; }
.btn-red { border-color: #F56C6C !important; color: #F56C6C !important; --hover-bg: #F56C6C; }
.btn-red:hover { background: var(--hover-bg) !important; box-shadow: 3px 3px 0 #c04b4b !important; }

[data-theme='dark'] .btn-green { border-color: #8bc34a !important; color: #8bc34a !important; --hover-bg: #8bc34a; }
[data-theme='dark'] .btn-blue { border-color: #409eff !important; color: #409eff !important; --hover-bg: #409eff; }
[data-theme='dark'] .btn-orange { border-color: #e6a23c !important; color: #e6a23c !important; --hover-bg: #e6a23c; }
[data-theme='dark'] .btn-lime { border-color: #d4d4aa !important; color: #d4d4aa !important; --hover-bg: #d4d4aa; }
[data-theme='dark'] .btn-gray { border-color: #a6a9ad !important; color: #a6a9ad !important; --hover-bg: #a6a9ad; }
[data-theme='dark'] .btn-red { border-color: #f89898 !important; color: #f89898 !important; --hover-bg: #f89898; }


.sketch-radio-group :deep(.el-radio-button__inner) {
  background: transparent !important;
  border: 1px dashed var(--border-color) !important;
  border-radius: 4px !important;
  box-shadow: none !important;
  margin-right: 6px;
  color: var(--pencil-text) !important;
  font-family: var(--handwriting-font);
  font-size: 1rem;
  padding: 6px 12px;
  transition: all 0.2s;
}
.sketch-radio-group :deep(.el-radio-button:first-child .el-radio-button__inner),
.sketch-radio-group :deep(.el-radio-button:last-child .el-radio-button__inner) {
  border-radius: 4px !important;
}
.sketch-radio-group :deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
  background: var(--pencil-text) !important;
  color: var(--paper-bg) !important;
  border-color: var(--pencil-text) !important;
  box-shadow: none !important;
  transform: scale(1.05);
}

.carousel-loading {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  width: 100%;
}

.instructions-dialog {
  max-width: 95vw;
}
.instructions-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 32px;
}
@media (max-width: 768px) {
  .instructions-grid {
    grid-template-columns: 1fr;
  }
}
.instructions-content h4 { margin-top: 16px; margin-bottom: 8px; padding-bottom: 4px; border-bottom: 1px solid var(--border-color); color: var(--pencil-text); }
/* 移除列表第一列的标题顶部margin，以对齐 */
.inst-col h4:first-child { margin-top: 0; }
.instructions-content ul { padding-left: 20px; list-style-type: disc; color: var(--pencil-text); }
.instructions-content li { margin-bottom: 8px; }
[data-theme='dark'] .instructions-content h4 { color: #e0e0e0; border-bottom-color: #555; }
[data-theme='dark'] .instructions-content ul { color: #c0c0c0; }
[data-theme='dark'] .instructions-content li { color: #c0c0c0; }
[data-theme='dark'] .instructions-content b { color: #fff; }
</style>

<style scoped>
.page-header-row {
  display: flex; align-items: center; margin-bottom: 0px;
}
.page-title {
  font-family: var(--handwriting-font); font-size: 1.8rem; color: var(--pencil-text); margin: 0; margin-right: 12px;
}
.sketch-switch { margin-left: 8px; transform: scale(1.1); }
.sketch-loader-wrapper {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  width: 100%; height: 100vh;
  background: var(--paper-bg);
  transition: background-color 0.3s;
  z-index: 9999; position: fixed; top: 0; left: 0;
}
.sketch-loader-content { display: flex; flex-direction: column; align-items: center; gap: 16px; }
.loader-icon-box {
  width: 60px; height: 60px; border-radius: 50%;
  border: 2px dashed var(--pencil-text);
  display: flex; align-items: center; justify-content: center;
  animation: rotate 8s linear infinite;
}
.loader-icon { font-size: 30px; color: var(--pencil-text); }
@keyframes rotate { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
.loader-text {
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  font-size: 1.2rem; font-weight: 500; color: var(--pencil-text); margin: 0; display: flex; align-items: baseline; letter-spacing: 1px;
}
.loader-dots { display: inline-flex; margin-left: 4px; }
.loader-dots .dot {
  display: inline-block; margin: 0 2px; font-weight: bold;
  animation: bounce 1.4s infinite ease-in-out both;
  animation-delay: calc(var(--i) * 0.2s);
}
@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); opacity: 0.5; }
  40% { transform: scale(1.2); opacity: 1; }
}
.sketchbook-wrapper {
  width: 100%; height: calc(100vh - 60px); background: var(--table-bg); padding: 20px 0; overflow: hidden; display: flex; align-items: center; justify-content: center;
}
.sketchbook-container {
  display: flex; width: 95vw; max-width: 1800px; height: calc(100vh - 100px); background: var(--paper-bg); box-shadow: 0 10px 30px rgba(0,0,0,0.4); border: 1px solid var(--border-color); border-radius: 2px; overflow: hidden;
}
.sketchbook-spine {
  width: 24px; background: linear-gradient(to right, var(--spine-color) 0%, var(--spine-color) 40%, #3a3a3a 50%, var(--spine-color) 60%, var(--spine-color) 100%); box-shadow: inset 0 0 10px var(--spine-shadow); z-index: 5;
}
.sketchbook-page { padding: 24px; position: relative; }
.page-left { flex: 0 0 280px; background: var(--paper-bg); border-right: 1px dashed var(--border-dashed); overflow-y: auto; height: 100%; }
.page-subtitle {
  font-family: var(--handwriting-font); font-size: 0.8rem; color: #888; margin-top: 0; margin-bottom: 16px; border-bottom: 1px solid var(--paper-lines); padding-bottom: 8px;
}
.page-right { flex: 1; background: var(--paper-background-lines); overflow-y: auto; height: 100%; }
.page-right-content { padding: 10px; min-height: 100%; }
.control-bar { margin-bottom: 24px; display: flex; gap: 12px; align-items: center; flex-wrap: wrap; padding-bottom: 16px; border-bottom: 2px dashed var(--paper-lines); }
.photo-grid { display: grid; grid-template-columns: repeat(v-bind(photosPerRow), 1fr); gap: 24px; }
.photo-card {
  position: relative; background: var(--card-bg); border: 1px solid var(--border-color); box-shadow: var(--card-shadow); padding: 10px; padding-bottom: 15px; transition: transform 0.2s, box-shadow 0.2s; transform: rotate(-0.5deg);
}
.photo-card:nth-child(2n) { transform: rotate(0.8deg); }
.photo-card:nth-child(3n) { transform: rotate(-0.3deg); }
.photo-card:nth-child(4n) { transform: rotate(0.6deg); }
.photo-card:hover { transform: scale(1.03) rotate(0deg) !important; box-shadow: var(--card-hover-shadow); z-index: 5; }
.washi-tape {
  content: ''; position: absolute; top: -10px; left: 50%; transform: translateX(-50%) rotate(1deg); width: 120px; height: 25px; background: var(--washi-tape-bg); box-shadow: 0 1px 1px rgba(0,0,0,0.1); border-left: 2px dashed rgba(255, 255, 255, 0.3); border-right: 2px dashed rgba(255, 255, 255, 0.3); z-index: 2; opacity: 0.8; pointer-events: none; backdrop-filter: blur(1px);
}
.photo-card:nth-child(2n) .washi-tape { transform: translateX(-50%) rotate(-1.5deg); }
.photo-card:nth-child(3n) .washi-tape { width: 100px; }
.photo-container { position: relative; overflow: hidden; background: #f0f0f0; border: 1px solid rgba(0,0,0,0.05); }
.photo-img { width: 100%; height: 200px; object-fit: cover; cursor: pointer; display: block; transition: filter 0.2s; }
.photo-card:hover .photo-img { filter: brightness(1.05); }
.magnifying-loupe {
  position: absolute; width: 150px; height: 150px; border-radius: 50%; border: 4px solid var(--card-bg); box-shadow: 0 0 10px rgba(0,0,0,0.3), inset 0 0 5px rgba(0,0,0,0.1); pointer-events: none; background-repeat: no-repeat; z-index: 10; backdrop-filter: blur(1px);
}
.photo-info { margin-top: 12px; padding: 0 5px; text-align: left; }
.photo-title { font-family: var(--handwriting-font); font-size: 1.6rem; font-weight: 700; color: var(--pencil-text); display: block; line-height: 1.2; }
.photo-meta { font-family: var(--handwriting-font); font-size: 1.1rem; color: #777; }
.photo-actions { margin-top: 12px; text-align: right; display: flex; gap: 4px; justify-content: flex-end; flex-wrap: wrap; }
.photo-actions .el-button { font-family: var(--handwriting-font); font-size: 1.1rem; font-weight: 700; color: #666; padding: 4px 8px; }
[data-theme='dark'] .photo-meta { color: #bbb; }
[data-theme='dark'] .photo-actions .el-button { color: #ddd; font-weight: 600; }
.photo-actions .el-button:hover { color: #007aff; background: rgba(0, 122, 255, 0.05); }
[data-theme='dark'] .photo-actions .el-button:hover { color: #409eff; background: rgba(64, 158, 255, 0.15); }
.photo-select-check, .photo-batch-check {
  position: absolute; left: 10px; top: 10px; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; z-index: 3; cursor: pointer; border: 2px solid #fff; transition: all 0.3s;
}
.photo-select-check { background: rgba(0,0,0,0.25); }
.photo-batch-check { background: rgba(64, 158, 255, 0.3); border-color: #409eff; }
.photo-batch-check:hover { background: rgba(64, 158, 255, 0.5); transform: scale(1.1); }
.photo-check-mark { color: #fff; font-size: 20px; font-weight: bold; text-shadow: 0 1px 2px rgba(0,0,0,0.5); }
.carousel-info {
  font-family: var(--handwriting-font); color: var(--pencil-text); margin-top: 16px; text-align: center; background: var(--card-bg-transparent); padding: 10px 20px; border-radius: 4px;
}
.carousel-info h4 { font-size: 1.8rem; margin: 5px 0; }
.carousel-info p { font-size: 1.2rem; margin: 5px 0; }
.photo-info-list ul { padding-left: 0; list-style: none; font-family: var(--handwriting-font); font-size: 1.4rem; color: var(--pencil-text); }
.photo-info-list li { margin-bottom: 12px; line-height: 1.4; }
.dialog-footer { display: flex; justify-content: space-between; align-items: center; width: 100%; }
</style>