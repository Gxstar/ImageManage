<template>
  <div class="space-y-1">
    <button class="w-full flex items-center space-x-3 px-3 py-2 rounded-button hover:bg-gray-100 text-left">
      <div class="icon-wrapper">
        <font-awesome-icon icon="mountain" class="text-primary" />
      </div>
      <span>旅行记忆</span>
      <span class="ml-auto text-xs text-gray-400">{{ photoCounts.travel || 0 }}</span>
    </button>
    <button class="w-full flex items-center space-x-3 px-3 py-2 rounded-button hover:bg-gray-100 text-left">
      <div class="icon-wrapper">
        <font-awesome-icon icon="utensils" class="text-primary" />
      </div>
      <span>美食日记</span>
      <span class="ml-auto text-xs text-gray-400">{{ photoCounts.food || 0 }}</span>
    </button>
    <button class="w-full flex items-center space-x-3 px-3 py-2 rounded-button hover:bg-gray-100 text-left">
      <div class="icon-wrapper">
        <font-awesome-icon icon="birthday-cake" class="text-primary" />
      </div>
      <span>生日派对</span>
      <span class="ml-auto text-xs text-gray-400">{{ photoCounts.birthday || 0 }}</span>
    </button>
  </div>
</template>

<script setup>
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'

defineProps({
  photoCounts: {
    type: Object,
    default: () => ({
      travel: 0,
      food: 0,
      birthday: 0
    })
  }
})
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