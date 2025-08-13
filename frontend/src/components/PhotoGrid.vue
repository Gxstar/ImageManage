<template>
  <div class="content flex flex-col h-full">
    <!-- 工具栏 -->
  <div class="toolbar p-3 border-b border-gray-200 bg-white">
    <div class="flex items-center space-x-4">
      <div class="flex items-center space-x-2">
        <label class="text-sm font-medium text-gray-700">缩略图:</label>
        <select
          v-model="thumbnailSize"
          class="text-sm border border-gray-300 rounded-md px-2 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option :value="100" selected>小</option>
          <option :value="150">中</option>
          <option :value="200">大</option>
        </select>
      </div>
      
      <!-- 评分筛选 -->
      <div class="flex items-center space-x-2">
        <label class="text-sm font-medium text-gray-700">评分:</label>
        <el-rate
          v-model="ratingFilter"
          :max="5"
          :allow-half="false"
          size="small"
          :colors="['#ff6b6b', '#ffa726', '#66bb6a']"
          :void-color="'#e4e7ed'"
          :clearable="true"
          @change="applyRatingFilter"
        />
        <el-button 
          v-if="ratingFilter > 0"
          type="text" 
          size="small" 
          @click="clearRatingFilter"
          class="ml-1"
        >
          清除
        </el-button>
      </div>
    </div>
  </div>

    <!-- 照片网格 -->
    <div class="flex-1 overflow-y-auto p-6 photo-grid-container" ref="photosContainer">
      <div v-if="loading" class="text-center py-4">
        <p>正在加载图片...</p>
      </div>
      <div v-else-if="error" class="text-center py-4 text-red-500">
        <p>{{ error }}</p>
      </div>
      <div v-else>
        <div class="photo-grid grid gap-4" :style="gridStyle">
          <!-- 虚拟滚动占位符 -->
          <div 
            v-for="image in visibleImages" 
            :key="image.id || image.path" 
            class="photo-thumbnail bg-white rounded-lg overflow-hidden border border-gray-200 hover:border-blue-500 cursor-pointer relative group"
            @click="selectImage(image)"
            :style="{ minHeight: thumbnailSize + 'px' }"
          >
            <!-- 收藏按钮 -->
            <button 
              @click.stop="toggleFavorite(image)"
              class="absolute top-2 right-2 z-10 p-1.5 bg-black bg-opacity-20 rounded-full text-white opacity-0 group-hover:opacity-100 transition-all duration-200 hover:bg-opacity-40"
              :class="{ 'opacity-100': image.is_favorite }"
            >
              <FontAwesomeIcon 
                :icon="image.is_favorite ? faHeartSolid : faHeartRegular" 
                class="w-4 h-4"
                :class="{ 'text-red-500': image.is_favorite }"
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
            显示 {{ visibleImages.length }} / {{ totalCount }} 张图片
            <span class="text-blue-600">(评分≥{{ ratingFilter }}星)</span>
          </template>
          <template v-else>
            显示 {{ Math.min(visibleImages.length, totalCount) }} / {{ totalCount }} 张图片
          </template>
          <span v-if="totalCount === 0" class="text-gray-400">(暂无图片)</span>
          <div v-if="debugMode" class="text-xs text-gray-500 mt-1">
            当前模式: {{ 
              showFavorites ? '收藏夹' : 
              showAllPhotos ? '全部照片' : '目录: ' + directoryPath 
            }}<br>
            分页: offset={{ currentOffset }}, limit={{ pageSize }}<br>
            已加载缩略图: {{ loadedThumbnails.size }}<br>
            评分筛选: {{ ratingFilter > 0 ? ratingFilter + '星' : '无' }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed, onUnmounted, nextTick } from 'vue'
import { API_URLS } from '../config/api'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { faHeart as faHeartSolid } from '@fortawesome/free-solid-svg-icons'
import { faHeart as faHeartRegular } from '@fortawesome/free-regular-svg-icons'

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

// 基础数据
const images = ref([])
const loading = ref(false)
const error = ref(null)
const thumbnailSize = ref(100)
const pageSize = ref(100)
const currentOffset = ref(0)
const totalCount = ref(0)
const hasMore = ref(true)
const isLoadingMore = ref(false)
const debugMode = ref(false)
const ratingFilter = ref(0)

// 缩略图懒加载状态
const loadedThumbnails = ref(new Set())
const photosContainer = ref(null)

// 可见图片（用于虚拟滚动）
const visibleImages = computed(() => {
  if (ratingFilter.value > 0) {
    return images.value.filter(image => image.rating >= ratingFilter.value)
  }
  return images.value
})

// 动态计算网格样式
const gridStyle = computed(() => ({
  gridTemplateColumns: `repeat(auto-fill, minmax(${thumbnailSize.value}px, 1fr))`
}))

// 评分筛选相关方法
const applyRatingFilter = () => {
  loadImages(props.directoryPath)
}

const clearRatingFilter = () => {
  ratingFilter.value = 0
  applyRatingFilter()
}

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
      const image = visibleImages.value[index] // 使用visibleImages而不是images.value
      if (image && !loadedThumbnails.value.has(image.id || image.path)) {
        loadedThumbnails.value.add(image.id || image.path)
      }
    }
  })
}

// 加载图片方法 - 支持分页和评分筛选
const loadImages = async (directoryPath, loadMore = false) => {
  if (!loadMore) {
    images.value = [];
    currentOffset.value = 0;
    hasMore.value = true;
    loadedThumbnails.value.clear()
  }
  
  if (!props.showAllPhotos && !props.showFavorites && !directoryPath) {
    loading.value = false;
    error.value = null;
    return;
  }

  if (loadMore) {
    isLoadingMore.value = true;
  } else {
    loading.value = true;
  }
  error.value = null;

  try {
    let result;

    // 直接使用 PyWebView API
    if (props.showFavorites) {
      result = await window.pywebview.api.get_favorite_images();
      // 收藏夹不支持分页，一次性获取所有
      if (result.images) {
        result.total = result.images.length;
        // 只有在loadMore时才需要切片，初次加载显示全部
        if (loadMore) {
          result.images = result.images.slice(currentOffset.value, currentOffset.value + pageSize.value);
        }
      }
    } else if (props.showAllPhotos) {
      result = await window.pywebview.api.get_all_images(pageSize.value, currentOffset.value);
    } else {
      result = await window.pywebview.api.get_images_in_directory(directoryPath, pageSize.value, currentOffset.value);
    }

    if (result.error) {
      throw new Error(result.error);
    }

    const newImages = (result.images || []).sort((a, b) => {
      return new Date(b.modified_at || 0) - new Date(a.modified_at || 0);
    });

    if (loadMore) {
      images.value.push(...newImages);
    } else {
      images.value = newImages;
    }

    totalCount.value = result.total || 0;
    
    // 收藏夹模式下，分页逻辑需要调整
    if (props.showFavorites) {
      // 收藏夹模式下，初次加载显示全部，loadMore时不再加载更多
      currentOffset.value = images.value.length;
      hasMore.value = false; // 收藏夹一次性显示全部，不支持分页加载更多
    } else {
      currentOffset.value += newImages.length;
      hasMore.value = currentOffset.value < totalCount.value;
    }

    // 延迟加载可见缩略图
    nextTick(() => {
      loadVisibleThumbnails()
    })

  } catch (err) {
    console.error('加载图片时出错:', err);
    error.value = err.message || '加载图片时出错';
    if (!loadMore) {
      images.value = [];
    }
  } finally {
    if (loadMore) {
      isLoadingMore.value = false;
    } else {
      loading.value = false;
    }
  }
};

// 加载更多图片
const loadMoreImages = () => {
  if (hasMore.value && !isLoadingMore.value) {
    loadImages(props.showAllPhotos ? '' : props.directoryPath, true);
  }
};

// 滚动到底部检测 + 懒加载
const handleScroll = (event) => {
  const element = event.target;
  const scrollTop = element.scrollTop;
  const scrollHeight = element.scrollHeight;
  const clientHeight = element.clientHeight;
  
  // 当滚动到底部附近时加载更多
  if (scrollHeight - scrollTop - clientHeight < 200) {
    loadMoreImages();
  }
  
  // 懒加载可见缩略图
  loadVisibleThumbnails()
};

// 选择图片
const selectImage = (image) => {
  emit('select-image', image);
};

// 切换收藏状态
const toggleFavorite = async (image) => {
  try {
    const imageId = image.id;
    if (!imageId) {
      console.error('图片ID不存在');
      return;
    }
    
    // 调用后端API更新收藏状态
    const result = await window.pywebview.api.toggle_image_favorite(imageId);
    
    if (result.success) {
      // 更新本地状态
      image.is_favorite = !image.is_favorite;
    } else {
      console.error('更新收藏状态失败:', result.error);
    }
  } catch (error) {
    console.error('切换收藏状态时出错:', error);
  }
};

// 重置并重新加载
const resetAndLoad = () => {
  let targetPath = '';
  if (!props.showAllPhotos && !props.showFavorites) {
    // 目录模式
    targetPath = props.directoryPath;
  } else if (props.showAllPhotos) {
    // 全部照片模式
    targetPath = '';
  } else {
    // 收藏夹模式
    targetPath = '';
  }
  loadImages(targetPath);
};

// 公开方法供父组件调用
const refresh = () => {
  resetAndLoad();
};

// 暴露方法给父组件
defineExpose({
  resetAndLoad,
  refresh
})

// 监听目录路径变化
watch(() => props.directoryPath, (newPath) => {
  if (!props.showAllPhotos && !props.showFavorites) {
    resetAndLoad();
  }
}, { immediate: true })

// 监听显示全部照片变化
watch(() => props.showAllPhotos, (newShowAllPhotos) => {
  resetAndLoad();
}, { immediate: true })

// 监听显示收藏夹变化
watch(() => props.showFavorites, (newShowFavorites) => {
  resetAndLoad();
}, { immediate: true })

// 添加滚动事件监听
const setupScrollListener = () => {
  const container = photosContainer.value;
  if (container) {
    container.addEventListener('scroll', handleScroll);
  }
};

const removeScrollListener = () => {
  const container = photosContainer.value;
  if (container) {
    container.removeEventListener('scroll', handleScroll);
  }
};

// 组件挂载后设置滚动监听
watch(() => images.value.length, () => {
  nextTick(() => {
    setupScrollListener();
    loadVisibleThumbnails();
  });
});

onUnmounted(() => {
  removeScrollListener();
});
</script>

<style scoped>
.content {
  width: calc(100% - 280px);
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