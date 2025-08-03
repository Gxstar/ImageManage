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
              <div class="flex items-center space-x-2">
                <button @click="loadDirectories" class="text-primary hover:text-gray-700" title="刷新目录">
                  <i class="fas fa-sync-alt w-4 h-4"></i>
                </button>
                <button @click="addLocalDirectory" class="text-primary hover:text-gray-700">
                  <i class="fas fa-plus w-4 h-4"></i>
                </button>
              </div>
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
              this.$emit('remove-directory', dir.path);
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
      // 检查是否在pywebview环境中
      if (!window.pywebview || !window.pywebview.api) {
        console.log('当前在开发环境，不显示模拟目录');
        // 开发环境不显示任何目录
        directories.value = {};
        return;
      }

      // 使用pywebview选择目录
      try {
        const selectedDir = await window.pywebview.api.select_directory();
        if (selectedDir && selectedDir.success) {
          // 重新加载目录
          await loadDirectories();
        }
      } catch (error) {
        console.error('Failed to add directory with pywebview:', error);
        
        // 开发环境不显示任何目录
        directories.value = {};
      }
    };
    
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
      // 检查是否在pywebview环境中
      if (!window.pywebview || !window.pywebview.api) {
        console.log('当前在开发环境，使用模拟数据');
        // 开发环境不显示任何目录
        directories.value = {};
        return;
      }

      try {
        // 使用pywebview获取目录结构
        const savedDirs = await window.pywebview.api.get_directories();
        console.log('从pywebview获取的目录数据:', savedDirs);
        
        if (savedDirs && Array.isArray(savedDirs)) {
          // 转换为所需格式
          const convertedDirs = savedDirs.map(convertDirectoryStructure).filter(Boolean);
          console.log('转换后的目录数据:', convertedDirs);
          
          // 将数组转换为对象格式，以路径为键
          const newDirectories = {};
          convertedDirs.forEach(dir => {
            newDirectories[dir.path] = dir;
          });
          
          console.log('最终目录数据:', newDirectories);
          directories.value = newDirectories;
        } else {
          // 如果没有保存的目录，设置一个默认值
          console.log('没有获取到目录数据');
          directories.value = {};
        }
      } catch (error) {
        console.error('Failed to load directories with pywebview:', error);
        
        // 开发环境不显示任何目录
        directories.value = {};
        console.log('开发环境不显示目录');
      }
    };
    
    // 从后端加载目录结构
    onMounted(async () => {
      await loadDirectories();
      
      // 添加重试机制，确保在pywebview可用时重新加载目录
      // 每2秒检查一次pywebview是否可用，最多重试10次
      let retryCount = 0;
      const maxRetries = 10;
      
      const checkPyWebView = async () => {
        if (retryCount >= maxRetries) {
          console.log('已达到最大重试次数，停止检查pywebview');
          return;
        }
        
        retryCount++;
        
        // 检查pywebview是否可用
        if (window.pywebview && window.pywebview.api) {
          console.log('检测到pywebview可用，重新加载目录...');
          await loadDirectories();
          return; // 成功加载后停止重试
        }
        
        console.log(`第${retryCount}次检查pywebview，还未就绪...`);
        
        // 继续重试
        setTimeout(checkPyWebView, 2000);
      };
      
      // 如果当前不在pywebview环境中，启动重试机制
      if (!window.pywebview || !window.pywebview.api) {
        console.log('启动pywebview检测重试机制...');
        setTimeout(checkPyWebView, 1000);
      }
    })
    
    // 移除目录
    const removeDirectory = async (directoryPath) => {
      // 显示确认对话框
      if (!confirm('确定要移除这个目录吗？')) {
        return;
      }
      
      // 检查是否在pywebview环境中
      if (!window.pywebview || !window.pywebview.api) {
        console.log('当前在开发环境，模拟移除目录');
        // 开发环境回退到模拟移除
        const dirName = directoryPath.split('\\\\').pop();
        console.log(`在开发环境中模拟移除目录: ${dirName}`);
        
        // 从本地数据中移除
        const newDirectories = { ...directories.value };
        delete newDirectories[directoryPath];
        directories.value = newDirectories;
        return;
      }
      
      try {
        // 使用pywebview移除目录
        const result = await window.pywebview.api.remove_directory(directoryPath);
        if (result && result.success) {
          // 重新加载目录
          await loadDirectories();
        }
      } catch (error) {
        console.error('Failed to remove directory with pywebview:', error);
        
        // 开发环境回退到模拟移除
        const dirName = directoryPath.split('\\\\').pop();
        console.log(`在开发环境中模拟移除目录: ${dirName}`);
        
        // 从本地数据中移除
        const newDirectories = { ...directories.value };
        delete newDirectories[directoryPath];
        directories.value = newDirectories;
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