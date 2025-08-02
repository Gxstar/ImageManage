<template>
  <div class="app-container flex h-screen bg-gray-50">
    <!-- 侧边栏 -->
    <Sidebar :selectedDirectory="selectedDirectory" @update:selectedDirectory="updateSelectedDirectory" @showAllPhotos="handleShowAllPhotos" />
    <!-- 照片网格 -->
    <PhotoGrid :directoryPath="selectedDirectory" :showAllPhotos="showAllPhotos" @select-image="updateSelectedImage" :has-info-panel="!!selectedImage" />
    <!-- 信息面板 -->
    <InfoPanel v-if="selectedImage" :image="selectedImage" @update-image="updateImageInfo" @close="selectedImage = null" class="z-40" />
  </div>
</template>

<script>
import Sidebar from './components/Sidebar.vue'
import PhotoGrid from './components/PhotoGrid.vue'
import InfoPanel from './components/InfoPanel.vue'

export default {
  name: 'App',
  components: {
    Sidebar,
    PhotoGrid,
    InfoPanel
  },
  data() {
    return {
      selectedDirectory: '',
      selectedImage: null,
      showAllPhotos: true
    };
  },
  methods: {
    updateSelectedDirectory(path) {
      this.selectedDirectory = path;
      // 当选择特定目录时，关闭全部照片模式
      this.showAllPhotos = false;
    },
    updateSelectedImage(image) {
      this.selectedImage = image;
    },
    async updateImageInfo(updatedImage) {
      try {
        // 通过IPC调用更新图片信息
        const result = await window.electronAPI.updateImageInfo(updatedImage);
        if (result.success) {
          // 更新成功，更新本地状态
          this.selectedImage = updatedImage;
          
          // 如果需要，也可以通知用户更新成功
          console.log('图片信息更新成功');
        } else {
          console.error('图片信息更新失败:', result.error);
        }
      } catch (error) {
        console.error('更新图片信息时出错:', error);
      }
    },
    handleShowAllPhotos() {
      // 设置显示全部照片模式
      this.showAllPhotos = true;
      // 清空selectedDirectory，避免与全部照片模式冲突
      this.selectedDirectory = '';
    }
  }
}
</script>

<style>
.app-container {
  width: 100%;
  overflow: hidden;
}
/* 全局样式 */
.rounded-button {
  border-radius: 6px;
}
</style>
