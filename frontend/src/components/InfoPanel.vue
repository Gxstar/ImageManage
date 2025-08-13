<template>
  <div class="info-panel w-[320px] bg-white border-l border-gray-200 h-full flex flex-col relative overflow-y-auto">
    <!-- 关闭按钮 -->
    <button @click="emit('close')" class="absolute top-4 right-4 p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-full transition-colors duration-200 z-10">
      <i class="fas fa-times"></i>
    </button>
    <!-- 照片预览 -->
    <div class="p-4 border-b border-gray-200">
      <el-image
        v-if="imageDetails.id"
        :src="API_URLS.image(imageDetails.id)"
        :preview-src-list="[API_URLS.image(imageDetails.id)]"
        fit="scale-down"
        class="w-full h-48 rounded-button cursor-pointer"
        loading="lazy"
        preview-teleport
        :alt="imageDetails.filename"
      />
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
          <el-rate
            v-model="imageDetails.rating"
            :max="5"
            :allow-half="false"
            size="small"
            class="mt-1"
            :colors="['#ff6b6b', '#ffa726', '#66bb6a']"
            :void-color="'#e4e7ed'"
            :disabled-void-color="'#e4e7ed'"
            @change="updateRating"
          />
        </div>
      </div>
      <!-- 快速操作 -->
      <div class="p-4 border-b border-gray-200">
        <h3 class="font-medium mb-3">快速操作</h3>
        <div class="grid grid-cols-2 gap-2">
          <button class="py-2 rounded-button bg-white border border-gray-200 hover:border-primary hover:bg-primary/5 flex items-center justify-center space-x-2 transition-colors duration-200">
            <font-awesome-icon icon="edit" class="text-gray-500" />
            <span>编辑</span>
          </button>
          <button class="py-2 rounded-button bg-white border border-gray-200 hover:border-primary hover:bg-primary/5 flex items-center justify-center space-x-2 transition-colors duration-200">
            <font-awesome-icon icon="share-alt" class="text-gray-500" />
            <span>分享</span>
          </button>
          <button class="py-2 rounded-button bg-white border border-gray-200 hover:border-primary hover:bg-primary/5 flex items-center justify-center space-x-2 transition-colors duration-200">
            <font-awesome-icon icon="trash-alt" class="text-gray-500" />
            <span>删除</span>
          </button>
          <button class="py-2 rounded-button bg-white border border-gray-200 hover:border-primary hover:bg-primary/5 flex items-center justify-center space-x-2 transition-colors duration-200">
            <font-awesome-icon icon="tags" class="text-gray-500" />
            <span>标签</span>
          </button>
        </div>
      </div>
      <!-- 应用标签 -->
      <div class="p-4">
        <h3 class="font-medium mb-3">应用标签</h3>
        <div class="flex flex-wrap gap-2 mb-4">
          <span v-for="tag in (imageDetails.tags || [])" :key="tag" class="px-3 py-1 bg-primary/10 text-primary rounded-full text-sm flex items-center space-x-1 cursor-pointer hover:bg-primary/20 transition-colors duration-200">
            <span>{{ tag }}</span>
            <font-awesome-icon icon="times-circle" />
          </span>
        </div>
        <div v-if="imageDetails.category">
          <h3 class="font-medium mb-3">分类</h3>
          <div class="px-3 py-1 bg-primary/10 text-primary rounded-full text-sm inline-block">
            {{ imageDetails.category }}
          </div>
        </div>
        <button class="w-full py-2 rounded-button bg-white border border-dashed border-gray-300 hover:border-primary hover:bg-primary/5 flex items-center justify-center space-x-2 transition-colors duration-200">
          <font-awesome-icon icon="plus" class="text-gray-400" />
          <span>新建相册</span>
        </button>
      </div>
    </div>

  </div>


</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { API_URLS } from '../config/api';

const props = defineProps({
  image: {
    type: Object,
    required: true
  }
});

const emit = defineEmits(['close', 'update-image']);

const imageDetails = ref(props.image);
// 计算图片预览URL
const imagePreviewUrl = computed(() => 
  API_URLS.image(imageDetails.id)
);

// 监听image变化，重置数据
watch(() => props.image, () => {
  imageDetails.value = props.image;
  fetchImageDetails();
});

// 获取图片详细信息
const fetchImageDetails = async () => {
  if (!props.image?.id) return;
  
  try {
    const result = await window.pywebview.api.get_image_details(props.image.id);
    if (result.success) {
      imageDetails.value = { ...props.image, ...result.image };
    } else {
      console.error('获取图片详细信息失败:', result.error);
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

// 实时更新评分
const updateRating = async (newRating) => {
  try {
    const result = await window.pywebview.api.update_image_rating(
      imageDetails.value.id, 
      newRating
    );
    
    if (!result.success) {
      throw new Error(result.error || '评分更新失败');
    }
    
    // 更新本地数据
    imageDetails.value.rating = newRating;
    
    // 通知父组件更新数据
    emit('update-image', { ...imageDetails.value, rating: newRating });
    
  } catch (error) {
    console.error('更新评分失败:', error);
    alert('评分更新失败: ' + error.message);
  }
};
</script>

<style scoped>
.info-panel {
  flex-shrink: 0;
}
</style>