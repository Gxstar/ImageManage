import { createApp } from 'vue'
import App from './App.vue'
import './assets/style.css'

// 在开发模式下模拟electronAPI
if (process.env.NODE_ENV === 'development' && !window.electronAPI) {
  // 模拟electronAPI的部分功能，用于开发调试
  window.electronAPI = {
    // 模拟选择目录
    selectDirectory: () => Promise.resolve('/path/to/selected/directory'),
    
    // 模拟获取保存的目录
    getSavedDirectories: () => Promise.resolve([
      {
        name: '示例目录',
        path: '/path/to/example/directory',
        subdirectories: []
      }
    ]),
    
    // 模拟获取目录中的图片
    getImagesInDirectory: (directoryPath) => {
      // 在开发模式下，我们仍然使用模拟数据，但在生产环境中会从API获取真实数据
      console.log('开发模式：模拟获取目录中的图片');
      return Promise.resolve({
        images: [
          {
            name: '示例图片1.jpg',
            path: '/path/to/example/image1.jpg',
            size: 1024000,
            width: 1920,
            height: 1080,
            date: '2023-05-20T10:30:00',
            exif: {
              DateTimeOriginal: '2023:05:20 10:30:00',
              Model: 'Canon EOS R5',
              FocalLength: '50mm',
              FNumber: 'f/1.8',
              ExifImageWidth: 1920,
              ExifImageHeight: 1080
            }
          },
          {
            name: '示例图片2.jpg',
            path: '/path/to/example/image2.jpg',
            size: 2048000,
            width: 3840,
            height: 2160,
            date: '2023-05-21T14:45:00',
            exif: {
              DateTimeOriginal: '2023:05:21 14:45:00',
              Model: 'Nikon D850',
              FocalLength: '24mm',
              FNumber: 'f/2.8',
              ExifImageWidth: 3840,
              ExifImageHeight: 2160
            }
          }
        ]
      });
    },
    
    // 模拟获取图片EXIF信息
    getExifData: (imagePath) => {
      // 根据图片路径返回相应的EXIF数据
      if (imagePath.includes('image1')) {
        return Promise.resolve({
          exif: {
            DateTimeOriginal: '2023:05:20 10:30:00',
            Model: 'Canon EOS R5',
            FocalLength: '50mm',
            FNumber: 'f/1.8',
            ExifImageWidth: 1920,
            ExifImageHeight: 1080
          }
        });
      } else if (imagePath.includes('image2')) {
        return Promise.resolve({
          exif: {
            DateTimeOriginal: '2023:05:21 14:45:00',
            Model: 'Nikon D850',
            FocalLength: '24mm',
            FNumber: 'f/2.8',
            ExifImageWidth: 3840,
            ExifImageHeight: 2160
          }
        });
      }
      return Promise.resolve({ exif: {} });
    },
    
    // 模拟更新图片信息
    updateImageInfo: (imageData) => Promise.resolve({ success: true })
  };
}

createApp(App).mount('#app')
