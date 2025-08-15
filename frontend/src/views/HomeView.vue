<template>
  <div class="home-container flex h-screen bg-gray-50  border-t border-solid">
    <!-- 侧边栏 -->
    <Sidebar 
      :selectedDirectory="selectedDirectory" 
      :showAllPhotos="showAllPhotos"
      :showFavorites="showFavorites"
      :photoCounts="photoCounts"
      @update:selectedDirectory="updateSelectedDirectory" 
      @showAllPhotos="handleShowAllPhotos" 
      @showFavorites="handleShowFavorites"
      @directoriesLoaded="handleDirectoriesLoaded"
      @photoCountsChanged="loadPhotoCounts"
      @select-album="selectAlbum"
    />
    <!-- 照片网格 -->
    <PhotoGrid 
      ref="photoGridRef"
      :directoryPath="selectedDirectory" 
      :showAllPhotos="showAllPhotos" 
      :showFavorites="showFavorites"
      :selectedAlbum="selectedAlbum"
      @select-image="updateSelectedImage" 
      @image-count-changed="loadPhotoCounts"
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
import { ref, onMounted } from 'vue'
import Sidebar from '../components/Sidebar.vue'
import PhotoGrid from '../components/PhotoGrid.vue'
import InfoPanel from '../components/InfoPanel.vue'

// 响应式数据
const selectedDirectory = ref('')
const selectedImage = ref(null)
const showAllPhotos = ref(true)
const showFavorites = ref(false)
const selectedAlbum = ref(null)
const photoGridRef = ref(null)
const photoCounts = ref({
  allPhotos: 0,
  favorites: 0,
  directories: {},
  travel: 0,
  food: 0,
  birthday: 0,
  family: 0
})

// 方法定义
const updateSelectedDirectory = (path) => {
  selectedDirectory.value = path
  // 当选择特定目录时，关闭全部照片和收藏夹模式
  showAllPhotos.value = false
  showFavorites.value = false
  selectedAlbum.value = null
}

const updateSelectedImage = (image) => {
  selectedImage.value = image
}

// 当目录加载完成后，刷新全部照片和计数
const handleDirectoriesLoaded = () => {
  if (photoGridRef.value) {
    // 目录加载完成后，刷新PhotoGrid
    photoGridRef.value.refresh()
  }
  // 同时刷新照片计数
  loadPhotoCounts()
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
  showFavorites.value = false
  selectedAlbum.value = null
  // 清空selectedDirectory，避免与全部照片模式冲突
  selectedDirectory.value = ''
}

const handleShowFavorites = () => {
  // 设置显示收藏夹模式
  showFavorites.value = true
  showAllPhotos.value = false
  selectedAlbum.value = null
  // 清空selectedDirectory，避免与收藏夹模式冲突
  selectedDirectory.value = ''
}

const selectAlbum = (albumId) => {
  // 设置相册模式
  selectedAlbum.value = albumId
  showAllPhotos.value = false
  showFavorites.value = false
  selectedDirectory.value = ''
}

// 加载照片计数
const loadPhotoCounts = async () => {
  try {
    const counts = await window.pywebview.api.get_photo_counts();
    if (counts) {
      photoCounts.value = {
        allPhotos: counts.all_photos || 0,
        favorites: counts.favorites || 0,
        directories: counts.directories || {},
        travel: counts.travel || 0,
        food: counts.food || 0,
        birthday: counts.birthday || 0,
        family: counts.family || 0
      };
    }
  } catch (error) {
    console.error('加载照片计数失败:', error);
  }
}

// 生命周期钩子
onMounted(() => {
  loadPhotoCounts();
})
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