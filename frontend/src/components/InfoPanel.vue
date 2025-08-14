<template>
  <div class="info-panel w-[320px] bg-white border-l border-gray-200 h-full flex flex-col relative overflow-y-auto">
    <!-- 关闭按钮 -->
    <button @click="emit('close')" class="absolute top-3 right-3 flex items-center justify-center w-8 h-8 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-all duration-200 z-10 backdrop-blur-sm">
      <font-awesome-icon icon="times" class="text-sm font-medium" />
    </button>
    
    <div class="flex-1 overflow-y-auto">
      <!-- 图片预览和信息卡片 -->
      <ImageCard 
        :image="imageDetails" 
        @update-rating="handleRatingUpdate"
      />
      
      <!-- 快速操作 -->
      <QuickActions @action="handleQuickAction" />
      
      <!-- 标签和分类 -->
      <ImageTags 
        :image="imageDetails"
        @remove-tag="handleRemoveTag"
        @create-album="handleCreateAlbum"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import ImageCard from './InfoPanel/ImageCard.vue'
import QuickActions from './InfoPanel/QuickActions.vue'
import ImageTags from './InfoPanel/ImageTags.vue'

const props = defineProps({
  image: {
    type: Object,
    required: true
  }
});

const emit = defineEmits(['close', 'update-image']);

const imageDetails = ref(props.image);

// 监听image变化，重置数据
watch(() => props.image, () => {
  imageDetails.value = props.image;
  fetchImageDetails();
});

// 获取图片详细信息
const fetchImageDetails = async () => {
  if (!props.image?.id) return;
  
  try {
    const result = await window.pywebview.api.get_image_details(props.image.id);
    if (result.success) {
      imageDetails.value = { ...props.image, ...result.image };
    } else {
      console.error('获取图片详细信息失败:', result.error);
    }
  } catch (error) {
    console.error('获取图片详细信息失败:', error);
  }
};

// 组件挂载时获取图片详细信息
onMounted(() => {
  fetchImageDetails();
});

// 处理评分更新
const handleRatingUpdate = async (newRating) => {
  try {
    const result = await window.pywebview.api.update_image_rating(
      imageDetails.value.id, 
      newRating
    );
    
    if (!result.success) {
      throw new Error(result.error || '评分更新失败');
    }
    
    // 更新本地数据
    imageDetails.value.rating = newRating;
    
    // 通知父组件更新数据
    emit('update-image', { ...imageDetails.value, rating: newRating });
    
  } catch (error) {
    console.error('更新评分失败:', error);
    alert('评分更新失败: ' + error.message);
  }
};

// 处理快速操作
const handleQuickAction = (action) => {
  console.log('快速操作:', action);
  // 这里可以扩展实际的操作处理
};

// 处理标签移除
const handleRemoveTag = (tag) => {
  console.log('移除标签:', tag);
  // 这里可以扩展实际的标签移除逻辑
};

// 处理创建相册
const handleCreateAlbum = () => {
  console.log('创建相册');
  // 这里可以扩展实际的相册创建逻辑
};
</script>

<style scoped>
.info-panel {
  flex-shrink: 0;
}
</style>