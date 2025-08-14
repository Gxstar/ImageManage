<template>
  <el-card class="w-full" shadow="never">
    <!-- 图片预览 -->
    <div class="mb-3 relative group">
      <el-image
        v-if="image?.id"
        :src="API_URLS.image(image.id)"
        :preview-src-list="[API_URLS.image(image.id)]"
        fit="contain"
        class="w-full h-40 rounded-lg cursor-pointer shadow-sm"
        loading="lazy"
        preview-teleport
        :alt="image.filename"
      >
        <template #placeholder>
          <div class="w-full h-40 bg-gray-100 rounded-lg flex items-center justify-center">
            <i class="el-icon-picture-outline text-gray-400 text-xl"></i>
          </div>
        </template>
      </el-image>
    </div>
    
    <!-- 基本信息区域 -->
    <div class="space-y-3">
      <!-- 文件信息 -->
      <div class="bg-gray-50 rounded-lg p-2.5">
        <h3 class="text-xs font-semibold text-gray-700 mb-1.5 flex items-center">
          <i class="el-icon-document mr-1.5"></i>
          文件信息
        </h3>
        <div class="space-y-0.5 text-xs">
          <div class="flex justify-between">
            <span class="text-gray-600">文件名:</span>
            <span class="font-medium text-gray-800 truncate ml-2">{{ image?.filename || '未知' }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-600">大小:</span>
            <span class="font-medium text-gray-800">{{ formatFileSize(image?.file_size) }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-600">日期:</span>
            <span class="font-medium text-gray-800">{{ formatDate(getPhotoDate()) }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-600">尺寸:</span>
            <span class="font-medium text-gray-800">
              {{ image?.width || 0 }}×{{ image?.height || 0 }}
              <span v-if="image?.width && image?.height" class="text-gray-500 ml-1">
                ({{ formatPixelCount(image.width * image.height) }})
              </span>
            </span>
          </div>
        </div>
      </div>

      <!-- 拍摄参数 -->
        <div class="bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg p-2.5">
          <h3 class="text-xs font-semibold text-gray-700 mb-1.5 flex items-center">
            <i class="el-icon-camera mr-1.5"></i>
            拍摄参数
          </h3>
          <div class="grid grid-cols-2 gap-1.5 text-xs">
            <div>
              <span class="text-gray-600">相机:</span>
              <el-tooltip 
                :content="(getExifData('Make') || '') + ' ' + (getExifData('Model') || '未知')" 
                placement="top" 
                :disabled="!((getExifData('Make') || '') + ' ' + (getExifData('Model') || '')).length || ((getExifData('Make') || '') + ' ' + (getExifData('Model') || '')).length <= 15"
              >
                <div class="font-medium text-gray-800 truncate">{{ getExifData('Make') || '未知' }} {{ getExifData('Model') || '' }}</div>
              </el-tooltip>
            </div>
            <div>
              <span class="text-gray-600">镜头:</span>
              <el-tooltip 
                :content="getExifData('LensModel') || '未知'" 
                placement="top" 
                :disabled="!(getExifData('LensModel') || '').length || (getExifData('LensModel') || '').length <= 15"
              >
                <div class="font-medium text-gray-800 truncate">{{ getExifData('LensModel') || '未知' }}</div>
              </el-tooltip>
            </div>
            <div>
              <span class="text-gray-600">焦距（等效）:</span>
              <div class="font-medium text-gray-800">
                {{ formatFocalLength(getExifData('FocalLength')) || '未知' }}
                <span v-if="getEquivalentFocalLength()" class="text-gray-500 text-xs ml-1">
                  ({{ getEquivalentFocalLength() }}mm)
                </span>
              </div>
            </div>
            <div>
              <span class="text-gray-600">光圈:</span>
              <div class="font-medium text-gray-800">{{ getExifData('FNumber') || '未知' }}</div>
            </div>
            <div>
              <span class="text-gray-600">ISO:</span>
              <div class="font-medium text-gray-800">{{ getExifData('ISO') || getExifData('ISOSpeedRatings') || getExifData('PhotographicSensitivity') || '未知' }}</div>
            </div>
            <div>
              <span class="text-gray-600">快门:</span>
              <div class="font-medium text-gray-800">{{ formatShutterSpeed(getExifData('ExposureTime')) || '未知' }}</div>
            </div>
          </div>
        </div>

      <!-- 文件位置 -->
        <div class="bg-blue-50 rounded-lg p-2.5">
          <h3 class="text-xs font-semibold text-gray-700 mb-1.5 flex items-center">
            <i class="el-icon-folder mr-1.5"></i>
            位置
          </h3>
          <div class="text-xs">
            <el-tooltip 
              :content="image?.file_path || '未知'" 
              placement="top" 
              :disabled="!(image?.file_path || '').length || (image?.file_path || '').length <= 30"
            >
              <div class="bg-white rounded px-1.5 py-1 border text-gray-700 font-mono text-xs break-all leading-tight truncate">
                {{ image?.file_path || '未知' }}
              </div>
            </el-tooltip>
          </div>
        </div>

      <!-- 评分 -->
      <div class="bg-yellow-50 rounded-lg p-2.5">
        <h3 class="text-xs font-semibold text-gray-700 mb-1.5 flex items-center">
          <i class="el-icon-star-on mr-1.5"></i>
          评分
        </h3>
        <div class="flex items-center justify-between">
          <el-rate
            v-model="localRating"
            :max="5"
            :colors="['#FF6B6B', '#FFD166', '#57CC99']"
            :disabled="!image?.id"
            :texts="['算了吧', '有点拉', '还行吧', '挺不错', '绝绝子']"
            show-text
            @change="handleRatingChange"
            size="small"
            class="rating-stars"
          />
          <span class="text-xs font-medium text-gray-700 ml-2">{{ localRating || 0 }}</span>
        </div>
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

// 获取照片日期（优先EXIF拍摄日期，其次文件创建时间）
const getPhotoDate = () => {
  // 优先从EXIF数据获取拍摄日期
  const dateFields = ['DateTimeOriginal', 'DateTime', 'DateTimeDigitized']
  
  for (const field of dateFields) {
    const exifDate = getExifData(field)
    if (exifDate) {
      return exifDate
    }
  }
  
  // 如果没有EXIF日期，使用文件创建时间
  if (props.image.created_at) {
    return props.image.created_at
  }
  
  // 最后使用文件修改时间
  if (props.image.modified_at) {
    return props.image.modified_at
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
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  }
  
  // 尝试解析标准日期格式
  const date = new Date(dateString)
  if (!isNaN(date.getTime())) {
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  }
  
  // 如果无法解析，返回原始字符串
  return dateString
}

// 格式化快门速度
const formatShutterSpeed = (exposureTime) => {
  if (!exposureTime) return null
  
  try {
    // 处理常见的EXIF格式
    const time = parseFloat(exposureTime)
    if (isNaN(time)) return exposureTime
    
    if (time >= 1) {
      return `${time}s`
    } else {
      // 转换为分数形式，如1/125
      const denominator = Math.round(1 / time)
      return `1/${denominator}s`
    }
  } catch (error) {
    return exposureTime
  }
}

// 格式化焦距，确保只显示整数
const formatFocalLength = (focalLength) => {
  if (!focalLength) return null
  
  try {
    // 处理常见的EXIF格式，如"24.0 mm"或"24"
    const value = parseFloat(focalLength)
    if (isNaN(value)) return focalLength
    
    return Math.round(value) + 'mm'
  } catch (error) {
    return focalLength
  }
}

// 格式化像素数量
const formatPixelCount = (totalPixels) => {
  if (!totalPixels || totalPixels === 0) return '0像素'
  
  // 转换为百万像素
  const megaPixels = totalPixels / 1000000
  
  if (megaPixels >= 1000) {
    return Math.round(megaPixels) + 'MP'
  } else if (megaPixels >= 100) {
    return megaPixels.toFixed(0) + 'MP'
  } else if (megaPixels >= 10) {
    return megaPixels.toFixed(1) + 'MP'
  } else {
    return megaPixels.toFixed(2) + 'MP'
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

<style scoped>
/* 评分星星样式增强 */
:deep(.rating-stars .el-rate__item .el-rate__icon) {
  font-size: 16px;
  margin-right: 2px;
}

:deep(.rating-stars .el-rate__item:hover .el-rate__icon) {
  transform: scale(1.1);
  transition: transform 0.2s ease;
}
</style>