<template>
  <div class="content flex flex-col h-full">
    <!-- 顶部工具栏 -->
    <div class="bg-white border-b border-gray-200 p-3 flex items-center justify-between">
      <div class="flex items-center space-x-2 flex-nowrap">
        <button class="px-3 py-1.5 rounded-button hover:bg-gray-100 flex items-center space-x-2 whitespace-nowrap min-w-max">
          <i class="fas fa-th-large text-gray-500"></i>
          <span>网格视图</span>
        </button>
        <button class="px-3 py-1.5 rounded-button hover:bg-gray-100 flex items-center space-x-2 whitespace-nowrap min-w-max">
          <i class="fas fa-list text-gray-500"></i>
          <span>列表视图</span>
        </button>
      </div>
      <div class="flex items-center space-x-4">
        <div class="flex items-center space-x-2">
          <button class="px-3 py-1.5 rounded-button hover:bg-gray-100 flex items-center space-x-2 whitespace-nowrap min-w-max">
            <i class="fas fa-sort-amount-down text-gray-500"></i>
            <span>按日期</span>
          </button>
          <button class="px-3 py-1.5 rounded-button hover:bg-gray-100 flex items-center space-x-2 whitespace-nowrap min-w-max">
            <i class="fas fa-filter text-gray-500"></i>
            <span>筛选</span>
          </button>
        </div>
        <!-- 缩略图大小选择 -->
        <div class="relative">
          <button 
            @click="showThumbnailSizeSelector = !showThumbnailSizeSelector"
            class="px-3 py-1.5 rounded-button hover:bg-gray-100 flex items-center space-x-2 whitespace-nowrap min-w-max"
          >
            <i class="fas fa-expand text-gray-500"></i>
            <span>{{ thumbnailSizeLabel }}</span>
          </button>
          <div 
            v-if="showThumbnailSizeSelector" 
            class="absolute right-0 top-full mt-1 bg-white border border-gray-200 rounded-button shadow-lg z-30"
          >
            <div class="py-1">
              <button 
                v-for="size in thumbnailSizes" 
                :key="size.value"
                @click="selectThumbnailSize(size)"
                class="block w-full text-left px-4 py-2 text-sm hover:bg-gray-100 whitespace-nowrap"
                :class="{ 'bg-primary text-white hover:bg-primary-dark': thumbnailMinWidth === size.value }"
              >
                {{ size.label }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- 照片网格 -->
    <div class="flex-1 overflow-y-auto p-6" ref="photoGrid">
      <div v-if="loading" class="text-center py-4">
        <p>正在加载图片...</p>
      </div>
      <div v-else-if="error" class="text-center py-4 text-red-500">
        <p>{{ error }}</p>
      </div>
      <div v-else class="photo-grid grid gap-4">
        <div 
          v-for="(image, index) in displayedImages" 
          :key="image.path" 
          class="photo-thumbnail bg-white rounded-button overflow-hidden border border-gray-200 hover:border-primary cursor-pointer relative group"
          @click="selectImage(image)"
          :data-index="index"
        >
          <img 
            v-if="image.thumbnail" 
            :src="`data:image/jpeg;base64,${image.thumbnail}`" 
            class="w-full h-full object-cover" 
            :alt="image.name"
            loading="lazy"
            @load="onImageLoad(index)"
            @error="onImageError(index)"
          >
          <img 
            v-else
            :src="`file://${image.path}`" 
            class="w-full h-full object-cover" 
            :alt="image.name"
            loading="lazy"
            @load="onImageLoad(index)"
            @error="onImageError(index)"
          >
          <div class="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-20 transition-all duration-200"></div>
          <div class="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-all duration-200">
            <button class="bg-white p-1 rounded-full shadow-sm">
              <i class="fas fa-star text-gray-400 hover:text-yellow-400"></i>
            </button>
          </div>
        </div>
      </div>
      <!-- 加载更多按钮 -->
      <div v-if="hasMoreImages && !loading" class="text-center py-4">
        <button @click="loadMore" class="px-4 py-2 bg-primary text-white rounded-button hover:bg-primary-dark">
          加载更多
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount, nextTick, computed } from 'vue'

const props = defineProps({
  directoryPath: {
    type: String,
    default: ''
  },
  showAllPhotos: {
    type: Boolean,
    default: false
  },
  hasInfoPanel: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['select-image'])
const images = ref([])
const displayedImages = ref([])
const loading = ref(false)
const error = ref(null)
const currentPage = ref(0)
const pageSize = 50  // 每页显示50张图片
const observer = ref(null)
const thumbnailMinWidth = ref(150)  // 缩略图最小宽度，默认150px
const showThumbnailSizeSelector = ref(false)  // 控制缩略图大小选择器的显示/隐藏
const photoGrid = ref(null)

// 缩略图大小选项
const thumbnailSizes = [
  { label: '小', value: 120 },
  { label: '中', value: 150 },
  { label: '大', value: 180 },
  { label: '超大', value: 220 }
]

// 当前选择的缩略图大小标签
const thumbnailSizeLabel = computed(() => {
  const currentSize = thumbnailSizes.find(size => size.value === thumbnailMinWidth.value)
  return currentSize ? currentSize.label : '缩略图大小'
})

// 加载图片方法
const loadImages = async (directoryPath) => {
  images.value = [];
  displayedImages.value = [];
  currentPage.value = 0;

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
        // 开发环境回退到模拟数据
        if (props.showAllPhotos) {
          result = {
            images: [
              {
                name: '示例图片1.jpg',
                path: 'C:\\mock\\image1.jpg',
                size: 1024000,
                width: 1920,
                height: 1080,
                created_at: Date.now() / 1000,
                modified_at: Date.now() / 1000,
                thumbnail: 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==', // 1x1透明像素作为占位符
                exif: {
                  DateTimeOriginal: '2023:05:20 10:30:00',
                  Model: 'Canon EOS R5',
                  FocalLength: '50mm',
                  FNumber: 'f/1.8'
                }
              },
              {
                name: '示例图片2.jpg',
                path: 'C:\\mock\\image2.jpg',
                size: 2048000,
                width: 3840,
                height: 2160,
                created_at: Date.now() / 1000,
                modified_at: Date.now() / 1000,
                thumbnail: 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==', // 1x1透明像素作为占位符
                exif: {
                  DateTimeOriginal: '2023:05:21 14:45:00',
                  Model: 'Nikon D850',
                  FocalLength: '24mm',
                  FNumber: 'f/2.8'
                }
              }
            ]
          };
        } else {
          result = {
            images: [
              {
                name: '示例图片1.jpg',
                path: directoryPath + '\\image1.jpg',
                size: 1024000,
                width: 1920,
                height: 1080,
                created_at: Date.now() / 1000,
                modified_at: Date.now() / 1000,
                thumbnail: 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==', // 1x1透明像素作为占位符
                exif: {
                  DateTimeOriginal: '2023:05:20 10:30:00',
                  Model: 'Canon EOS R5',
                  FocalLength: '50mm',
                  FNumber: 'f/1.8'
                }
              }
            ]
          };
        }
    } else {
      // 使用pywebview API调用
      if (props.showAllPhotos) {
        // 显示全部照片
        result = await window.pywebview.api.get_all_images();
      } else {
        // 显示特定目录的照片
        result = await window.pywebview.api.get_images_in_directory(directoryPath);
      }
    }

    if (result.error) {
      throw new Error(result.error);
    }

    // 处理图片数据
    console.log('处理图片数据，总数:', result.images?.length || 0);
    const processedImages = (result.images || []).map(image => {
      console.log('图片:', image.name, '缩略图:', !!image.thumbnail);
      return {
        ...image,
        thumbnail: image.thumbnail || null,
        loaded: true, // 后端返回的图片数据已经是可用的
        // 转换时间戳为Date对象
        created_at: image.created_at ? new Date(image.created_at * 1000) : new Date(),
        modified_at: image.modified_at ? new Date(image.modified_at * 1000) : new Date()
      };
    }).sort((a, b) => {
      // 按修改时间降序排列
      return new Date(b.modified_at) - new Date(a.modified_at);
    });

    images.value = processedImages;
    currentPage.value = 0;
    // 直接加载第一页数据，避免loadMore作用域问题
    const start = 0;
    const end = pageSize;
    const newImages = images.value.slice(start, end);

    const newImagesWithLoadedState = newImages.map(image => ({
      ...image,
      loaded: false
    }));

    displayedImages.value = newImagesWithLoadedState;
    currentPage.value = 0;
  } catch (err) {
    console.error('加载图片时出错:', err);
    error.value = err.message || '加载图片时出错';
    images.value = [];
    displayedImages.value = [];
  } finally {
    loading.value = false;
  }
};

// 图片加载处理函数
const onImageLoad = (index) => {
  if (displayedImages.value[index]) {
    displayedImages.value[index].loaded = true;
  }
};

const onImageError = (index) => {
  if (displayedImages.value[index]) {
    console.error('图片加载失败:', displayedImages.value[index].path);
    displayedImages.value[index].loaded = false;
    displayedImages.value[index].thumbnail = null;
  }
};

// 选择图片监听目录路径变化
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

// 监听缩略图大小变化
watch(thumbnailMinWidth, (newWidth) => {
  const photoGridElement = document.querySelector('.photo-grid');
  if (photoGridElement) {
    photoGridElement.style.setProperty('--thumbnail-min-width', `${newWidth}px`);
  }
}, { immediate: true })

// 选择图片
const selectImage = async (image) => {
  const index = displayedImages.value.findIndex(img => img.path === image.path);
  if (index !== -1) {
    displayedImages.value[index] = { ...displayedImages.value[index], loaded: true };
  }

  let exifData = image.exif || null;
  
  // 获取EXIF信息
  if (!exifData && window.pywebview && window.pywebview.api) {
    try {
      const result = await window.pywebview.api.get_exif_data(image.path);
      if (!result.error) {
        exifData = result.exif;
      }
    } catch (err) {
      console.warn('获取EXIF信息失败:', err);
    }
  }

  emit('select-image', { ...image, exif: exifData });
};

// 更新信息面板宽度
const updateInfoPanelWidth = () => {
  const contentElement = document.querySelector('.content');
  if (contentElement) {
    if (props.hasInfoPanel) {
      contentElement.style.setProperty('--info-panel-width', '320px');
    } else {
      contentElement.style.setProperty('--info-panel-width', '0px');
    }
  }
};

// 加载更多图片
const loadMore = () => {
  const start = currentPage.value * pageSize;
  const end = start + pageSize;
  const newImages = images.value.slice(start, end);

  displayedImages.value = [...displayedImages.value, ...newImages];
  currentPage.value++;

  nextTick(() => {
    observeImages();
  });
};

// 处理滚动事件
const handleScroll = (event) => {
  const { scrollTop, scrollHeight, clientHeight } = event.target;
  if (scrollTop + clientHeight >= scrollHeight - 10) {
    if (!loading.value && hasMoreImages.value) {
      loadMore();
    }
  }
};

// 选择缩略图大小
const selectThumbnailSize = (size) => {
  thumbnailMinWidth.value = size.value;
  showThumbnailSizeSelector.value = false;
  
  // 立即更新CSS变量
  const photoGridElement = document.querySelector('.photo-grid');
  if (photoGridElement) {
    photoGridElement.style.setProperty('--thumbnail-min-width', `${size.value}px`);
  }
  
  nextTick(() => {
    observeImages();
  });
};

// 初始化Intersection Observer
const initIntersectionObserver = () => {
  observer.value = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const imgElement = entry.target;
        const imageIndex = parseInt(imgElement.dataset.index);
        
        if (displayedImages.value[imageIndex]) {
          displayedImages.value[imageIndex] = { ...displayedImages.value[imageIndex], loaded: true };
          displayedImages.value = [...displayedImages.value];
          observer.value.unobserve(imgElement);
        }
      }
    });
  }, {
    threshold: 0.1
  });
};

// 观察图片元素
const observeImages = () => {
  nextTick(() => {
    if (!photoGrid.value || !observer.value) return;
    
    const photoElements = photoGrid.value.querySelectorAll('.photo-thumbnail');
    photoElements.forEach((element, index) => {
      element.dataset.index = index;
      if (!displayedImages.value[index] || !displayedImages.value[index].loaded) {
        observer.value.observe(element);
      }
    });
  });
};

// 计算属性
const hasMoreImages = computed(() => {
  return displayedImages.value.length < images.value.length;
});

// 生命周期钩子
onMounted(() => {
  updateInfoPanelWidth();
  initIntersectionObserver();
  
  // 设置初始缩略图大小
  const photoGridElement = document.querySelector('.photo-grid');
  if (photoGridElement) {
    photoGridElement.style.setProperty('--thumbnail-min-width', `${thumbnailMinWidth.value}px`);
  }
  
  if (photoGrid.value) {
    photoGrid.value.addEventListener('scroll', handleScroll);
  }
});

onBeforeUnmount(() => {
  if (photoGrid.value) {
    photoGrid.value.removeEventListener('scroll', handleScroll);
  }
  if (observer.value) {
    observer.value.disconnect();
  }
});
</script>

<style scoped>
.content {
  width: calc(100% - 280px - var(--info-panel-width, 0px));
}
.photo-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(var(--thumbnail-min-width, 150px), 1fr));
  gap: 1rem;
}
.photo-thumbnail {
  aspect-ratio: 1;
  min-height: var(--thumbnail-min-width, 150px);
}

@media (max-width: 768px) {
  .photo-grid {
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  }
}

  /* 垂直滑块样式 */
  input[type="range"][orient="vertical"] {
    writing-mode: bt-lr; /* IE */
    -webkit-appearance: slider-vertical; /* WebKit */
    width: 8px;
    height: 100px;
    padding: 0 5px;
  }
</style>