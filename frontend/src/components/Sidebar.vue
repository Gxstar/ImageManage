<template>
  <div class="sidebar bg-white border-r border-gray-200 flex flex-col h-full">
    <div class="p-4 border-b border-gray-200">
      <div class="flex items-center space-x-2">
        <div class="w-8 h-8 bg-primary rounded-button flex items-center justify-center">
          <font-awesome-icon icon="camera" class="text-white text-sm" />
        </div>
        <span class="font-['Pacifico'] text-xl text-gray-800">照片管理器</span>
      </div>
    </div>
    <div class="flex-1 overflow-y-auto py-4">
      <!-- 导航部分 -->
      <NavigationSection 
        :showAllPhotos="props.showAllPhotos"
        :showFavorites="props.showFavorites"
        :photoCounts="photoCounts"
        @showAllPhotos="showAllPhotos"
        @showFavorites="showFavorites" />

      <div class="px-4 mt-6">
        <!-- 本地目录 -->
        <LocalDirectorySection 
          :directories="directories"
          :selectedDirectory="props.selectedDirectory"
          :photoCounts="photoCounts"
          @loadDirectories="loadDirectories"
          @addLocalDirectory="addLocalDirectory"
          @selectDirectory="selectDirectory"
          @showDirectoryContextMenu="showDirectoryContextMenu"
          @removeDirectory="removeDirectory" />

        <!-- 相册部分 -->
        <AlbumSection 
          ref="albumSectionRef"
          :photoCounts="photoCounts" 
          @select-album="selectAlbum"
          @album-changed="handleAlbumChanged" />
      </div>

      <!-- 智能分类部分 -->
      <div class="px-4 mt-6">
        <div class="flex items-center justify-between mb-2">
          <h3 class="text-xs font-semibold text-gray-400 uppercase tracking-wider">智能分类</h3>
        </div>
        <SmartCategorySection />
      </div>
    </div>
    <div class="p-4 border-t border-gray-200">
      <SettingsSection />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import NavigationSection from './Sidebar/NavigationSection.vue'
import LocalDirectorySection from './Sidebar/LocalDirectorySection.vue'
import AlbumSection from './Sidebar/AlbumSection.vue'
import SmartCategorySection from './Sidebar/SmartCategorySection.vue'
import SettingsSection from './Sidebar/SettingsSection.vue'

// Props 定义
const props = defineProps({
  selectedDirectory: {
    type: String,
    default: ''
  },
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
      favorites: 0,
      directories: {},
      travel: 0,
      food: 0,
      birthday: 0,
      family: 0
    })
  }
});

// Emits 定义
const emit = defineEmits(['update:selectedDirectory', 'showContextMenu', 'showAllPhotos', 'showFavorites', 'directoriesLoaded', 'photoCountsChanged', 'select-album']);

// 响应式数据
const directories = ref({});
const albumSectionRef = ref(null);

// 选择目录
const selectDirectory = (path) => {
  emit('update:selectedDirectory', path);
  // 清除相册选择
  if (albumSectionRef.value) {
    albumSectionRef.value.clearSelection();
  }
};

// 选择相册
const selectAlbum = (albumId) => {
  emit('update:selectedDirectory', ''); // 清除目录选择
  emit('select-album', albumId);
};

// 处理相册变化
const handleAlbumChanged = () => {
  emit('photoCountsChanged');
};

// 显示目录右键菜单
const showDirectoryContextMenu = (event, path) => {
  event.preventDefault();
  emit('showContextMenu', { event, path, type: 'directory' });
};



// 转换新的目录树结构数据格式
const convertDirectoryStructure = (treeNode) => {
  if (!treeNode) return null;

  return {
    name: treeNode.name,
    path: treeNode.path,
    type: treeNode.type,
    expanded: false,
    image_count: treeNode.image_count || 0,
    has_subdirs: treeNode.has_subdirs || false,
    subdirectories: treeNode.children ? treeNode.children
      .filter(child => child.type === 'directory')
      .map(convertDirectoryStructure)
      .filter(Boolean) : []
  };
};

// 添加本地目录
const addLocalDirectory = async () => {
  try {
    const selectedDir = await window.pywebview.api.add_directory();
    if (selectedDir && selectedDir.success) {
      // 重新加载目录
      await loadDirectories();
      // 通知父组件计数已改变
      emit('photoCountsChanged');
    }
  } catch (error) {
    console.error('添加目录失败:', error);
  }
};

// 移除目录
const removeDirectory = async (directoryPath) => {
  // 显示确认对话框
  if (!confirm('确定要移除这个目录吗？')) {
    return;
  }

  try {
    const result = await window.pywebview.api.remove_directory(directoryPath);
    if (result && result.success) {
      await loadDirectories();
      // 通知父组件计数已改变
      emit('photoCountsChanged');
    }
  } catch (error) {
    console.error('移除目录失败:', error);
  }
};

// 显示全部照片
const showAllPhotos = () => {
  emit('showAllPhotos');
};

// 显示收藏夹
const showFavorites = () => {
  emit('showFavorites');
};

// 从后端加载目录树结构
const loadDirectories = async () => {
  try {
    // 直接从后端获取目录树
    const treeResult = await window.pywebview.api.get_directory_tree(null, 2);
    
    if (treeResult && treeResult.tree && Array.isArray(treeResult.tree)) {
      const convertedDirs = treeResult.tree.map(convertDirectoryStructure).filter(Boolean);
      
      const newDirectories = {};
      convertedDirs.forEach(dir => {
        newDirectories[dir.path] = dir;
      });

      directories.value = newDirectories;
      emit('directoriesLoaded');
    } else {
      directories.value = {};
      emit('directoriesLoaded');
    }
  } catch (error) {
    console.error('加载目录失败:', error);
    directories.value = {};
    emit('directoriesLoaded');
  }
};

// 生命周期钩子
onMounted(async () => {
  loadDirectories();
});
</script>

<style scoped>
.sidebar {
  min-width: 200px;
  max-width: 250px;
}

.icon-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 24px;
  height: 24px;
}
</style>