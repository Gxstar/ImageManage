<template>
  <div class="flex-1 overflow-y-auto px-6 py-2 photo-grid-container" ref="photosContainer">
    <div v-if="loading" class="text-center py-4">
      <p>正在加载图片...</p>
    </div>
    <div v-else-if="error" class="text-center py-4 text-red-500">
      <p>{{ error }}</p>
    </div>
    <div v-else>
      <!-- 按月份分组显示 -->
      <div v-for="group in groupedImages" :key="group.month" class="mb-8">
        <el-divider content-position="left">
          <span class="text-md font-semibold text-gray-700">{{ group.month }}</span>
        </el-divider>
        
        <div class="photo-grid grid gap-4" :style="gridStyle">
          <div 
            v-for="image in group.images" 
            :key="image.id || image.path" 
            class="photo-thumbnail bg-white rounded-lg overflow-hidden border border-gray-200 hover:border-blue-500 cursor-pointer relative group"
            @click="selectImage(image)"
            :style="{ minHeight: thumbnailSize + 'px' }"
          >
            <!-- 收藏按钮 -->
            <button 
              @click.stop="toggleFavorite(image)"
              class="absolute top-1 right-1 z-10 w-6 h-6 bg-black bg-opacity-20 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all duration-200 hover:bg-opacity-30"
              :class="{ 'opacity-100': image.is_favorite }"
            >
              <FontAwesomeIcon 
                :icon="image.is_favorite ? faHeartSolid : faHeartRegular" 
                class="w-3 h-3"
                :class="image.is_favorite ? 'text-red-500' : 'text-white'"
              />
            </button>
            
            <!-- 缩略图容器 -->
            <div class="thumbnail-container w-full h-full">
              <img 
                v-if="image.id && loadedThumbnails.has(image.id)"
                :src="API_URLS.thumbnail(image.id)"
                class="w-full h-full object-cover" 
                :alt="image.name || image.filename"
                loading="lazy"
                @load="onImageLoad(image.id)"
                @error="onImageError(image.id)"
              >
              <img 
                v-else-if="loadedThumbnails.has(image.path)"
                :src="API_URLS.imagePath(image.path)"
                class="w-full h-full object-cover" 
                :alt="image.name || image.filename"
                loading="lazy"
                @load="onImageLoad(image.path)"
                @error="onImageError(image.path)"
              >
              <div 
                v-else
                class="w-full h-full flex items-center justify-center bg-gray-100 text-gray-400"
              >
                <svg class="animate-spin h-8 w-8" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 加载更多 -->
      <div v-if="hasMore" class="text-center py-4">
        <button 
          @click="loadMoreImages"
          :disabled="isLoadingMore"
          class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
        >
          {{ isLoadingMore ? '加载中...' : '加载更多' }}
        </button>
      </div>
      
      <!-- 加载状态 -->
      <div v-if="isLoadingMore" class="text-center py-2">
        <p class="text-sm text-gray-500">正在加载更多图片...</p>
      </div>
      
      <!-- 图片总数信息 -->
      <div v-if="!loading && images.length > 0" class="text-center py-2 text-sm text-gray-600">
        <template v-if="ratingFilter > 0">
          显示 {{ groupedImages.reduce((total, group) => total + group.images.length, 0) }} / {{ totalCount }} 张图片
          <span class="text-blue-600">(评分≥{{ ratingFilter }}星)</span>
        </template>
        <template v-else>
          显示 {{ groupedImages.reduce((total, group) => total + group.images.length, 0) }} / {{ totalCount }} 张图片
        </template>
        <span v-if="totalCount === 0" class="text-gray-400">(暂无图片)</span>
        <div v-if="debugMode" class="text-xs text-gray-500 mt-1">
          当前模式: {{ 
            showFavorites ? '收藏夹' : 
            showAllPhotos ? '全部照片' : '目录: ' + directoryPath 
          }}<br>
          分组数量: {{ groupedImages.length }}<br>
          已加载缩略图: {{ loadedThumbnails.size }}<br>
          评分筛选: {{ ratingFilter > 0 ? ratingFilter + '星' : '无' }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onUnmounted, nextTick } from 'vue'
import { API_URLS } from '../../config/api'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { faHeart as faHeartSolid } from '@fortawesome/free-solid-svg-icons'
import { faHeart as faHeartRegular } from '@fortawesome/free-regular-svg-icons'
import { ElDivider } from 'element-plus'

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
  },
  thumbnailSize: {
    type: Number,
    default: 100
  },
  ratingFilter: {
    type: Number,
    default: 0
  },
  loading: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: null
  },
  images: {
    type: Array,
    default: () => []
  },
  totalCount: {
    type: Number,
    default: 0
  },
  hasMore: {
    type: Boolean,
    default: true
  },
  isLoadingMore: {
    type: Boolean,
    default: false
  },
  debugMode: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits([
  'select-image', 
  'toggle-favorite', 
  'load-more', 
  'image-count-changed'
])

const photosContainer = ref(null)
const loadedThumbnails = ref(new Set())

// 获取照片日期（优先EXIF拍摄日期，其次文件创建日期）
const getPhotoDate = (image) => {
  // 优先从EXIF数据中提取拍摄日期
  if (image.exif_data) {
    const exif = image.exif_data;
    // 尝试多个EXIF日期字段
    const dateFields = ['DateTimeOriginal', 'DateTime', 'DateTimeDigitized'];
    for (const field of dateFields) {
      if (exif[field]) {
        try {
          // EXIF日期格式: "2023:10:15 14:30:25"
          const dateStr = exif[field];
          if (dateStr && dateStr.length >= 19) {
            const year = parseInt(dateStr.substring(0, 4));
            const month = parseInt(dateStr.substring(5, 7)) - 1; // 月份从0开始
            const day = parseInt(dateStr.substring(8, 10));
            const hour = parseInt(dateStr.substring(11, 13));
            const minute = parseInt(dateStr.substring(14, 16));
            const second = parseInt(dateStr.substring(17, 19));
            
            if (!isNaN(year) && !isNaN(month) && !isNaN(day)) {
              return new Date(year, month, day, hour, minute, second);
            }
          }
        } catch (e) {
          console.warn('解析EXIF日期失败:', e);
        }
      }
    }
  }
  
  // 其次使用文件创建日期
  if (image.created_at) {
    return new Date(image.created_at)
  }
  
  // 最后使用文件修改日期
  return new Date(image.modified_at || 0)
}

// 格式化月份显示
const formatMonthYear = (date) => {
  const year = date.getFullYear()
  const month = date.getMonth() + 1
  return `${year}年${month}月`
}

// 按月份分组的图片数据
const groupedImages = computed(() => {
  const filteredImages = props.ratingFilter > 0 
    ? props.images.filter(image => image.rating >= props.ratingFilter)
    : props.images

  const groups = {}
  
  filteredImages.forEach(image => {
    const date = getPhotoDate(image)
    const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`
    const monthLabel = formatMonthYear(date)
    
    if (!groups[monthKey]) {
      groups[monthKey] = {
        month: monthLabel,
        images: []
      }
    }
    groups[monthKey].images.push(image)
  })
  
  // 按月份降序排序，并在每个分组内按时间降序排序
  return Object.entries(groups)
    .sort(([a], [b]) => b.localeCompare(a))
    .map(([_, group]) => {
      // 在每个分组内按时间降序排序
      group.images.sort((a, b) => {
        const dateA = getPhotoDate(a)
        const dateB = getPhotoDate(b)
        return dateB - dateA // 降序排序
      })
      return group
    })
})

// 可见图片（用于虚拟滚动）- 已废弃，使用groupedImages
const visibleImages = computed(() => {
  if (props.ratingFilter > 0) {
    return props.images.filter(image => image.rating >= props.ratingFilter)
  }
  return props.images
})

// 动态计算网格样式
const gridStyle = computed(() => ({
  gridTemplateColumns: `repeat(auto-fill, minmax(${props.thumbnailSize}px, 1fr))`
}))

// 缩略图加载/错误处理
const onImageLoad = (id) => {
  loadedThumbnails.value.add(id)
}

const onImageError = (id) => {
  loadedThumbnails.value.delete(id)
}

// 加载可见缩略图
const loadVisibleThumbnails = () => {
  if (!photosContainer.value) return
  const container = photosContainer.value
  const items = container.querySelectorAll('.photo-thumbnail')
  items.forEach((item, index) => {
    const rect = item.getBoundingClientRect()
    const containerRect = container.getBoundingClientRect()
    if (rect.top < containerRect.bottom + 200 && rect.bottom > containerRect.top - 200) {
      const image = visibleImages.value[index]
      if (image && !loadedThumbnails.value.has(image.id || image.path)) {
        loadedThumbnails.value.add(image.id || image.path)
      }
    }
  })
}

// 选择图片
const selectImage = (image) => {
  emit('select-image', image)
}

// 切换收藏状态
const toggleFavorite = async (image) => {
  emit('toggle-favorite', image)
}

// 加载更多图片
const loadMoreImages = () => {
  emit('load-more')
}

// 滚动到底部检测 + 懒加载
const handleScroll = (event) => {
  const element = event.target
  const scrollTop = element.scrollTop
  const scrollHeight = element.scrollHeight
  const clientHeight = element.clientHeight
  
  // 当滚动到底部附近时加载更多
  if (scrollHeight - scrollTop - clientHeight < 200) {
    loadMoreImages()
  }
  
  // 懒加载可见缩略图
  loadVisibleThumbnails()
}

// 重置并重新加载
const resetAndLoad = () => {
  loadedThumbnails.value.clear()
}

// 监听数据变化
watch(() => props.images, () => {
  nextTick(() => {
    loadVisibleThumbnails()
  })
}, { deep: true })

// 添加滚动事件监听
const setupScrollListener = () => {
  const container = photosContainer.value
  if (container) {
    container.addEventListener('scroll', handleScroll)
  }
}

const removeScrollListener = () => {
  const container = photosContainer.value
  if (container) {
    container.removeEventListener('scroll', handleScroll)
  }
}

// 组件挂载后设置滚动监听
watch(() => props.images.length, () => {
  nextTick(() => {
    setupScrollListener()
    loadVisibleThumbnails()
  })
})

onUnmounted(() => {
  removeScrollListener()
})

// 公开方法供父组件调用
defineExpose({
  resetAndLoad,
  loadVisibleThumbnails
})
</script>

<style scoped>
.photo-grid-container {
  height: 100%;
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
}

/* 动态网格列数将在computed中处理 */
</style>