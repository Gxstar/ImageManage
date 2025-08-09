<template>
  <div class="content flex flex-col h-full">
    <!-- 工具栏 -->
    <div class="toolbar p-3 border-b border-gray-200 bg-white">
      <div class="flex items-center space-x-3">
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
    </div>

    <!-- 照片网格 -->
    <div class="flex-1 overflow-y-auto p-6 photo-grid-container">
      <div v-if="loading" class="text-center py-4">
        <p>正在加载图片...</p>
      </div>
      <div v-else-if="error" class="text-center py-4 text-red-500">
        <p>{{ error }}</p>
      </div>
      <div v-else>
        <div class="photo-grid grid gap-4" :style="gridStyle">
          <div 
            v-for="image in images" 
            :key="image.path" 
            class="photo-thumbnail bg-white rounded-lg overflow-hidden border border-gray-200 hover:border-blue-500 cursor-pointer"
            @click="selectImage(image)"
            :style="{ minHeight: thumbnailSize + 'px' }"
          >
            <img 
              v-if="image.id"
              :src="`http://localhost:8324/api/thumbnail/${image.id}`"
              class="w-full h-full object-cover" 
              :alt="image.name"
              loading="lazy"
            >
            <img 
              v-else
              :src="`http://localhost:8324/api/image/path?file_path=${encodeURIComponent(image.path)}`"
              class="w-full h-full object-cover" 
              :alt="image.name"
              loading="lazy"
            >
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
          显示 {{ Math.min(images.length, totalCount) }} / {{ totalCount }} 张图片
          <span v-if="totalCount === 0" class="text-gray-400">(暂无图片)</span>
          <div v-if="debugMode" class="text-xs text-gray-500 mt-1">
            当前模式: {{ showAllPhotos ? '全部照片' : '目录: ' + directoryPath }}<br>
            分页: offset={{ currentOffset }}, limit={{ pageSize }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed, onUnmounted } from 'vue'

const props = defineProps({
  directoryPath: {
    type: String,
    default: ''
  },
  showAllPhotos: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['select-image'])
const images = ref([])
const loading = ref(false)
const error = ref(null)
const thumbnailSize = ref(100) // 默认100px（小）
const pageSize = ref(50) // 每页加载数量
const currentOffset = ref(0)
const totalCount = ref(0)
const hasMore = ref(true)
const isLoadingMore = ref(false)
const debugMode = ref(false) // 调试模式

// 动态计算网格样式
const gridStyle = computed(() => ({
  gridTemplateColumns: `repeat(auto-fill, minmax(${thumbnailSize.value}px, 1fr))`
}))

// 加载图片方法 - 支持分页
const loadImages = async (directoryPath, loadMore = false) => {
  if (!loadMore) {
    images.value = [];
    currentOffset.value = 0;
    hasMore.value = true;
  }
  
  if (!props.showAllPhotos && !directoryPath) {
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

    // 检查是否在pywebview环境中
    if (!window.pywebview || !window.pywebview.api) {
      console.log('当前在开发环境，使用模拟数据');
      result = {
        images: [
          {
            name: '示例图片.jpg',
            path: directoryPath ? directoryPath + '\\image.jpg' : 'C:\\mock\\image.jpg',
            thumbnail: 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=='
          }
        ],
        total: 1
      };
    } else {
      // 使用pywebview API调用
      if (props.showAllPhotos) {
        result = await window.pywebview.api.get_all_images(pageSize.value, currentOffset.value);
      } else {
        result = await window.pywebview.api.get_images_in_directory(directoryPath, pageSize.value, currentOffset.value);
      }
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
    currentOffset.value += newImages.length;
    hasMore.value = currentOffset.value < totalCount.value;

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

// 滚动到底部检测
const handleScroll = (event) => {
  const element = event.target;
  const scrollTop = element.scrollTop;
  const scrollHeight = element.scrollHeight;
  const clientHeight = element.clientHeight;
  
  // 当滚动到底部附近时加载更多
  if (scrollHeight - scrollTop - clientHeight < 200) {
    loadMoreImages();
  }
};

// 选择图片
const selectImage = (image) => {
  emit('select-image', image);
};

// 重置并重新加载
const resetAndLoad = () => {
  loadImages(props.showAllPhotos ? '' : props.directoryPath);
};

// 监听目录路径变化
watch(() => props.directoryPath, (newPath) => {
  if (!props.showAllPhotos) {
    resetAndLoad();
  }
}, { immediate: true })

// 监听显示全部照片变化
watch(() => props.showAllPhotos, (newShowAllPhotos) => {
  resetAndLoad();
}, { immediate: true })

// 添加滚动事件监听
const photoGridContainer = ref(null);

const setupScrollListener = () => {
  const container = document.querySelector('.photo-grid-container');
  if (container) {
    container.addEventListener('scroll', handleScroll);
  }
};

const removeScrollListener = () => {
  const container = document.querySelector('.photo-grid-container');
  if (container) {
    container.removeEventListener('scroll', handleScroll);
  }
};

// 组件挂载后设置滚动监听
watch(() => images.value.length, () => {
  setTimeout(setupScrollListener, 100);
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