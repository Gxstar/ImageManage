<template>
  <div class="space-y-1">
    <button class="w-full flex items-center space-x-3 px-3 py-2 rounded-button hover:bg-gray-100 text-left">
      <div class="icon-wrapper">
        <font-awesome-icon icon="user" class="text-primary" />
      </div>
      <span>人物</span>
    </button>
    <button class="w-full flex items-center space-x-3 px-3 py-2 rounded-button hover:bg-gray-100 text-left">
      <div class="icon-wrapper">
        <font-awesome-icon icon="map-marker-alt" class="text-primary" />
      </div>
      <span>地点</span>
    </button>
    <button class="w-full flex items-center space-x-3 px-3 py-2 rounded-button hover:bg-gray-100 text-left">
      <div class="icon-wrapper">
        <font-awesome-icon icon="calendar-alt" class="text-primary" />
      </div>
      <span>时间线</span>
    </button>
  </div>
</template>

<script setup>
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
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