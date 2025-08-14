<template>
  <div class="mb-6">
    <div class="flex items-center justify-between mb-3">
      <h2 class="text-sm font-semibold text-gray-700">本地目录</h2>
      <div class="flex items-center space-x-2">
        <button @click="$emit('loadDirectories')" class="text-primary hover:text-gray-700" title="刷新目录">
          <font-awesome-icon icon="sync-alt" class="w-4 h-4" />
        </button>
        <button @click="$emit('addLocalDirectory')" class="text-primary hover:text-gray-700">
          <font-awesome-icon icon="plus" class="w-4 h-4" />
        </button>
      </div>
    </div>

    <!-- 显示目录列表 -->
    <div v-if="Object.keys(directories).length > 0">
      <div v-for="(dir, dirPath) in directories" :key="dirPath">
        <div @contextmenu.prevent="$emit('showDirectoryContextMenu', $event, dir.path)" :class="[
          'w-full flex items-center justify-between p-2 rounded-lg hover:bg-gray-100 transition-colors group cursor-pointer',
          { 'bg-primary/10': selectedDirectory === dir.path }
        ]">
          <div class="flex items-center flex-grow" @click="$emit('selectDirectory', dir.path)">
            <button @click.stop="toggleDirectoryExpansion(dir)"
              class="mr-2 opacity-0 group-hover:opacity-100 text-gray-400 hover:text-gray-600">
              <font-awesome-icon icon="chevron-down" class="w-4 h-4 transition-transform"
                :class="{ 'transform rotate-180': dir.expanded }" />
            </button>
            <font-awesome-icon icon="folder" class="w-4 h-4 mr-2 text-primary" />
            <span class="text-sm">{{ dir.name }}</span>
          </div>
          <div class="flex items-center space-x-2">
            <span class="text-xs text-gray-400">{{ photoCounts.directories[dir.path] || 0 }}</span>
            <button @click.stop="$emit('removeDirectory', dir.path)"
              class="opacity-0 group-hover:opacity-100 text-gray-400 hover:text-red-600">
              <font-awesome-icon icon="times" class="h-4 w-4" />
            </button>
          </div>
        </div>

        <!-- 展开的子目录 (递归显示) -->
        <div v-show="dir.expanded">
          <div class="ml-4 border-l-2 border-gray-200 pl-2">
            <RecursiveSubDirectory :directories="dir.subdirectories" :selectedDirectory="selectedDirectory"
              :photoCounts="photoCounts"
              @select-directory="$emit('selectDirectory', $event)" 
              @show-context-menu="$emit('showDirectoryContextMenu', $event)" 
              @remove-directory="$emit('removeDirectory', $event)" />
          </div>
        </div>
      </div>
    </div>

    <!-- 如果没有目录，显示提示信息 -->
    <div v-else class="text-center py-4 text-primary text-sm">
      <p>暂无目录</p>
      <p class="mt-1">点击上方 + 按钮添加目录</p>
    </div>
  </div>
</template>

<script setup>
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import RecursiveSubDirectory from './RecursiveSubDirectory.vue'

defineProps({
  directories: {
    type: Object,
    default: () => ({})
  },
  selectedDirectory: {
    type: String,
    default: ''
  },
  photoCounts: {
    type: Object,
    default: () => ({
      directories: {}
    })
  }
})

const emit = defineEmits([
  'loadDirectories', 
  'addLocalDirectory', 
  'selectDirectory', 
  'showDirectoryContextMenu', 
  'removeDirectory'
])

const toggleDirectoryExpansion = async (dir) => {
  if (dir.has_subdirs && (!dir.subdirectories || dir.subdirectories.length === 0)) {
    // 懒加载子目录
    try {
      const result = await window.pywebview.api.get_directory_tree(dir.path, 1);
      if (result && result.tree && result.tree[0]) {
        dir.subdirectories = result.tree[0].children || [];
      }
    } catch (error) {
      console.error('加载子目录失败:', error);
    }
  }
  if (dir) {
    dir.expanded = !dir.expanded;
  }
};
</script>