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
        <!-- 缩略图大小控制滑块 -->
        <div class="relative">
          <button 
            @click="showThumbnailSlider = !showThumbnailSlider"
            class="px-3 py-1.5 rounded-button hover:bg-gray-100 flex items-center space-x-2 whitespace-nowrap min-w-max"
          >
            <i class="fas fa-expand text-gray-500"></i>
            <span>缩略图大小</span>
          </button>
          <div 
            v-if="showThumbnailSlider" 
            class="absolute right-0 top-full mt-1 bg-white border border-gray-200 rounded-button shadow-lg p-3 z-30"
          >
            <input 
              type="range" 
              min="100" 
              max="180" 
              v-model="thumbnailMinWidth" 
              @input="handleThumbnailSizeChange"
              class="w-24"
              orient="vertical"
            >
            <div class="text-center text-sm text-gray-600 mt-1">{{ thumbnailMinWidth }}px</div>
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
            v-if="image.thumbnail && image.loaded" 
            :src="`data:image/jpeg;base64,${image.thumbnail}`" 
            class="w-full h-full object-cover" 
            :alt="image.name"
            loading="lazy"
          >
          <img 
            v-else-if="!image.thumbnail && image.loaded"
            :src="`file://${image.path}`" 
            class="w-full h-full object-cover" 
            :alt="image.name"
            loading="lazy"
          >
          <div v-else class="w-full h-full bg-gray-200 flex items-center justify-center">
            <div class="text-gray-500 text-sm">加载中...</div>
          </div>
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

<script>
export default {
  name: 'PhotoGrid',
  props: {
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
  },
  data() {
    return {
      images: [],
      displayedImages: [],
      loading: false,
      error: null,
      currentPage: 0,
      pageSize: 50,  // 每页显示50张图片
      observer: null,
      thumbnailMinWidth: 150,  // 缩略图最小宽度，默认150px
      showThumbnailSlider: false  // 控制缩略图大小滑块的显示/隐藏
    };
  },
  watch: {
    directoryPath: {
      handler(newPath) {
        // 只有在不显示全部照片时才根据目录路径变化加载图片
        if (!this.showAllPhotos) {
          this.loadImages(newPath);
        }
      },
      immediate: true
    },
    showAllPhotos: {
      handler(newShowAllPhotos) {
        // 当showAllPhotos属性变化时，重新加载图片
        if (newShowAllPhotos) {
          this.loadImages('');
        }
      },
      immediate: true
    },
    thumbnailMinWidth: {
      handler(newWidth) {
        // 更新CSS变量
        if (this.$el) {
          this.$el.style.setProperty('--thumbnail-min-width', `${newWidth}px`);
        }
      },
      immediate: true
    }
  },
  methods: {
    async loadImages(directoryPath) {
      // 清空现有图片列表
      this.images = [];
      this.displayedImages = [];
      this.currentPage = 0;
      
      // 如果不是显示全部照片且没有选择目录，重置状态并返回
      if (!this.showAllPhotos && !directoryPath) {
        this.loading = false;
        this.error = null;
        return;
      }
      
      // 开始加载
      this.loading = true;
      this.error = null;
      
      try {
        let result;
        
        // 检查electronAPI是否存在
      if (!window.electronAPI) {
        console.warn('electronAPI不可用，使用包含EXIF信息的模拟数据');
        // 使用包含EXIF信息的模拟数据
        result = {
          images: [
            {
              name: '示例图片1.jpg',
              path: '/path/to/example/image1.jpg',
              size: 1024000,
              width: 1920,
              height: 1080,
              date: '2023-05-20T10:30:00',
              exif: {
                DateTimeOriginal: '2023:05:20 10:30:00',
                Model: 'Canon EOS R5',
                FocalLength: '50mm',
                FNumber: 'f/1.8',
                ExifImageWidth: 1920,
                ExifImageHeight: 1080
              }
            },
            {
              name: '示例图片2.jpg',
              path: '/path/to/example/image2.jpg',
              size: 2048000,
              width: 3840,
              height: 2160,
              date: '2023-05-21T14:45:00',
              exif: {
                DateTimeOriginal: '2023:05:21 14:45:00',
                Model: 'Nikon D850',
                FocalLength: '24mm',
                FNumber: 'f/2.8',
                ExifImageWidth: 3840,
                ExifImageHeight: 2160
              }
            }
          ]
        };
      }
        
        // 根据showAllPhotos属性决定调用哪个方法
        if (this.showAllPhotos) {
          // 显示全部照片
          if (window.electronAPI && window.electronAPI.getAllImages) {
            result = await window.electronAPI.getAllImages();
          } else {
            console.warn('getAllImages方法不可用，使用模拟数据');
            // 使用模拟数据
            result = {
              images: [
                {
                  name: '示例图片1.jpg',
                  path: '/path/to/example/image1.jpg',
                  size: 1024000,
                  width: 1920,
                  height: 1080,
                  exif: {
                    DateTimeOriginal: '2023:05:20 10:30:00',
                    Model: 'Canon EOS R5',
                    FocalLength: '50mm',
                    FNumber: 'f/1.8'
                  }
                },
                {
                  name: '示例图片2.jpg',
                  path: '/path/to/example/image2.jpg',
                  size: 2048000,
                  width: 3840,
                  height: 2160,
                  exif: {
                    DateTimeOriginal: '2023:05:21 14:45:00',
                    Model: 'Nikon D850',
                    FocalLength: '24mm',
                    FNumber: 'f/2.8'
                  }
                }
              ]
            };
          }
        } else {
          // 显示特定目录的照片
          if (window.electronAPI && window.electronAPI.getImagesInDirectory) {
            result = await window.electronAPI.getImagesInDirectory(directoryPath);
          } else {
            console.warn('getImagesInDirectory方法不可用，使用模拟数据');
            // 使用模拟数据
            result = {
              images: [
                {
                  name: '示例图片1.jpg',
                  path: '/path/to/example/image1.jpg',
                  size: 1024000,
                  width: 1920,
                  height: 1080,
                  exif: {
                    DateTimeOriginal: '2023:05:20 10:30:00',
                    Model: 'Canon EOS R5',
                    FocalLength: '50mm',
                    FNumber: 'f/1.8'
                  }
                },
                {
                  name: '示例图片2.jpg',
                  path: '/path/to/example/image2.jpg',
                  size: 2048000,
                  width: 3840,
                  height: 2160,
                  exif: {
                    DateTimeOriginal: '2023:05:21 14:45:00',
                    Model: 'Nikon D850',
                    FocalLength: '24mm',
                    FNumber: 'f/2.8'
                  }
                }
              ]
            };
          }
        }
        
        // 检查是否有错误
        if (result.error) {
          throw new Error(result.error);
        }
        
        // 更新图片列表，并处理缩略图数据
        this.images = (result.images || []).map(image => ({
          ...image,
          thumbnail: image.thumbnail ? image.thumbnail.toString('base64') : null,
          loaded: false
        })).sort((a, b) => {
          // 按拍摄日期倒序排列，如果没有拍摄日期则使用文件创建时间
          const getDate = (image) => {
            if (image.exif && image.exif.DateTimeOriginal) {
              return new Date(image.exif.DateTimeOriginal);
            } else if (image.created_at) {
              return new Date(image.created_at);
            } else {
              return new Date(0);
            }
          };
          
          const dateA = getDate(a);
          const dateB = getDate(b);
          
          // 降序排列（最近的在前）
          return dateB - dateA;
        });
        
        // 重置分页
        this.currentPage = 0;
        this.loadMore();
      } catch (err) {
        console.error('加载图片时出错:', err);
        this.error = err.message || '加载图片时出错';
        this.images = [];
        this.displayedImages = [];
      } finally {
        this.loading = false;
      }
    },
    async selectImage(image) {
      // 当图片被选中时，将其loaded状态设置为true
      const index = this.displayedImages.findIndex(img => img.path === image.path);
      if (index !== -1) {
        // 使用Vue 3的响应式系统更新数组元素
        this.displayedImages[index] = { ...this.displayedImages[index], loaded: true };
        // 触发视图更新
        this.displayedImages = [...this.displayedImages];
      }

      // 获取EXIF信息
      let exifData = image.exif || null;
      try {
        if (window.electronAPI && window.electronAPI.getExifData && !exifData) {
          const result = await window.electronAPI.getExifData(image.path);
          if (!result.error) {
            exifData = result.exif;
          }
        }
      } catch (err) {
        console.error('获取EXIF信息时出错:', err);
      }
      
      // 发射事件，将选中的图片信息和EXIF信息传递给父组件
      this.$emit('select-image', { ...image, exif: exifData });
    },
    updateInfoPanelWidth() {
      // 根据hasInfoPanel属性设置CSS变量
      const contentElement = this.$el;
      if (contentElement) {
        if (this.hasInfoPanel) {
          contentElement.style.setProperty('--info-panel-width', '320px');
        } else {
          contentElement.style.setProperty('--info-panel-width', '0px');
        }
      }
    },
    // 加载更多图片
    loadMore() {
      const start = this.currentPage * this.pageSize;
      const end = start + this.pageSize;
      const newImages = this.images.slice(start, end);
      
      // 为新图片添加loaded状态
      const newImagesWithLoadedState = newImages.map(image => ({
        ...image,
        loaded: false
      }));
      
      this.displayedImages = [...this.displayedImages, ...newImagesWithLoadedState];
      this.currentPage++;
      
      // 在下次DOM更新后重新观察图片
      this.$nextTick(() => {
        this.observeImages();
      });
    },
    
    // 处理滚动事件，实现无限滚动加载
    handleScroll(event) {
      const { scrollTop, scrollHeight, clientHeight } = event.target;
      // 当滚动到底部时自动加载更多
      if (scrollTop + clientHeight >= scrollHeight - 10) {
        if (!this.loading && this.hasMoreImages) {
          this.loadMore();
        }
      }
    },
    
    // 处理缩略图大小变化
    handleThumbnailSizeChange() {
      // 触发网格重新渲染
      this.$forceUpdate();
      
      // 点击滑块后隐藏滑块面板
      setTimeout(() => {
        this.showThumbnailSlider = false;
      }, 1000);
    },
    
    // 初始化Intersection Observer
    initIntersectionObserver() {
      // 创建Intersection Observer实例
      this.observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            // 当图片进入视口时，标记为已加载
            const imgElement = entry.target;
            const imageIndex = parseInt(imgElement.dataset.index);
            
            // 更新对应图片的loaded状态
            if (this.displayedImages[imageIndex]) {
              // 使用Vue 3的响应式系统更新数组元素
              this.displayedImages[imageIndex] = { ...this.displayedImages[imageIndex], loaded: true };
              // 触发视图更新
              this.displayedImages = [...this.displayedImages];
              
              // 停止观察已加载的图片
              this.observer.unobserve(imgElement);
            }
          }
        });
      }, {
        // 设置阈值，当图片进入视口10%时触发
        threshold: 0.1
      });
      
      // 初始观察已存在的图片
      this.observeImages();
    },
    
    // 观察图片元素
    observeImages() {
      // 在下次DOM更新后执行
      this.$nextTick(() => {
        const photoElements = this.$refs.photoGrid.querySelectorAll('.photo-thumbnail');
        photoElements.forEach((element, index) => {
          // 确保每个元素都有正确的索引
          element.dataset.index = index;
          // 如果图片尚未加载，则观察它
          if (!this.displayedImages[index] || !this.displayedImages[index].loaded) {
            this.observer.observe(element);
          }
        });
      });
    }
  },
  mounted() {
    this.updateInfoPanelWidth();
    // 设置初始的缩略图大小CSS变量
    if (this.$el) {
      this.$el.style.setProperty('--thumbnail-min-width', `${this.thumbnailMinWidth}px`);
    }
    // 监听滚动事件，实现无限滚动加载
    this.$refs.photoGrid.addEventListener('scroll', this.handleScroll);
    
    // 初始化Intersection Observer
    this.initIntersectionObserver();
  },
  updated() {
    this.updateInfoPanelWidth();
    
    // 在组件更新后重新观察图片
    this.observeImages();
  },
  beforeDestroy() {
    // 移除滚动事件监听
    if (this.$refs.photoGrid) {
      this.$refs.photoGrid.removeEventListener('scroll', this.handleScroll);
    }
  },
  
  // 计算属性
  computed: {
    hasMoreImages() {
      return this.displayedImages.length < this.images.length;
    }
  },
    

}
</script>

<style scoped>
.content {
  width: calc(100% - 280px - var(--info-panel-width, 0px));
}
.photo-grid {
  grid-template-columns: repeat(auto-fill, minmax(var(--thumbnail-min-width, 100px), 1fr));
}
.photo-thumbnail {
  aspect-ratio: 1/1;
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