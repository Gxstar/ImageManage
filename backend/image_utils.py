import os
import base64
import logging
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
        """使用Pillow直接处理原始图片生成缩略图，缩略图尺寸不超过max_size"""
        if not PIL_AVAILABLE:
            return None
            
        try:
            if not os.path.exists(image_path):
                return None
            
            with Image.open(image_path) as img:
                # 处理EXIF方向信息
                try:
                    # 获取EXIF数据
                    exif = img._getexif()
                    if exif is not None:
                        # EXIF方向标签 (Orientation)
                        orientation_tag = 0x0112
                        orientation = exif.get(orientation_tag, 1)
                        
                        # 根据方向旋转图片
                        if orientation == 3:
                            img = img.rotate(180, expand=True)
                        elif orientation == 6:
                            img = img.rotate(270, expand=True)
                        elif orientation == 8:
                            img = img.rotate(90, expand=True)
                except (AttributeError, KeyError, TypeError):
                    # 如果没有EXIF数据或出错，跳过旋转处理
                    pass
                
                # 转换为RGB模式（处理RGBA或其他模式）
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 计算缩略图尺寸，保持宽高比，最大尺寸不超过max_size
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # 将缩略图保存到内存缓冲区
                buffer = BytesIO()
                img.save(buffer, format='JPEG', quality=90)  # 提高质量到90
                buffer.seek(0)
                
                return buffer.getvalue()
                
        except Exception as e:
            logging.getLogger(__name__).error(f"生成缩略图失败: {str(e)}")
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