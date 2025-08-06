import os
import base64
from io import BytesIO
from typing import Dict, Any

try:
    from PIL import Image
    from PIL.ExifTags import TAGS
    PIL_AVAILABLE = True
    # 设置PIL图像像素限制为2亿像素
    Image.MAX_IMAGE_PIXELS = 200000000
except ImportError:
    PIL_AVAILABLE = False

class ImageProcessor:
    @staticmethod
    def generate_thumbnail(image_path: str, max_size: tuple = (200, 200)) -> bytes:
        """智能生成缩略图，优先使用EXIF缩略图，没有则自动生成"""
        if not PIL_AVAILABLE:
            return None
            
        try:
            if not os.path.exists(image_path):
                return None
            
            with Image.open(image_path) as img:
                # 首先尝试从EXIF获取缩略图
                exif_thumbnail = ImageProcessor._get_exif_thumbnail(image_path)
                if exif_thumbnail:
                    # 检查EXIF缩略图尺寸是否合适
                    if exif_thumbnail.width >= max_size[0] * 0.8 and exif_thumbnail.height >= max_size[1] * 0.8:
                        # 使用EXIF缩略图并调整到目标尺寸
                        exif_thumbnail.thumbnail(max_size, Image.Resampling.LANCZOS)
                        buffer = BytesIO()
                        exif_thumbnail.save(buffer, format='JPEG', quality=85)
                        buffer.seek(0)
                        return buffer.getvalue()
                
                # 如果没有合适的EXIF缩略图，则自动生成
                # 转换为RGB模式（处理RGBA或其他模式）
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 计算缩略图尺寸，保持宽高比
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # 将缩略图保存到内存缓冲区
                buffer = BytesIO()
                img.save(buffer, format='JPEG', quality=85)
                buffer.seek(0)
                
                return buffer.getvalue()
                
        except Exception as e:
            print(f"生成缩略图失败: {str(e)}")
            return None
    
    @staticmethod
    def _get_exif_thumbnail(image_path: str) -> Image.Image:
        """从EXIF中获取缩略图"""
        try:
            with Image.open(image_path) as img:
                # 检查是否有EXIF缩略图
                if hasattr(img, 'thumbnail') and img.thumbnail:
                    return img.thumbnail
                
                # 尝试从EXIF数据中获取缩略图
                exif = img._getexif()
                if exif and 513 in exif:  # 缩略图偏移量标签
                    thumbnail_data = exif.get(513)  # JPEGInterchangeFormat
                    if thumbnail_data:
                        return Image.open(BytesIO(thumbnail_data))
                        
        except Exception as e:
            print(f"获取EXIF缩略图失败: {str(e)}")
        
        return None
    
    @staticmethod
    def get_exif_data(image_path: str) -> Dict[str, Any]:
        """获取图片的EXIF信息"""
        if not PIL_AVAILABLE:
            return {"error": "PIL库未安装，无法获取EXIF信息"}
            
        try:
            if not os.path.exists(image_path):
                return {"error": "图片文件不存在"}
            
            try:
                with Image.open(image_path) as img:
                    exif_data = {}
                    
                    if hasattr(img, '_getexif') and img._getexif():
                        exif = img._getexif()
                        for tag_id, value in exif.items():
                            tag = TAGS.get(tag_id, tag_id)
                            exif_data[tag] = str(value)
                    
                    # 添加基本图片信息
                    exif_data.update({
                        "Width": img.width,
                        "Height": img.height,
                        "Format": img.format,
                        "Mode": img.mode
                    })
                    
                    return {"exif": exif_data}
                    
            except Exception as e:
                # 如果PIL无法处理，返回基本图片信息
                with Image.open(image_path) as img:
                    return {"exif": {
                        "Width": img.width,
                        "Height": img.height,
                        "Format": img.format,
                        "Mode": img.mode
                    }}
                    
        except Exception as e:
            return {"error": f"获取EXIF信息失败: {str(e)}"}
    
    @staticmethod
    def is_image_file(file_path: str) -> bool:
        """检查文件是否为图片"""
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.raw', '.heic', '.heif'}
        file_ext = os.path.splitext(file_path)[1].lower()
        return file_ext in image_extensions