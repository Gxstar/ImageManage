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
      <div class="px-4 space-y-1">
            <button @click="showAllPhotos"
              class="w-full flex items-center space-x-3 px-3 py-2 rounded-button hover:bg-gray-100 text-left"
              :class="{ 'bg-primary/10': props.showAllPhotos }">
              <div class="icon-wrapper">
                <font-awesome-icon icon="images" class="text-primary" />
              </div>
              <span>全部照片</span>
              <span class="ml-auto text-xs text-gray-400">{{ photoCounts.allPhotos || 0 }}</span>
            </button>
            <button @click="showFavorites"
              class="w-full flex items-center space-x-3 px-3 py-2 rounded-button hover:bg-gray-100 text-left"
              :class="{ 'bg-primary/10': props.showFavorites }">
              <div class="icon-wrapper">
                <font-awesome-icon icon="star" class="text-primary" />
              </div>
              <span>收藏夹</span>
              <span class="ml-auto text-xs text-gray-400">{{ photoCounts.favorites || 0 }}</span>
            </button>
          </div>
      <div class="px-4 mt-6">
        <!-- 本地目录 -->
        <div class="mb-6">
          <div class="flex items-center justify-between mb-3">
            <h2 class="text-sm font-semibold text-gray-700">本地目录</h2>
            <div class="flex items-center space-x-2">
              <button @click="loadDirectories" class="text-primary hover:text-gray-700" title="刷新目录">
                <font-awesome-icon icon="sync-alt" class="w-4 h-4" />
              </button>
              <button @click="addLocalDirectory" class="text-primary hover:text-gray-700">
                <font-awesome-icon icon="plus" class="w-4 h-4" />
              </button>
            </div>
          </div>

          <!-- 显示目录列表 -->
          <div v-if="Object.keys(directories).length > 0">
            <div v-for="(dir, dirPath) in directories" :key="dirPath">
              <div @contextmenu.prevent="showDirectoryContextMenu($event, dir.path)" :class="[
                'w-full flex items-center justify-between p-2 rounded-lg hover:bg-gray-100 transition-colors group cursor-pointer',
                { 'bg-primary/10': props.selectedDirectory === dir.path }
              ]">
                <div class="flex items-center flex-grow" @click="selectDirectory(dir.path)">
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
                  <button @click.stop="removeDirectory(dir.path)"
                    class="opacity-0 group-hover:opacity-100 text-gray-400 hover:text-red-600">
                    <font-awesome-icon icon="times" class="h-4 w-4" />
                  </button>
                </div>
              </div>

              <!-- 展开的子目录 (递归显示) -->
              <div v-show="dir.expanded">
                <div class="ml-4 border-l-2 border-gray-200 pl-2">
                  <RecursiveSubDirectory :directories="dir.subdirectories" :selectedDirectory="props.selectedDirectory"
                    :photoCounts="props.photoCounts"
                    @select-directory="selectDirectory" @show-context-menu="showDirectoryContextMenu" />
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
      </div>
      <div class="px-4 mt-6">
        <div class="flex items-center justify-between mb-2">
          <h3 class="text-xs font-semibold text-gray-400 uppercase tracking-wider">智能分类</h3>
        </div>
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
      </div>
    </div>
    <div class="p-4 border-t border-gray-200">
      <button class="w-full flex items-center space-x-3 px-3 py-2 rounded-button hover:bg-gray-100 text-left">
        <div class="icon-wrapper">
          <font-awesome-icon icon="cog" class="text-gray-500" />
        </div>
        <span>设置</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, defineComponent, h } from 'vue'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'

// 定义递归组件
const RecursiveSubDirectory = defineComponent({
  name: 'RecursiveSubDirectory',
  props: {
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
  },
  emits: ['select-directory', 'show-context-menu', 'remove-directory'],
  components: {
    'font-awesome-icon': FontAwesomeIcon
  },
  setup(props, { emit }) {
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
      dir.expanded = !dir.expanded;
    };

    const removeDirectory = (path) => {
      emit('remove-directory', path);
    };

    return {
      toggleDirectoryExpansion,
      selectDirectory: (path) => emit('select-directory', path),
      showContextMenu: (event, path) => emit('show-context-menu', { event, path, type: 'directory' }),
      removeDirectory
    };
  },
  render() {
    if (!this.directories || this.directories.length === 0) {
      return null;
    }

    return h('div', { class: 'recursive-subdirectory' }, [
      this.directories.map(node => [
        node.type === 'directory' ? 
          h('div', {
              key: node.path,
              onClick: () => this.selectDirectory(node.path),
              onContextmenu: (event) => this.showContextMenu(event, node.path),
              class: [
                'w-full flex items-center justify-between p-2 rounded-lg hover:bg-gray-100 transition-colors group cursor-pointer',
                { 'bg-primary/10': this.selectedDirectory === node.path }
              ]
            }, [
              h('div', {
                class: 'flex items-center flex-grow',
                onClick: () => this.selectDirectory(node.path)
              }, [
                h('button', {
                  onClick: (event) => {
                    event.stopPropagation();
                    this.toggleDirectoryExpansion(node);
                  },
                  class: [
                    'mr-2 text-gray-400 hover:text-gray-600',
                    { 'opacity-0 group-hover:opacity-100': !node.has_subdirs, 'opacity-100': node.has_subdirs }
                  ]
                }, [
                  h(FontAwesomeIcon, {
                  icon: 'chevron-down',
                  class: [
                    'w-4 h-4 transition-transform',
                    { 'transform rotate-180': node.expanded }
                  ]
                })
                ]),
                h(FontAwesomeIcon, { icon: 'folder', class: 'w-4 h-4 mr-2 text-primary' }),
                h('span', { class: 'text-sm' }, node.name)
              ]),
              h('div', {
                class: 'flex items-center space-x-2'
              }, [
                h('span', { class: 'text-xs text-gray-400' }, node.image_count || 0),
                h('button', {
                  onClick: (event) => {
                    event.stopPropagation();
                    this.$emit('remove-directory', node.path);
                  },
                  class: 'opacity-0 group-hover:opacity-100 text-gray-400 hover:text-red-600'
                }, [
                  h('svg', {
                    xmlns: 'http://www.w3.org/2000/svg',
                    class: 'h-4 w-4',
                    fill: 'none',
                    viewBox: '0 0 24 24',
                    stroke: 'currentColor'
                  }, [
                    h('path', {
                      'stroke-linecap': 'round',
                      'stroke-linejoin': 'round',
                      'stroke-width': 2,
                      d: 'M6 18L18 6M6 6l12 12'
                    })
                  ])
                ])
              ])
            ]) :
          node.type === 'image' ?
            h('div', {
              key: node.path,
              onClick: () => this.selectDirectory(node.path),
              class: [
                'w-full flex items-center p-2 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer',
                { 'bg-primary/10': this.selectedDirectory === node.path }
              ]
            }, [
              h(FontAwesomeIcon, { icon: 'image', class: 'w-4 h-4 mr-2 text-gray-500' }),
              h('span', { class: 'text-sm text-gray-700 flex-1' }, node.name),
              h('span', { class: 'text-xs text-gray-400 ml-2' }, node.image_count || 0)
            ]) :
            null,
        node.type === 'directory' && node.expanded && node.has_subdirs ?
          h('div', {
            key: 'sub-' + node.path,
            class: 'ml-4 border-l-2 border-gray-200 pl-2'
          }, [
            h(RecursiveSubDirectory, {
              directories: node.subdirectories || [],
              selectedDirectory: this.selectedDirectory,
              photoCounts: this.photoCounts,
              'onSelect-directory': this.selectDirectory,
              'onShow-context-menu': this.showContextMenu,
              'onRemove-directory': (path) => this.removeDirectory(path)
            })
          ]) :
          null
      ])
    ]);
  }
});

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
const emit = defineEmits(['update:selectedDirectory', 'showContextMenu', 'showAllPhotos', 'showFavorites', 'directoriesLoaded', 'photoCountsChanged']);

// 响应式数据
const directories = ref({});

// 选择目录
const selectDirectory = (path) => {
  emit('update:selectedDirectory', path);
};

// 显示目录右键菜单
const showDirectoryContextMenu = (event, path) => {
  event.preventDefault();
  emit('showContextMenu', { event, path, type: 'directory' });
};

// 切换目录展开状态
const toggleDirectoryExpansion = async (dir) => {
  if (dir.has_subdirs && (!dir.subdirectories || dir.subdirectories.length === 0)) {
    // 懒加载子目录
    try {
      await waitForPyWebView();
      console.log('懒加载子目录:', dir.path);
      const result = await window.pywebview.api.get_directory_tree(dir.path, 1);
      console.log('子目录加载结果:', result);
      if (result && result.tree && result.tree[0]) {
        dir.subdirectories = result.tree[0].children || [];
        console.log('加载的子目录:', dir.subdirectories);
      }
    } catch (error) {
      console.error('加载子目录失败:', error);
    }
  }
  if (dir) {
    dir.expanded = !dir.expanded;
  }
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
  min-width: 280px;
  max-width: 400px;
}

.icon-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 24px;
  height: 24px;
}
</style>