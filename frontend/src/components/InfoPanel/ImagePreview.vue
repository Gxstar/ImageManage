<template>
  <div class="p-4 border-b border-gray-200">
    <el-image
      v-if="image?.id"
      :src="API_URLS.image(image.id)"
      :preview-src-list="[API_URLS.image(image.id)]"
      fit="scale-down"
      class="w-full h-48 rounded-button cursor-pointer"
      loading="lazy"
      preview-teleport
      :alt="image.filename"
    />
  </div>
</template>

<script setup>
import { API_URLS } from '../../config/api';

const props = defineProps({
  image: {
    type: Object,
    required: true
  }
});
</script>