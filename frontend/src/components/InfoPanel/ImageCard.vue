<template>
  <el-card class="w-full" shadow="hover">
    <!-- 图片预览 -->
    <div class="mb-4">
      <el-image
        v-if="image?.id"
        :src="API_URLS.image(image.id)"
        :preview-src-list="[API_URLS.image(image.id)]"
        fit="scale-down"
        class="w-full h-48 rounded-lg cursor-pointer"
        loading="lazy"
        preview-teleport
        :alt="image.filename"
      />
    </div>
    
    <!-- 图片信息 -->
    <div class="grid grid-cols-2 gap-4">
      <div>
        <h3 class="text-xs font-medium text-gray-500">文件名</h3>
        <p class="text-sm font-medium">{{ image.filename }}</p>
      </div>
      <div>
        <h3 class="text-xs font-medium text-gray-500">文件大小</h3>
        <p class="text-sm">{{ formatFileSize(image.file_size) }}</p>
      </div>
      <div>
        <h3 class="text-xs font-medium text-gray-500">拍摄日期</h3>
        <p class="text-sm">{{ formatDate(getExifData('DateTimeOriginal') || getExifData('DateTime') || image.created_at) }}</p>
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
        <h3 class="text-xs font-medium text-gray-500">焦距（等效）</h3>
        <p class="text-sm">
          {{ Math.round(parseFloat(getExifData('FocalLength')) || 0) || 'N/A' }}mm
          <span v-if="getEquivalentFocalLength()" class="text-gray-400">
            ({{ getEquivalentFocalLength() }}mm)
          </span>
        </p>
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
        <p class="text-sm">{{ image.file_path }}</p>
      </div>
      <div class="col-span-2">
        <h3 class="text-xs font-medium text-gray-500">评分</h3>
        <el-rate
          v-model="localRating"
          :max="5"
          :allow-half="false"
          size="small"
          class="mt-1"
          :colors="['#ff6b6b', '#ffa726', '#66bb6a']"
          :void-color="'#e4e7ed'"
          :disabled-void-color="'#e4e7ed'"
          @change="handleRatingChange"
        />
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { ref, watch } from 'vue'
import { API_URLS } from '../../config/api'

const props = defineProps({
  image: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['update-rating'])

const localRating = ref(props.image.rating || 0)

watch(() => props.image.rating, (newRating) => {
  localRating.value = newRating || 0
})

const handleRatingChange = (newRating) => {
  emit('update-rating', newRating)
}

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 获取EXIF数据
const getExifData = (field) => {
  if (props.image.exif_data && props.image.exif_data[field]) {
    return props.image.exif_data[field]
  }
  return null
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  
  // 尝试解析EXIF日期格式 (YYYY:MM:DD HH:MM:SS)
  const exifRegex = /^\d{4}:\d{2}:\d{2} \d{2}:\d{2}:\d{2}$/
  if (exifRegex.test(dateString)) {
    const [datePart, timePart] = dateString.split(' ')
    const [year, month, day] = datePart.split(':')
    const [hour, minute, second] = timePart.split(':')
    const date = new Date(year, month - 1, day, hour, minute, second)
    return date.toLocaleString()
  }
  
  // 尝试解析标准日期格式
  const date = new Date(dateString)
  if (!isNaN(date.getTime())) {
    return date.toLocaleString()
  }
  
  // 如果无法解析，返回原始字符串
  return dateString
}

// 格式化快门速度
const formatShutterSpeed = (exposureTime) => {
  if (!exposureTime) return 'N/A'
  
  // 如果是字符串，先转换为数字
  const time = typeof exposureTime === 'string' ? parseFloat(exposureTime) : exposureTime
  
  if (time < 1) {
    // 小于1秒时转换为分数形式
    const denominator = Math.round(1 / time)
    return `1/${denominator}`
  } else {
    // 大于等于1秒时显示为整数
    return `${Math.round(time)}s`
  }
}

// 获取等效焦距
const getEquivalentFocalLength = () => {
  // 直接使用EXIF中的等效焦距信息
  const focalLengthIn35mmFilm = getExifData('FocalLengthIn35mmFilm')
  if (focalLengthIn35mmFilm) {
    return Math.round(parseFloat(focalLengthIn35mmFilm))
  }
  
  // 如果没有等效焦距信息，返回null
  return null
}

// 格式化尺寸
const formatDimensions = (width, height) => {
  // 检查是否有EXIF方向信息，如果图片是竖直的（方向为6或8），则交换宽高
  if (props.image.exif_data) {
    const orientation = props.image.exif_data.Orientation
    // 方向6和8表示图片需要旋转
    if (orientation === '6' || orientation === '8') {
      // 交换宽高
      if (width && height) {
        return `${height} × ${width}`
      } else {
        // 尝试从EXIF信息获取尺寸
        const exifWidth = props.image.exif_data.Width
        const exifHeight = props.image.exif_data.Height
        if (exifWidth && exifHeight) {
          return `${exifHeight} × ${exifWidth}`
        }
      }
    }
  }
  
  // 默认情况，不交换宽高
  if (width && height) {
    return `${width} × ${height}`
  } else if (props.image.exif_data) {
    // 尝试从EXIF信息获取尺寸
    const exifWidth = props.image.exif_data.Width
    const exifHeight = props.image.exif_data.Height
    if (exifWidth && exifHeight) {
      return `${exifWidth} × ${exifHeight}`
    }
  }
  return 'N/A'
}
</script>