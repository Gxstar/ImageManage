<template>
  <div class="flex items-center justify-between px-6 py-2 bg-white border-b border-dashed border-gray-200 shadow-sm">
    <!-- 左侧路径信息 -->
    <div class="flex items-center space-x-3">
      <div class="flex items-center justify-center w-8 h-8 bg-gradient-to-br from-blue-50 to-indigo-100 rounded-lg">
        <font-awesome-icon 
          :icon="locationIcon" 
          class="text-sm text-primary"
        />
      </div>
      <div class="flex flex-col">
        <span class="text-sm font-semibold text-gray-800 tracking-wide">{{ currentLocation }}</span>
        <span v-if="imageCount > 0" class="text-xs text-gray-500 font-medium">
          {{ imageCount }} 张照片
        </span>
      </div>
    </div>

    <!-- 右侧刷新按钮 -->
    <div class="flex items-center space-x-2">
      <el-tooltip 
        content="刷新图片列表" 
        placement="top"
        effect="light"
        :enterable="false"
      >
        <button
          @click="triggerScan"
          :disabled="isScanning"
          class="relative flex items-center justify-center w-10 h-10 bg-gray-50 hover:bg-gray-100 rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <font-awesome-icon 
            icon="sync-alt" 
            class="text-sm text-gray-600 hover:text-indigo-600 transition-colors duration-200"
            :class="{ 'animate-spin': isScanning }"
          />
        </button>
      </el-tooltip>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'

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
  },
  selectedAlbum: {
    type: [Number, String],
    default: null
  },
  albumName: {
    type: String,
    default: ''
  },
  imageCount: {
    type: Number,
    default: 0
  }
})

const emit = defineEmits(['refresh'])

const isScanning = ref(false)

// 计算当前位置显示文本
const currentLocation = computed(() => {
  if (props.selectedAlbum && props.albumName) {
    return props.albumName
  } else if (props.showFavorites) {
    return '收藏夹'
  } else if (props.showAllPhotos) {
    return '全部照片'
  } else if (props.directoryPath) {
    // 显示目录名或完整路径
    const pathParts = props.directoryPath.split(/[/\\]/)
    return pathParts[pathParts.length - 1] || props.directoryPath
  } else {
    return '未选择目录'
  }
})

// 计算当前位置的图标
const locationIcon = computed(() => {
  if (props.selectedAlbum) {
    return 'photo-video'
  } else if (props.showFavorites) {
    return 'heart'
  } else if (props.showAllPhotos) {
    return 'images'
  } else if (props.directoryPath) {
    return 'folder'
  } else {
    return 'question-circle'
  }
})

// 触发后台扫描
const triggerScan = async () => {
  if (isScanning.value) return
  
  isScanning.value = true
  try {
    const result = await window.pywebview.api.trigger_background_scan()
    if (result.success) {
      // 扫描完成后刷新图片列表
      emit('refresh')
      // 显示成功提示
      if (window.pywebview) {
        // 使用Element Plus的message
        const { ElMessage } = window.ElementPlus || {}
        if (ElMessage) {
          ElMessage.success(`扫描完成，共处理 ${result.processed} 个文件`)
        } else {
          console.log(`扫描完成，共处理 ${result.processed} 个文件`)
        }
      }
    } else {
      throw new Error(result.error || '扫描失败')
    }
  } catch (error) {
    console.error('触发扫描失败:', error)
    // 显示错误提示
    if (window.pywebview) {
      const { ElMessage } = window.ElementPlus || {}
      if (ElMessage) {
        ElMessage.error(`扫描失败: ${error.message}`)
      } else {
        console.error(`扫描失败: ${error.message}`)
      }
    }
  } finally {
    isScanning.value = false
  }
}
</script>

<style scoped>
.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* 图标悬停效果 */
.font-awesome-icon {
  transition: all 0.2s ease;
}

/* 按钮悬停效果增强 */
button:hover .font-awesome-icon {
  transform: scale(1.1);
}

button:active .font-awesome-icon {
  transform: scale(0.95);
}

/* 文字渐变效果 */
.text-sm.font-semibold {
  background: linear-gradient(135deg, #1f2937, #4b5563);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
</style>