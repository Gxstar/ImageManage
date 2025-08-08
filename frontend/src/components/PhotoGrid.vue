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
    <div class="flex-1 overflow-y-auto p-6">
      <div v-if="loading" class="text-center py-4">
        <p>正在加载图片...</p>
      </div>
      <div v-else-if="error" class="text-center py-4 text-red-500">
        <p>{{ error }}</p>
      </div>
      <div v-else class="photo-grid grid gap-4" :style="gridStyle">
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
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'

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

// 动态计算网格样式
const gridStyle = computed(() => ({
  gridTemplateColumns: `repeat(auto-fill, minmax(${thumbnailSize.value}px, 1fr))`
}))

// 加载图片方法
const loadImages = async (directoryPath) => {
  images.value = [];
  
  if (!props.showAllPhotos && !directoryPath) {
    loading.value = false;
    error.value = null;
    return;
  }

  loading.value = true;
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
        ]
      };
    } else {
      // 使用pywebview API调用
      if (props.showAllPhotos) {
        result = await window.pywebview.api.get_all_images();
      } else {
        result = await window.pywebview.api.get_images_in_directory(directoryPath);
      }
    }

    if (result.error) {
      throw new Error(result.error);
    }

    images.value = (result.images || []).sort((a, b) => {
      return new Date(b.modified_at || 0) - new Date(a.modified_at || 0);
    });

  } catch (err) {
    console.error('加载图片时出错:', err);
    error.value = err.message || '加载图片时出错';
    images.value = [];
  } finally {
    loading.value = false;
  }
};

// 选择图片
const selectImage = (image) => {
  emit('select-image', image);
};

// 监听目录路径变化
watch(() => props.directoryPath, (newPath) => {
  if (!props.showAllPhotos) {
    loadImages(newPath);
  }
}, { immediate: true })

// 监听显示全部照片变化
watch(() => props.showAllPhotos, (newShowAllPhotos) => {
  if (newShowAllPhotos) {
    loadImages('');
  }
}, { immediate: true })
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