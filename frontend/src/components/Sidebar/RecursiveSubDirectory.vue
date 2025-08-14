<template>
  <div class="recursive-subdirectory">
    <div v-for="node in directories" :key="node.path">
      <!-- 目录节点 -->
      <div v-if="node.type === 'directory'" 
        @contextmenu.prevent="$emit('show-context-menu', $event, node.path)"
        :class="[
          'w-full flex items-center justify-between p-2 rounded-lg hover:bg-gray-100 transition-colors group cursor-pointer',
          { 'bg-primary/10': selectedDirectory === node.path }
        ]">
        <div class="flex items-center flex-grow" @click="$emit('select-directory', node.path)">
          <button @click.stop="toggleDirectoryExpansion(node)"
            :class="[
              'mr-2 text-gray-400 hover:text-gray-600',
              { 'opacity-0 group-hover:opacity-100': !node.has_subdirs, 'opacity-100': node.has_subdirs }
            ]">
            <font-awesome-icon icon="chevron-down" 
              class="w-4 h-4 transition-transform"
              :class="{ 'transform rotate-180': node.expanded }" />
          </button>
          <font-awesome-icon icon="folder" class="w-4 h-4 mr-2 text-primary" />
          <span class="text-sm">{{ node.name }}</span>
        </div>
        <div class="flex items-center space-x-2">
          <span class="text-xs text-gray-400">{{ node.image_count || 0 }}</span>
          <button @click.stop="$emit('remove-directory', node.path)"
            class="opacity-0 group-hover:opacity-100 text-gray-400 hover:text-red-600">
            <font-awesome-icon icon="times" class="h-4 w-4" />
          </button>
        </div>
      </div>

      <!-- 图片节点 -->
      <div v-else-if="node.type === 'image'" 
        @click="$emit('select-directory', node.path)"
        :class="[
          'w-full flex items-center p-2 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer',
          { 'bg-primary/10': selectedDirectory === node.path }
        ]">
        <font-awesome-icon icon="image" class="w-4 h-4 mr-2 text-gray-500" />
        <span class="text-sm text-gray-700 flex-1">{{ node.name }}</span>
        <span class="text-xs text-gray-400 ml-2">{{ node.image_count || 0 }}</span>
      </div>

      <!-- 展开的子目录 -->
      <div v-if="node.type === 'directory' && node.expanded && node.has_subdirs"
        class="ml-4 border-l-2 border-gray-200 pl-2">
        <RecursiveSubDirectory 
          :directories="node.subdirectories || []"
          :selectedDirectory="selectedDirectory"
          :photoCounts="photoCounts"
          @select-directory="$emit('select-directory', $event)"
          @show-context-menu="$emit('show-context-menu', $event)"
          @remove-directory="$emit('remove-directory', $event)" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'

defineProps({
  directories: {
    type: Array,
    default: () => []
  },
  selectedDirectory: {
    type: String,
    default: ''
  },
  photoCounts: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits([
  'select-directory', 
  'show-context-menu', 
  'remove-directory'
])

const toggleDirectoryExpansion = async (node) => {
  if (node.has_subdirs && (!node.subdirectories || node.subdirectories.length === 0)) {
    try {
      const result = await window.pywebview.api.get_directory_tree(node.path, 1);
      if (result && result.tree && result.tree[0]) {
        node.subdirectories = result.tree[0].children || [];
      }
    } catch (error) {
      console.error('加载子目录失败:', error);
    }
  }
  if (node) {
    node.expanded = !node.expanded;
  }
};
</script>