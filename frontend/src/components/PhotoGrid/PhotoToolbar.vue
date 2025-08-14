<template>
  <div class="toolbar p-3 border-b border-gray-200 bg-white">
    <div class="flex items-center space-x-4">
      <div class="flex items-center space-x-2">
        <label class="text-sm font-medium text-gray-700">缩略图:</label>
        <select
          v-model="localThumbnailSize"
          class="text-sm border border-gray-300 rounded-md px-2 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option :value="80">小</option>
          <option :value="120">中</option>
          <option :value="160">大</option>
        </select>
      </div>
      
      <!-- 评分筛选 -->
      <div class="flex items-center space-x-2">
        <label class="text-sm font-medium text-gray-700">评分:</label>
        <el-rate
          v-model="localRatingFilter"
          :max="5"
          :allow-half="false"
          size="small"
          :colors="['#ff6b6b', '#ffa726', '#66bb6a']"
          :void-color="'#e4e7ed'"
          :clearable="true"
          @change="handleRatingChange"
        />
        <el-button 
          v-if="localRatingFilter > 0"
          type="text" 
          size="small" 
          @click="clearRatingFilter"
          class="ml-1"
        >
          清除
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  thumbnailSize: {
    type: Number,
    default: 100
  },
  ratingFilter: {
    type: Number,
    default: 0
  }
})

const emit = defineEmits(['update:thumbnailSize', 'update:ratingFilter', 'ratingChange'])

const localThumbnailSize = ref(props.thumbnailSize)
const localRatingFilter = ref(props.ratingFilter)

watch(() => props.thumbnailSize, (newVal) => {
  localThumbnailSize.value = newVal
})

watch(() => props.ratingFilter, (newVal) => {
  localRatingFilter.value = newVal
})

watch(localThumbnailSize, (newVal) => {
  emit('update:thumbnailSize', newVal)
})

const handleRatingChange = () => {
  emit('update:ratingFilter', localRatingFilter.value)
  emit('ratingChange')
}

const clearRatingFilter = () => {
  localRatingFilter.value = 0
  handleRatingChange()
}
</script>