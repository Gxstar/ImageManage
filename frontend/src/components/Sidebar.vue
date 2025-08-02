<template>
  <div class="sidebar bg-white border-r border-gray-200 flex flex-col h-full">
    <div class="p-4 border-b border-gray-200">
      <div class="flex items-center space-x-2">
        <div class="w-8 h-8 bg-primary rounded-button flex items-center justify-center">
          <i class="fas fa-camera text-white text-sm"></i>
        </div>
        <span class="font-['Pacifico'] text-xl text-gray-800">照片管理器</span>
      </div>
    </div>
    <div class="flex-1 overflow-y-auto py-4">
      <div class="px-4 space-y-1">
        <button @click="showAllPhotos" class="w-full flex items-center space-x-3 px-3 py-2 rounded-button hover:bg-gray-100 text-left">
          <div class="icon-wrapper">
            <i class="fas fa-images text-primary"></i>
          </div>
          <span>全部照片</span>
        </button>
        <button class="w-full flex items-center space-x-3 px-3 py-2 rounded-button hover:bg-gray-100 text-left">
          <div class="icon-wrapper">
            <i class="fas fa-clock text-primary"></i>
          </div>
          <span>最近导入</span>
        </button>
        <button class="w-full flex items-center space-x-3 px-3 py-2 rounded-button hover:bg-gray-100 text-left">
          <div class="icon-wrapper">
            <i class="fas fa-star text-primary"></i>
          </div>
          <span>收藏夹</span>
        </button>
      </div>
      <div class="px-4 mt-6">
        <!-- 本地目录 -->
        <div class="mb-6">
          <div class="flex items-center justify-between mb-3">
            <h2 class="text-sm font-semibold text-gray-700">本地目录</h2>
            <button @click="addLocalDirectory" class="text-primary hover:text-gray-700">
              <i class="fas fa-plus w-4 h-4"></i>
            </button>
          </div>
          
          <!-- 显示目录列表 -->
          <div v-if="Object.keys(directories).length > 0">
            <div v-for="(dir, dirPath) in directories" :key="dirPath">
              <div
                @contextmenu.prevent="showDirectoryContextMenu($event, dir.path)"
                :class="[
                  'w-full flex items-center justify-between p-2 rounded-lg hover:bg-gray-100 transition-colors group cursor-pointer',
                  { 'bg-primary/10': selectedDirectory === dir.path }
                ]"
              >
                <div class="flex items-center flex-grow" @click="selectDirectory(dir.path)">
                  <button
                    @click.stop="toggleDirectoryExpansion(dir)"
                    class="mr-2 opacity-0 group-hover:opacity-100 text-gray-400 hover:text-gray-600"
                  >
                    <i 
                      class="fas fa-chevron-down w-4 h-4 transition-transform" 
                      :class="{ 'transform rotate-180': dir.expanded }" 
                    ></i>
                  </button>
                  <i class="fas fa-folder w-4 h-4 mr-2 text-primary"></i>
                  <span class="text-sm">{{ dir.name }}</span>
                </div>
                <button 
                  @click.stop="removeDirectory(dir.path)"
                  class="opacity-0 group-hover:opacity-100 text-gray-400 hover:text-red-600"
                >
                  <i class="fas fa-times h-4 w-4"></i>
                </button>
              </div>
              
              <!-- 展开的子目录 (递归显示) -->
              <div v-show="dir.expanded">
                <div class="ml-4 border-l-2 border-gray-200 pl-2">
                  <RecursiveSubDirectory 
                    :directories="dir.subdirectories" 
                    :selectedDirectory="selectedDirectory" 
                    @select-directory="selectDirectory"
                    @show-context-menu="showDirectoryContextMenu"
                  />
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
              <i class="fas fa-mountain text-primary"></i>
            </div>
            <span>旅行记忆</span>
            <span class="ml-auto text-xs text-gray-400">128</span>
          </button>
          <button class="w-full flex items-center space-x-3 px-3 py-2 rounded-button hover:bg-gray-100 text-left">
            <div class="icon-wrapper">
              <i class="fas fa-utensils text-primary"></i>
            </div>
            <span>美食日记</span>
            <span class="ml-auto text-xs text-gray-400">56</span>
          </button>
          <button class="w-full flex items-center space-x-3 px-3 py-2 rounded-button hover:bg-gray-100 text-left">
            <div class="icon-wrapper">
              <i class="fas fa-birthday-cake text-primary"></i>
            </div>
            <span>生日派对</span>
            <span class="ml-auto text-xs text-gray-400">42</span>
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
              <i class="fas fa-user text-primary"></i>
            </div>
            <span>人物</span>
          </button>
          <button class="w-full flex items-center space-x-3 px-3 py-2 rounded-button hover:bg-gray-100 text-left">
            <div class="icon-wrapper">
              <i class="fas fa-map-marker-alt text-primary"></i>
            </div>
            <span>地点</span>
          </button>
          <button class="w-full flex items-center space-x-3 px-3 py-2 rounded-button hover:bg-gray-100 text-left">
            <div class="icon-wrapper">
              <i class="fas fa-calendar-alt text-primary"></i>
            </div>
            <span>时间线</span>
          </button>
        </div>
      </div>
    </div>
    <div class="p-4 border-t border-gray-200">
      <button class="w-full flex items-center space-x-3 px-3 py-2 rounded-button hover:bg-gray-100 text-left">
        <div class="icon-wrapper">
          <i class="fas fa-cog text-gray-500"></i>
        </div>
        <span>设置</span>
      </button>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, defineProps, defineEmits, defineComponent, h } from 'vue'
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
    }
  },
  emits: ['select-directory', 'show-context-menu', 'remove-directory'],
  setup(props, { emit }) {
    const toggleDirectoryExpansion = (dir) => {
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
      this.directories.map(dir => [
        h('div', {
          key: dir.path,
          onClick: () => this.selectDirectory(dir.path),
          onContextmenu: (event) => this.showContextMenu(event, dir.path),
          class: [
            'w-full flex items-center justify-between p-2 rounded-lg hover:bg-gray-100 transition-colors group cursor-pointer',
            { 'bg-primary/10': this.selectedDirectory === dir.path }
          ]
        }, [
          h('div', { 
            class: 'flex items-center flex-grow',
            onClick: () => this.selectDirectory(dir.path)
          }, [
            h('button', {
              onClick: (event) => {
                event.stopPropagation();
                this.toggleDirectoryExpansion(dir);
              },
              class: 'mr-2 opacity-0 group-hover:opacity-100 text-gray-400 hover:text-gray-600'
            }, [
              h('i', {
                class: [
                  'fas fa-chevron-down w-4 h-4 transition-transform',
                  { 'transform rotate-180': dir.expanded }
                ]
              })
            ]),
            h('i', { class: 'fas fa-folder w-4 h-4 mr-2 text-primary' }),
            h('span', { class: 'text-sm' }, dir.name)
          ]),
          h('button', {
            onClick: (event) => {
              event.stopPropagation();
              // 触发移除目录事件
              this.showContextMenu(event, dir.path);
              // 显示确认对话框并移除目录
              if (confirm('确定要移除这个目录吗？')) {
                this.$emit('remove-directory', dir.path);
              }
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
                'stroke-width': '2',
                d: 'M6 18L18 6M6 6l12 12'
              })
            ])
          ])
        ]),
        dir.expanded && dir.subdirectories && dir.subdirectories.length > 0 ?
          h('div', { 
            key: 'sub-' + dir.path,
            class: 'ml-4 border-l-2 border-gray-200 pl-2'
          }, [
            h(RecursiveSubDirectory, {
              directories: dir.subdirectories,
              selectedDirectory: this.selectedDirectory,
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

export default defineComponent({
  name: 'Sidebar',
  components: {
    RecursiveSubDirectory
  },
  props: {
    selectedDirectory: {
      type: String,
      default: ''
    }
  },
  setup(props, { emit }) {
    const directories = ref({})
    
    // 选择目录
    const selectDirectory = (path) => {
      emit('update:selectedDirectory', path)
    }
    
    // 显示目录右键菜单
    const showDirectoryContextMenu = (event, path) => {
      event.preventDefault()
      emit('showContextMenu', { event, path, type: 'directory' })
    }
    
    // 切换目录展开状态
    const toggleDirectoryExpansion = (dir) => {
      if (dir) {
        dir.expanded = !dir.expanded
      }
    }
    
    // 添加本地目录
    const addLocalDirectory = async () => {
      const isElectron = !!window.electronAPI;
      
      if (!isElectron) {
        // 在开发环境中添加模拟目录
        const mockDir = {
          '开发目录': {
            path: 'C:\\mock\\development\\directory',
            expanded: false,
            subdirectories: []
          }
        };
        directories.value = { ...directories.value, ...mockDir };
        return;
      }
      
      // 在Electron环境中添加实际目录
      if (window.electronAPI && window.electronAPI.addDirectory) {
        try {
          const result = await window.electronAPI.addDirectory();
          if (result) {
            // 重新加载目录
            loadDirectories();
          }
        } catch (error) {
          console.error('Failed to add directory:', error);
        }
      } else {
        console.error('electronAPI or addDirectory method is not available');
      }
    }
    
    // 转换目录结构数据格式
    const convertDirectoryStructure = (dirStructure) => {
      if (!dirStructure) return null;
      
      return {
        name: dirStructure.name,
        path: dirStructure.path,
        expanded: false,
        subdirectories: dirStructure.subdirectories ? dirStructure.subdirectories.map(convertDirectoryStructure).filter(Boolean) : []
      };
    };
    
    // 获取目录中的图片数量
    // 已移除此功能
    
    // 从后端加载目录结构
    const loadDirectories = async () => {
      // 检查electronAPI是否存在
      if (!window.electronAPI) {
        // 在开发环境中添加模拟目录
        const mockDirs = {
          'C:\\mock\\development\\directory': {
            name: '开发目录',
            path: 'C:\\mock\\development\\directory',
            expanded: false,
            subdirectories: [
              {
                name: '子目录1',
                path: 'C:\\mock\\development\\directory\\子目录1',
                expanded: false,
                subdirectories: []
              },
              {
                name: '子目录2',
                path: 'C:\\mock\\development\\directory\\子目录2',
                expanded: false,
                subdirectories: [
                  {
                    name: '子子目录',
                    path: 'C:\\mock\\development\\directory\\子目录2\\子子目录',
                    expanded: false,
                    subdirectories: []
                  }
                ]
              }
            ]
          }
        };
        directories.value = mockDirs;
        console.log('使用开发环境模拟数据:', mockDirs);
        return;
      }
      
      // 检查getSavedDirectories方法是否存在
      if (!window.electronAPI.getSavedDirectories) {
        console.error('getSavedDirectories method is not available on electronAPI');
        return;
      }
      
      // 从主进程获取保存的目录
      try {
        const savedDirs = await window.electronAPI.getSavedDirectories();
        console.log('从主进程获取的目录数据:', savedDirs);
        
        if (savedDirs && Array.isArray(savedDirs)) {
          // 转换为所需格式
          const convertedDirs = savedDirs.map(convertDirectoryStructure).filter(Boolean);
          console.log('转换后的目录数据:', convertedDirs);
          
          // 将数组转换为对象格式，以路径为键
          const newDirectories = {};
          convertedDirs.forEach(dir => {
            newDirectories[dir.path] = dir;
          });
          
          // 获取每个目录的图片数量
          // 已移除此功能
          
          console.log('最终目录数据:', newDirectories);
          directories.value = newDirectories;
        } else {
          // 如果没有保存的目录，设置一个默认值
          console.log('没有获取到目录数据');
          directories.value = {};
        }
      } catch (error) {
        console.error('Failed to load saved directories:', error);
        // 出错时也设置一个默认值
        directories.value = {};
      }
    }
    
    // 从后端加载目录结构
    onMounted(async () => {
      await loadDirectories();
    })
    
    // 移除目录
    const removeDirectory = async (directoryPath) => {
      // 显示确认对话框
      if (!confirm('确定要移除这个目录吗？')) {
        return;
      }
      
      const isElectron = !!window.electronAPI;
      
      if (!isElectron) {
        // 在开发环境中模拟移除目录
        const dirName = directoryPath.split('\\').pop();
        console.log(`在开发环境中模拟移除目录: ${dirName}`);
        return;
      }
      
      // 在Electron环境中移除实际目录
      if (window.electronAPI && window.electronAPI.removeDirectory) {
        try {
          await window.electronAPI.removeDirectory(directoryPath);
          // 重新加载目录
          loadDirectories();
        } catch (error) {
          console.error('Failed to remove directory:', error);
        }
      } else {
        console.error('electronAPI or removeDirectory method is not available');
      }
    };
    
    // 显示全部照片
    const showAllPhotos = () => {
      emit('showAllPhotos')
    }
    
    return {
      directories,
      selectDirectory,
      showDirectoryContextMenu,
      toggleDirectoryExpansion,
      addLocalDirectory,
      removeDirectory,
      showAllPhotos
    }
  }
})
</script>


<style scoped>
.sidebar {
  width: 280px;
}
.icon-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 24px;
  height: 24px;
}
</style>