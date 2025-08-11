<template>
  <div class="home-container flex h-screen bg-gray-50">
    <!-- 侧边栏 -->
    <Sidebar 
      :selectedDirectory="selectedDirectory" 
      @update:selectedDirectory="updateSelectedDirectory" 
      @showAllPhotos="handleShowAllPhotos" 
      @directoriesLoaded="handleDirectoriesLoaded"
    />
    <!-- 照片网格 -->
    <PhotoGrid 
      ref="photoGridRef"
      :directoryPath="selectedDirectory" 
      :showAllPhotos="showAllPhotos" 
      @select-image="updateSelectedImage" 
      :has-info-panel="!!selectedImage" 
    />
    <!-- 信息面板 -->
    <InfoPanel 
      v-if="selectedImage" 
      :image="selectedImage" 
      @update-image="updateImageInfo" 
      @close="selectedImage = null" 
      class="z-40" 
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Sidebar from '../components/Sidebar.vue'
import PhotoGrid from '../components/PhotoGrid.vue'
import InfoPanel from '../components/InfoPanel.vue'

// 响应式数据
const selectedDirectory = ref('')
const selectedImage = ref(null)
const showAllPhotos = ref(true)
const photoGridRef = ref(null)

// 方法定义
const updateSelectedDirectory = (path) => {
  selectedDirectory.value = path
  // 当选择特定目录时，关闭全部照片模式
  showAllPhotos.value = false
}

const updateSelectedImage = (image) => {
  selectedImage.value = image
}

// 当目录加载完成后，刷新全部照片
const handleDirectoriesLoaded = () => {
  if (showAllPhotos.value && photoGridRef.value) {
    // 如果当前是全部照片模式，重新加载
    photoGridRef.value.refresh()
  }
}

const updateImageInfo = async (updatedImage) => {
  try {
    // 通过IPC调用更新图片信息
    const result = await window.electronAPI?.updateImageInfo(updatedImage)
    if (result?.success) {
      // 更新成功，更新本地状态
      selectedImage.value = updatedImage
      console.log('图片信息更新成功')
    } else {
      console.error('图片信息更新失败:', result?.error)
    }
  } catch (error) {
    console.error('更新图片信息时出错:', error)
  }
}

const handleShowAllPhotos = () => {
  // 设置显示全部照片模式
  showAllPhotos.value = true
  // 清空selectedDirectory，避免与全部照片模式冲突
  selectedDirectory.value = ''
}
</script>

<style scoped>
.home-container {
  width: 100%;
  overflow: hidden;
}

/* 全局样式 */
.rounded-button {
  border-radius: 6px;
}
</style>