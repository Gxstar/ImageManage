<template>
  <div class="p-4 border-b border-gray-200">
    <h3 class="font-medium mb-3">快速操作</h3>
    <div class="grid grid-cols-2 gap-2">
      <button 
        @click="handleAction('edit')"
        class="py-2 rounded-button bg-white border border-gray-200 hover:border-primary hover:bg-primary/5 flex items-center justify-center space-x-2 transition-colors duration-200"
      >
        <font-awesome-icon icon="edit" class="text-gray-500" />
        <span>编辑</span>
      </button>
      <button 
        @click="handleAction('share')"
        class="py-2 rounded-button bg-white border border-gray-200 hover:border-primary hover:bg-primary/5 flex items-center justify-center space-x-2 transition-colors duration-200"
      >
        <font-awesome-icon icon="share-alt" class="text-gray-500" />
        <span>分享</span>
      </button>
      <button 
        @click="handleAction('delete')"
        class="py-2 rounded-button bg-white border border-gray-200 hover:border-primary hover:bg-primary/5 flex items-center justify-center space-x-2 transition-colors duration-200"
      >
        <font-awesome-icon icon="trash-alt" class="text-gray-500" />
        <span>删除</span>
      </button>
      <button 
        @click="handleAction('tags')"
        class="py-2 rounded-button bg-white border border-gray-200 hover:border-primary hover:bg-primary/5 flex items-center justify-center space-x-2 transition-colors duration-200"
      >
        <font-awesome-icon icon="tags" class="text-gray-500" />
        <span>标签</span>
      </button>
    </div>
  </div>
</template>

<script setup>
const emit = defineEmits(['action']);

const handleAction = (action) => {
  emit('action', action);
};
</script>