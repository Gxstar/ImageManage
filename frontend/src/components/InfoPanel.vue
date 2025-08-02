<template>
  <div class="info-panel w-[320px] bg-white border-l border-gray-200 h-full flex flex-col relative overflow-y-auto">
    <!-- 关闭按钮 -->
    <button @click="$emit('close')" class="absolute top-4 right-4 p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-full transition-colors duration-200 z-10">
      <i class="fas fa-times"></i>
    </button>
    <!-- 照片预览 -->
    <div class="p-4 border-b border-gray-200">
      <img :src="`file://${image.path}`"
           class="w-full h-48 object-cover rounded-button" :alt="image.name">
    </div>
    <div class="flex-1 overflow-y-auto">
      <!-- 照片信息 -->
      <div class="p-4 border-b border-gray-200 grid grid-cols-2 gap-4">
        <div>
          <h3 class="text-xs font-medium text-gray-500">文件名</h3>
          <p class="text-sm font-medium">{{ image.name }}</p>
        </div>
        <div>
          <h3 class="text-xs font-medium text-gray-500">文件大小</h3>
          <p class="text-sm">{{ formatFileSize(image.size) }}</p>
        </div>
        <div>
          <h3 class="text-xs font-medium text-gray-500">拍摄日期</h3>
          <p class="text-sm">{{ formatDate(getExifData('DateTimeOriginal') || getExifData('DateTime') || image.date) }}</p>
        </div>
        <div>
          <h3 class="text-xs font-medium text-gray-500">像素</h3>
          <p class="text-sm">{{ formatDimensions(image.width, image.height) }}</p>
        </div>
        <div>
          <h3 class="text-xs font-medium text-gray-500">相机型号</h3>
          <p class="text-sm">{{ getExifData('Model') || 'N/A' }}</p>
        </div>
        <div>
          <h3 class="text-xs font-medium text-gray-500">镜头型号</h3>
          <p class="text-sm">{{ getExifData('LensModel') || 'N/A' }}</p>
        </div>
        <div>
          <h3 class="text-xs font-medium text-gray-500">焦距</h3>
          <p class="text-sm">{{ getExifData('FocalLength') || 'N/A' }}</p>
        </div>
        <div>
          <h3 class="text-xs font-medium text-gray-500">光圈</h3>
          <p class="text-sm">{{ getExifData('FNumber') || 'N/A' }}</p>
        </div>
        <div class="col-span-2">
          <h3 class="text-xs font-medium text-gray-500">文件路径</h3>
          <p class="text-sm">{{ image.path }}</p>
        </div>
        <div class="col-span-2">
          <h3 class="text-xs font-medium text-gray-500">评分</h3>
          <div class="flex items-center space-x-1">
            <i v-for="n in 5" :key="n" class="fas" :class="n <= (image.rating || 0) ? 'fa-star text-yellow-400' : 'fa-star text-gray-300'"></i>
          </div>
        </div>
      </div>
      <!-- 快速操作 -->
      <div class="p-4 border-b border-gray-200">
        <h3 class="font-medium mb-3">快速操作</h3>
        <div class="grid grid-cols-2 gap-2">
          <button class="py-2 rounded-button bg-white border border-gray-200 hover:border-primary hover:bg-primary/5 flex items-center justify-center space-x-2 transition-colors duration-200">
            <i class="fas fa-edit text-gray-500"></i>
            <span>编辑</span>
          </button>
          <button class="py-2 rounded-button bg-white border border-gray-200 hover:border-primary hover:bg-primary/5 flex items-center justify-center space-x-2 transition-colors duration-200">
            <i class="fas fa-share-alt text-gray-500"></i>
            <span>分享</span>
          </button>
          <button class="py-2 rounded-button bg-white border border-gray-200 hover:border-primary hover:bg-primary/5 flex items-center justify-center space-x-2 transition-colors duration-200">
            <i class="fas fa-trash-alt text-gray-500"></i>
            <span>删除</span>
          </button>
          <button class="py-2 rounded-button bg-white border border-gray-200 hover:border-primary hover:bg-primary/5 flex items-center justify-center space-x-2 transition-colors duration-200">
            <i class="fas fa-tags text-gray-500"></i>
            <span>标签</span>
          </button>
          <button class="col-span-2 py-2 rounded-button bg-white border border-gray-200 hover:border-primary hover:bg-primary/5 flex items-center justify-center space-x-2 transition-colors duration-200" @click="openEditModal">
            <i class="fas fa-edit text-gray-500"></i>
            <span>编辑信息</span>
          </button>
        </div>
      </div>
      <!-- 应用标签 -->
      <div class="p-4">
        <h3 class="font-medium mb-3">应用标签</h3>
        <div class="flex flex-wrap gap-2 mb-4">
          <span v-for="tag in image.tags" :key="tag" class="px-3 py-1 bg-primary/10 text-primary rounded-full text-sm flex items-center space-x-1 cursor-pointer hover:bg-primary/20 transition-colors duration-200">
            <span>{{ tag }}</span>
            <i class="fas fa-times-circle"></i>
          </span>
        </div>
        <div v-if="image.category">
          <h3 class="font-medium mb-3">分类</h3>
          <div class="px-3 py-1 bg-primary/10 text-primary rounded-full text-sm inline-block">
            {{ image.category }}
          </div>
        </div>
        <button class="w-full py-2 rounded-button bg-white border border-dashed border-gray-300 hover:border-primary hover:bg-primary/5 flex items-center justify-center space-x-2 transition-colors duration-200">
          <i class="fas fa-plus text-gray-400"></i>
          <span>新建相册</span>
        </button>
      </div>
    </div>
    <!-- 编辑信息模态框 -->
    <div v-if="showEditModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg w-96 max-w-90vw max-h-90vh overflow-y-auto">
        <div class="p-6">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-lg font-medium">编辑照片信息</h3>
            <button @click="closeEditModal" class="text-gray-500 hover:text-gray-700">
              <i class="fas fa-times"></i>
            </button>
          </div>
          
          <div class="space-y-4">
            <!-- 评分 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">评分</label>
              <div class="flex space-x-1">
                <i v-for="n in 5" :key="n" 
                   class="fas fa-star text-2xl cursor-pointer" 
                   :class="n <= tempRating ? 'text-yellow-400' : 'text-gray-300'"
                   @click="setRating(n)"></i>
              </div>
            </div>
            
            <!-- 标签 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">标签</label>
              <div class="flex flex-wrap gap-2 mb-2">
                <span v-for="tag in tempTags" :key="tag" class="px-2 py-1 bg-primary/10 text-primary rounded-full text-sm flex items-center space-x-1">
                  <span>{{ tag }}</span>
                  <i class="fas fa-times-circle cursor-pointer" @click="removeTag(tag)"></i>
                </span>
              </div>
              <div class="flex space-x-2">
                <input v-model="newTag" placeholder="添加新标签" class="flex-1 border border-gray-300 rounded-button px-3 py-1 text-sm">
                <button @click="addTag" class="px-3 py-1 bg-primary text-white rounded-button text-sm">添加</button>
              </div>
            </div>
            
            <!-- 分类 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">分类</label>
              <input v-model="tempCategory" placeholder="输入分类" class="w-full border border-gray-300 rounded-button px-3 py-1 text-sm">
            </div>
          </div>
          
          <div class="flex justify-end space-x-3 mt-6">
            <button @click="closeEditModal" class="px-4 py-2 border border-gray-300 rounded-button text-sm">取消</button>
            <button @click="saveChanges" class="px-4 py-2 bg-primary text-white rounded-button text-sm">保存</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'InfoPanel',
  props: {
    image: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      showEditModal: false,
      tempRating: 0,
      tempTags: [],
      tempCategory: '',
      newTag: ''
    };
  },
  methods: {
    formatFileSize(bytes) {
      if (bytes === 0) return '0 Bytes';
      const k = 1024;
      const sizes = ['Bytes', 'KB', 'MB', 'GB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },
    getExifData(field) {
      if (this.image.exif && this.image.exif[field]) {
        return this.image.exif[field];
      }
      return null;
    },
    formatDate(dateString) {
      if (!dateString) return 'N/A';
      
      // 尝试解析EXIF日期格式 (YYYY:MM:DD HH:MM:SS)
      const exifRegex = /^\d{4}:\d{2}:\d{2} \d{2}:\d{2}:\d{2}$/;
      if (exifRegex.test(dateString)) {
        const [datePart, timePart] = dateString.split(' ');
        const [year, month, day] = datePart.split(':');
        const [hour, minute, second] = timePart.split(':');
        const date = new Date(year, month - 1, day, hour, minute, second);
        return date.toLocaleString();
      }
      
      // 尝试解析标准日期格式
      const date = new Date(dateString);
      if (!isNaN(date.getTime())) {
        return date.toLocaleString();
      }
      
      // 如果无法解析，返回原始字符串
      return dateString;
    },
    formatDimensions(width, height) {
      if (width && height) {
        return `${width} × ${height}`;
      } else if (this.image.exif) {
        // 尝试从EXIF信息获取尺寸
        const exifWidth = this.image.exif.ExifImageWidth || this.image.exif.ImageWidth;
        const exifHeight = this.image.exif.ExifImageHeight || this.image.exif.ImageHeight;
        if (exifWidth && exifHeight) {
          return `${exifWidth} × ${exifHeight}`;
        }
      }
      return 'N/A';
    },
    openEditModal() {
      // 初始化临时数据
      this.tempRating = this.image.rating || 0;
      this.tempTags = [...(this.image.tags || [])];
      this.tempCategory = this.image.category || '';
      this.showEditModal = true;
    },
    closeEditModal() {
      this.showEditModal = false;
      this.newTag = '';
    },
    setRating(rating) {
      this.tempRating = rating;
    },
    addTag() {
      if (this.newTag.trim() && !this.tempTags.includes(this.newTag.trim())) {
        this.tempTags.push(this.newTag.trim());
        this.newTag = '';
      }
    },
    removeTag(tag) {
      this.tempTags = this.tempTags.filter(t => t !== tag);
    },
    saveChanges() {
      // 这里需要实现保存更改到数据库的逻辑
      // 由于这是一个展示组件，实际保存逻辑应该通过事件传递给父组件处理
      const updatedImage = {
        ...this.image,
        rating: this.tempRating,
        tags: [...this.tempTags],
        category: this.tempCategory
      };
      
      // 发送事件通知父组件保存更改
      this.$emit('update-image', updatedImage);
      
      // 关闭模态框
      this.closeEditModal();
    }
  }
}
</script>

<style scoped>
.info-panel {
  flex-shrink: 0;
}
</style>