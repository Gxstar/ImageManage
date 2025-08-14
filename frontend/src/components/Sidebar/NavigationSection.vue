<template>
  <div class="px-4 space-y-1">
    <button @click="$emit('showAllPhotos')"
      class="w-full flex items-center space-x-3 px-3 py-2 rounded-button hover:bg-gray-100 text-left"
      :class="{ 'bg-primary/10': showAllPhotos }">
      <div class="icon-wrapper">
        <font-awesome-icon icon="images" class="text-primary" />
      </div>
      <span>全部照片</span>
      <span class="ml-auto text-xs text-gray-400">{{ photoCounts.allPhotos || 0 }}</span>
    </button>
    <button @click="$emit('showFavorites')"
      class="w-full flex items-center space-x-3 px-3 py-2 rounded-button hover:bg-gray-100 text-left"
      :class="{ 'bg-primary/10': showFavorites }">
      <div class="icon-wrapper">
        <font-awesome-icon icon="star" class="text-primary" />
      </div>
      <span>收藏夹</span>
      <span class="ml-auto text-xs text-gray-400">{{ photoCounts.favorites || 0 }}</span>
    </button>
  </div>
</template>

<script setup>
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'

defineProps({
  showAllPhotos: {
    type: Boolean,
    default: true
  },
  showFavorites: {
    type: Boolean,
    default: false
  },
  photoCounts: {
    type: Object,
    default: () => ({
      allPhotos: 0,
      favorites: 0
    })
  }
})

defineEmits(['showAllPhotos', 'showFavorites'])
</script>

<style scoped>
.icon-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 24px;
  height: 24px;
}
</style>