<template>
  <button class="w-full flex items-center space-x-3 px-3 py-2 rounded-button hover:bg-gray-100 text-left">
    <div class="icon-wrapper">
      <font-awesome-icon icon="cog" class="text-primary" />
    </div>
    <span>设置</span>
  </button>
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