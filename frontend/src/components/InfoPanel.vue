<template>
  <div class="info-panel w-[320px] bg-white border-l border-gray-200 h-full flex flex-col relative overflow-y-auto">
    <!-- 关闭按钮 -->
    <button @click="emit('close')" class="absolute top-4 right-4 p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-full transition-colors duration-200 z-10">
      <i class="fas fa-times"></i>
    </button>
    <!-- 照片预览 -->
    <div class="p-4 border-b border-gray-200">
      <el-image 
        :src="`http://localhost:8324/api/image/${imageDetails.id}`"
        :alt="imageDetails.filename"
        :preview-src-list="[`http://localhost:8324/api/image/${imageDetails.id}`]"
        :initial-index="0"
        fit="scale-down"
        class="w-full h-48 rounded-button cursor-pointer"
        loading="lazy"
        hide-on-click-modal
        preview-teleported>
      </el-image>
    </div>
    <div class="flex-1 overflow-y-auto">
      <!-- 照片信息 -->
      <div class="p-4 border-b border-gray-200 grid grid-cols-2 gap-4">
        <div>
          <h3 class="text-xs font-medium text-gray-500">文件名</h3>
          <p class="text-sm font-medium">{{ imageDetails.filename }}</p>
        </div>
        <div>
          <h3 class="text-xs font-medium text-gray-500">文件大小</h3>
          <p class="text-sm">{{ formatFileSize(imageDetails.file_size) }}</p>
        </div>
        <div>
          <h3 class="text-xs font-medium text-gray-500">拍摄日期</h3>
          <p class="text-sm">{{ formatDate(getExifData('DateTimeOriginal') || getExifData('DateTime') || imageDetails.created_at) }}</p>
        </div>
        <div>
          <h3 class="text-xs font-medium text-gray-500">像素</h3>
          <p class="text-sm">{{ formatDimensions(imageDetails.width, imageDetails.height) }}</p>
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
          <p class="text-sm">{{ getExifData('FocalLength') || 'N/A' }}mm</p>
        </div>
        <div>
          <h3 class="text-xs font-medium text-gray-500">光圈</h3>
          <p class="text-sm">f{{ getExifData('FNumber') || 'N/A' }}</p>
        </div>
        <div>
          <h3 class="text-xs font-medium text-gray-500">ISO</h3>
          <p class="text-sm">{{ getExifData('ISOSpeedRatings') || getExifData('ISO') || 'N/A' }}</p>
        </div>
        <div>
          <h3 class="text-xs font-medium text-gray-500">快门速度</h3>
          <p class="text-sm">{{ formatShutterSpeed(getExifData('ExposureTime')) }}</p>
        </div>
        <div class="col-span-2">
          <h3 class="text-xs font-medium text-gray-500">文件路径</h3>
          <p class="text-sm">{{ imageDetails.file_path }}</p>
        </div>
        <div class="col-span-2">
          <h3 class="text-xs font-medium text-gray-500">评分</h3>
          <div class="flex items-center space-x-1">
            <i v-for="n in 5" :key="n" class="fas" :class="n <= (imageDetails.rating || 0) ? 'fa-star text-yellow-400' : 'fa-star text-gray-300'"></i>
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
          <span v-for="tag in (imageDetails.tags || [])" :key="tag" class="px-3 py-1 bg-primary/10 text-primary rounded-full text-sm flex items-center space-x-1 cursor-pointer hover:bg-primary/20 transition-colors duration-200">
            <span>{{ tag }}</span>
            <i class="fas fa-times-circle"></i>
          </span>
        </div>
        <div v-if="imageDetails.category">
          <h3 class="font-medium mb-3">分类</h3>
          <div class="px-3 py-1 bg-primary/10 text-primary rounded-full text-sm inline-block">
            {{ imageDetails.category }}
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

<script setup>
import { ref, computed, watch, onMounted } from 'vue';

const props = defineProps({
  image: {
    type: Object,
    required: true
  }
});

const emit = defineEmits(['close', 'update-image']);

const showEditModal = ref(false);
const tempRating = ref(0);
const tempTags = ref([]);
const tempCategory = ref('');
const newTag = ref('');
const imageDetails = ref(props.image);

// 计算图片预览URL
const imagePreviewUrl = computed(() => 
  `http://localhost:8324/api/image/${imageDetails.id}`
);

// 监听image变化，重置编辑数据
watch(() => props.image, () => {
  closeEditModal();
  imageDetails.value = props.image;
  fetchImageDetails();
});

// 获取图片详细信息
const fetchImageDetails = async () => {
  if (!props.image.id) return;
  
  try {
    const response = await fetch(`http://localhost:8324/api/image/details/${props.image.id}`);
    if (response.ok) {
      const data = await response.json();
      imageDetails.value = { ...props.image, ...data };
    }
  } catch (error) {
    console.error('获取图片详细信息失败:', error);
  }
};

// 组件挂载时获取图片详细信息
onMounted(() => {
  fetchImageDetails();
});

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

// 获取EXIF数据
const getExifData = (field) => {
  if (imageDetails.value.exif_data && imageDetails.value.exif_data[field]) {
    return imageDetails.value.exif_data[field];
  }
  return null;
};

// 格式化日期
const formatDate = (dateString) => {
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
};

// 格式化快门速度
const formatShutterSpeed = (exposureTime) => {
  if (!exposureTime) return 'N/A';
  
  // 如果是字符串，先转换为数字
  const time = typeof exposureTime === 'string' ? parseFloat(exposureTime) : exposureTime;
  
  if (time < 1) {
    // 小于1秒时转换为分数形式
    const denominator = Math.round(1 / time);
    return `1/${denominator}`;
  } else {
    // 大于等于1秒时显示为整数
    return `${Math.round(time)}s`;
  }
};

// 格式化尺寸
const formatDimensions = (width, height) => {
  // 检查是否有EXIF方向信息，如果图片是竖直的（方向为6或8），则交换宽高
  if (imageDetails.value.exif_data) {
    const orientation = imageDetails.value.exif_data.Orientation;
    // 方向6和8表示图片需要旋转
    if (orientation === '6' || orientation === '8') {
      // 交换宽高
      if (width && height) {
        return `${height} × ${width}`;
      } else {
        // 尝试从EXIF信息获取尺寸
        const exifWidth = imageDetails.value.exif_data.Width;
        const exifHeight = imageDetails.value.exif_data.Height;
        if (exifWidth && exifHeight) {
          return `${exifHeight} × ${exifWidth}`;
        }
      }
    }
  }
  
  // 默认情况，不交换宽高
  if (width && height) {
    return `${width} × ${height}`;
  } else if (imageDetails.value.exif_data) {
    // 尝试从EXIF信息获取尺寸
    const exifWidth = imageDetails.value.exif_data.Width;
    const exifHeight = imageDetails.value.exif_data.Height;
    if (exifWidth && exifHeight) {
      return `${exifWidth} × ${exifHeight}`;
    }
  }
  return 'N/A';
};

// 编辑相关方法
const openEditModal = () => {
  tempRating.value = imageDetails.value.rating || 0;
    tempTags.value = [...(imageDetails.value.tags || [])];
    tempCategory.value = imageDetails.value.category || '';
  showEditModal.value = true;
};

const closeEditModal = () => {
  showEditModal.value = false;
  newTag.value = '';
};



const setRating = (rating) => {
  tempRating.value = rating;
};

const addTag = () => {
  if (newTag.value.trim() && !tempTags.value.includes(newTag.value.trim())) {
    tempTags.value.push(newTag.value.trim());
    newTag.value = '';
  }
};

const removeTag = (tag) => {
  tempTags.value = tempTags.value.filter(t => t !== tag);
};

const saveChanges = async () => {
  const updatedImage = {
    ...imageDetails.value,
    rating: tempRating.value,
    tags: [...tempTags.value],
    category: tempCategory.value
  };

  try {
    // 通过pywebview API更新图片信息
    const result = await window.electronAPI.updateImageInfo(updatedImage);
    if (result.success) {
      // 更新成功后，通知父组件更新数据
      emit('update-image', updatedImage);
      closeEditModal();
    }
  } catch (error) {
    console.error('更新图片信息失败:', error);
  }
};
</script>

<style scoped>
.info-panel {
  flex-shrink: 0;
}
</style>