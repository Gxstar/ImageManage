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