<template>
  <div class="content flex flex-col h-full">
    <!-- 信息栏 -->
    <InfoBar 
      :directoryPath="directoryPath"
      :showAllPhotos="showAllPhotos"
      :showFavorites="showFavorites"
      :imageCount="totalCount"
      @refresh="loadImages"
    />
    
    <!-- 工具栏 -->
    <PhotoToolbar 
      v-model:thumbnailSize="thumbnailSize"
      v-model:ratingFilter="ratingFilter"
      @ratingChange="applyRatingFilter"
    />

    <!-- 照片网格 -->
    <PhotoGridView 
      ref="photoGridViewRef"
      :directoryPath="directoryPath"
      :showAllPhotos="showAllPhotos"
      :showFavorites="showFavorites"
      :thumbnailSize="thumbnailSize"
      :ratingFilter="ratingFilter"
      :loading="loading"
      :error="error"
      :images="images"
      :totalCount="totalCount"
      :hasMore="hasMore"
      :isLoadingMore="isLoadingMore"
      :debugMode="debugMode"
      @select-image="selectImage"
      @toggle-favorite="toggleFavorite"
      @load-more="loadMoreImages"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import PhotoToolbar from './PhotoGrid/PhotoToolbar.vue'
import PhotoGridView from './PhotoGrid/PhotoGridView.vue'
import InfoBar from './PhotoGrid/InfoBar.vue'
import { API_URLS } from '../config/api'

const props = defineProps({
  directoryPath: {
    type: String,
    default: ''
  },
  showAllPhotos: {
    type: Boolean,
    default: false
  },
  showFavorites: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['select-image'])

// 状态管理
const images = ref([])
const loading = ref(false)
const error = ref(null)
const thumbnailSize = ref(80)
const ratingFilter = ref(0)
const totalCount = ref(0)
const currentOffset = ref(0)
const pageSize = 50
const hasMore = ref(true)
const isLoadingMore = ref(false)
const debugMode = ref(false)

// 组件引用
const photoGridViewRef = ref(null)

// 加载图片
const loadImages = async (loadMore = false) => {
  if (!loadMore) {
    images.value = []
    currentOffset.value = 0
    hasMore.value = true
  }
  
  loading.value = !loadMore
  isLoadingMore.value = loadMore
  error.value = null

  try {
    let result
    
    if (props.showFavorites) {
      result = await window.pywebview.api.get_favorite_images()
      if (result.images) {
        result.total = result.images.length
        // 应用评分筛选
        if (ratingFilter.value > 0) {
          result.images = result.images.filter(img => img.rating >= ratingFilter.value)
        }
        // 应用分页
        result.images = result.images.slice(currentOffset.value, currentOffset.value + pageSize)
      }
    } else if (props.showAllPhotos) {
      result = await window.pywebview.api.get_all_images(pageSize, currentOffset.value)
    } else if (props.directoryPath) {
      result = await window.pywebview.api.get_images_in_directory(props.directoryPath, pageSize, currentOffset.value)
    } else {
      return
    }

    if (result && Array.isArray(result.images)) {
      // 按修改时间排序
      const sortedImages = result.images.sort((a, b) => {
        return new Date(b.modified_at || 0) - new Date(a.modified_at || 0)
      })
      
      if (loadMore) {
        images.value.push(...sortedImages)
      } else {
        images.value = sortedImages
      }
      
      totalCount.value = result.total || sortedImages.length
      currentOffset.value += sortedImages.length
      hasMore.value = currentOffset.value < totalCount.value
    } else {
      throw new Error('获取图片数据失败')
    }
  } catch (err) {
    console.error('加载图片失败:', err)
    error.value = err.message || '加载图片失败'
  } finally {
    loading.value = false
    isLoadingMore.value = false
  }
}

// 加载更多图片
const loadMoreImages = () => {
  if (hasMore.value && !isLoadingMore.value) {
    loadImages(true)
  }
}

// 选择图片
const selectImage = (image) => {
  emit('select-image', image)
}

// 切换收藏状态
const toggleFavorite = async (image) => {
  try {
    const imageId = image.id
    if (!imageId) {
      console.error('图片ID不存在')
      return
    }
    
    const newFavoriteStatus = !image.is_favorite
    const result = await window.pywebview.api.toggle_image_favorite(imageId)
    
    if (result.success) {
      // 更新本地状态
      const index = images.value.findIndex(img => 
        (img.id && img.id === image.id) || 
        (img.path && img.path === image.path)
      )
      if (index !== -1) {
        images.value[index].is_favorite = newFavoriteStatus
      }
      
      // 如果在收藏夹模式下，移除已取消收藏的图片
      if (props.showFavorites && !newFavoriteStatus) {
        images.value.splice(index, 1)
        totalCount.value--
      }
      
      // 通知父组件更新照片计数
      emit('image-count-changed')
    } else {
      console.error('更新收藏状态失败:', result.error)
    }
  } catch (err) {
    console.error('更新收藏状态失败:', err)
  }
}

// 应用评分筛选
const applyRatingFilter = () => {
  loadImages()
}

// 清除评分筛选
const clearRatingFilter = () => {
  ratingFilter.value = 0
  loadImages()
}

// 监听属性变化
watch([() => props.directoryPath, () => props.showAllPhotos, () => props.showFavorites], () => {
  loadImages()
}, { immediate: true })

// 键盘快捷键
const handleKeyDown = (event) => {
  // F12 切换调试模式
  if (event.key === 'F12') {
    event.preventDefault()
    debugMode.value = !debugMode.value
  }
  
  // F5 刷新
  if (event.key === 'F5') {
    event.preventDefault()
    loadImages()
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeyDown)
})

// 清理
import { onUnmounted } from 'vue'
onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown)
})

// 暴露方法给父组件
const refresh = () => {
  loadImages()
}

defineExpose({
  refresh
})
</script>

<style scoped>
.content {
  width: 100%;
}

.photo-grid {
  display: grid;
  gap: 1rem;
}

.photo-thumbnail {
  aspect-ratio: 1;
  min-height: 150px;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.photo-thumbnail:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.thumbnail-container {
  position: relative;
  width: 100%;
  height: 100%;
  background: #f5f5f5;
}

.thumbnail-container img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.thumbnail-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.photo-info {
  padding: 8px;
}

.filename {
  font-size: 14px;
  font-weight: bold;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.metadata {
  font-size: 12px;
  color: #666;
  margin-top: 2px;
}

.load-more {
  text-align: center;
  padding: 20px;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.loading-placeholder {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@media (max-width: 768px) {
  .photo-grid {
    gap: 0.75rem;
  }
  
  .toolbar {
    padding: 0.5rem;
  }
}

/* 动态网格列数将在computed中处理 */
</style>