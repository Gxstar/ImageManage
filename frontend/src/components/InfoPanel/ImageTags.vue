<template>
  <div class="p-4">
    <h3 class="font-medium mb-3">应用标签</h3>
    <div class="flex flex-wrap gap-2 mb-4">
      <span 
        v-for="tag in (image.tags || [])" 
        :key="tag" 
        class="px-3 py-1 bg-primary/10 text-primary rounded-full text-sm flex items-center space-x-1 cursor-pointer hover:bg-primary/20 transition-colors duration-200"
        @click="handleRemoveTag(tag)"
      >
        <span>{{ tag }}</span>
        <font-awesome-icon icon="times-circle" />
      </span>
    </div>
    <div v-if="image.category">
      <h3 class="font-medium mb-3">分类</h3>
      <div class="px-3 py-1 bg-primary/10 text-primary rounded-full text-sm inline-block">
        {{ image.category }}
      </div>
    </div>
    <button 
      @click="handleCreateAlbum"
      class="w-full py-2 rounded-button bg-white border border-dashed border-gray-300 hover:border-primary hover:bg-primary/5 flex items-center justify-center space-x-2 transition-colors duration-200"
    >
      <font-awesome-icon icon="plus" class="text-gray-400" />
      <span>新建相册</span>
    </button>
  </div>
</template>

<script setup>
const props = defineProps({
  image: {
    type: Object,
    required: true
  }
});

const emit = defineEmits(['remove-tag', 'create-album']);

const handleRemoveTag = (tag) => {
  emit('remove-tag', tag);
};

const handleCreateAlbum = () => {
  emit('create-album');
};
</script>