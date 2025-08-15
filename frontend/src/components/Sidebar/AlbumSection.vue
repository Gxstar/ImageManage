<template>
  <div class="mb-6">
    <!-- 标题栏 - 参照 LocalDirectorySection 样式 -->
    <div class="flex items-center justify-between mb-3">
      <h2 class="text-sm font-semibold text-gray-700">相册</h2>
      <button 
        @click="showAddDialog = true" 
        class="text-primary hover:text-gray-700" 
        title="添加相册"
      >
        <font-awesome-icon icon="plus" class="w-4 h-4" />
      </button>
    </div>

    <!-- 相册列表 - 横向标签式排列 -->
    <div class="flex flex-wrap gap-2">
      <div 
        v-for="album in albums" 
        :key="album.id"
        class="album-tag relative group"
      >
        <button
          class="album-button px-2.5 py-1 text-[11px] rounded-full border transition-all duration-200 whitespace-nowrap leading-tight"
          :class="[
            selectedAlbum === album.id 
              ? 'bg-primary text-white border-primary' 
              : 'bg-gray-50 text-gray-600 border-gray-200 hover:border-gray-300 hover:bg-gray-100'
          ]"
          @click="selectAlbum(album.id)"
        >
          {{ album.name }}
        </button>
        
        <!-- 删除按钮 - 鼠标悬停显示 -->
        <button
          @click.stop="deleteAlbum(album.id)"
          class="absolute -right-1 -top-0.5 opacity-0 group-hover:opacity-100 transition-opacity duration-200 z-10"
        >
          <div class="w-3.5 h-3.5 rounded-full bg-red-500 text-white flex items-center justify-center text-[9px] leading-none">
            ×
          </div>
        </button>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="albums.length === 0" class="text-center py-6">
      <div class="text-gray-400 text-sm space-y-1">
        <p>还没有相册</p>
        <p class="text-xs">点击右上角 + 创建第一个相册</p>
      </div>
    </div>

    <!-- 添加相册对话框 -->
    <el-dialog
      v-model="showAddDialog"
      title="创建新相册"
      width="320px"
      :close-on-click-modal="false"
      class="album-dialog"
    >
      <el-form @submit.prevent>
        <el-form-item label="相册名称">
          <el-input
            v-model="newAlbumName"
            placeholder="给相册起个名字吧"
            maxlength="12"
            show-word-limit
            @keyup.enter="addAlbum"
            class="!rounded-lg"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button 
            @click="showAddDialog = false" 
            class="!rounded-lg"
          >
            取消
          </el-button>
          <el-button 
            type="primary" 
            @click="addAlbum" 
            :disabled="!newAlbumName.trim()"
            class="!rounded-lg"
          >
            创建
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'

// Props 和 Emits
const emit = defineEmits(['select-album', 'album-changed'])

// 状态管理
const albums = ref([])
const selectedAlbum = ref(null)
const showAddDialog = ref(false)
const newAlbumName = ref('')
const loading = ref(false)

// 方法
const loadAlbums = async () => {
  loading.value = true
  try {
    const result = await window.pywebview.api.get_all_albums()
    if (result.success) {
      albums.value = result.albums || []
    } else {
      console.error('获取相册失败:', result.error)
    }
  } catch (error) {
    console.error('获取相册失败:', error)
  } finally {
    loading.value = false
  }
}

const selectAlbum = (albumId) => {
  selectedAlbum.value = albumId
  emit('select-album', albumId)
}

const addAlbum = async () => {
  if (!newAlbumName.value.trim()) return
  
  try {
    const result = await window.pywebview.api.create_album(newAlbumName.value.trim())
    if (result.success) {
      await loadAlbums()
      newAlbumName.value = ''
      showAddDialog.value = false
      emit('album-changed')
    } else {
      console.error('创建相册失败:', result.error)
    }
  } catch (error) {
    console.error('创建相册失败:', error)
  }
}

const deleteAlbum = async (albumId) => {
  try {
    const result = await window.pywebview.api.delete_album(albumId)
    if (result.success) {
      await loadAlbums()
      if (selectedAlbum.value === albumId) {
        selectedAlbum.value = null
        emit('select-album', null)
      }
      emit('album-changed')
    } else {
      console.error('删除相册失败:', result.error)
    }
  } catch (error) {
    console.error('删除相册失败:', error)
  }
}

// 生命周期
onMounted(() => {
  loadAlbums()
})

// 暴露方法给父组件
const refreshAlbums = () => {
  loadAlbums()
}

const clearSelection = () => {
  selectedAlbum.value = null
}

defineExpose({
  refreshAlbums,
  clearSelection
})
</script>

<style scoped>
.album-tag {
  position: relative;
}

.album-button {
  font-size: 11px;
  line-height: 1.2;
  min-height: 20px;
  cursor: pointer;
}

.album-button:hover {
  transform: translateY(-0.5px);
}

.album-dialog :deep(.el-dialog) {
  border-radius: 12px;
}

.album-dialog :deep(.el-dialog__header) {
  margin-right: 0;
  padding-bottom: 12px;
}

.album-dialog :deep(.el-dialog__body) {
  padding-top: 8px;
}

:deep(.el-input__wrapper) {
  border-radius: 8px;
}
</style>