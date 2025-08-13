"""图片服务模块"""
import os
from typing import Dict, Any, List

from db import DatabaseManager

class ImageService:
    def __init__(self):
        self.db_manager = DatabaseManager()
    
    def get_all_images(self, limit: int = None, offset: int = 0) -> Dict[str, Any]:
        """获取所有图片 - 支持分页"""
        try:
            images = self.db_manager.get_all_images(limit=int(limit) if limit else None, offset=int(offset))
            total = self.db_manager.get_total_image_count()
            
            return {"images": images, "total": total, "offset": int(offset)}
        except Exception as e:
            return {"error": str(e), "images": [], "total": 0, "offset": 0}

    def get_images_in_directory(self, directory_path: str, limit: int = None, offset: int = 0) -> Dict[str, Any]:
        """获取指定目录下的所有图片 - 支持分页"""
        try:
            images = self.db_manager.get_images_in_directory(directory_path, limit=limit, offset=offset)
            total = self.db_manager.get_image_count_in_directory(directory_path)
            
            return {"images": images, "total": total, "offset": int(offset)}
        except Exception as e:
            return {"images": [], "total": 0, "error": str(e)}
    
    def _resolve_directory_path(self, directory_path: str) -> str:
        """将前端传递的相对路径转换为绝对路径"""
        try:
            # 如果已经是绝对路径，直接返回
            if os.path.isabs(directory_path):
                return directory_path
            
            # 获取所有已保存的目录
            directories = self.db_manager.get_directories()
            
            # 查找匹配的目录
            for dir_info in directories:
                base_path = dir_info["path"]
                
                # 检查是否是子目录
                full_path = os.path.join(base_path, directory_path)
                if os.path.exists(full_path):
                    return full_path
                
                # 检查是否是直接子目录
                if directory_path in base_path:
                    return base_path
            
            # 如果找不到匹配的目录，返回原始路径
            return directory_path
            
        except Exception as e:
            print(f"解析目录路径失败: {str(e)}")
            return directory_path
    
    def delete_image(self, file_path: str) -> Dict[str, Any]:
        """删除图片记录"""
        try:
            self.db_manager.delete_image(file_path)
            return {"success": True, "message": "图片删除成功"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_image_details(self, image_id: int) -> Dict[str, Any]:
        """获取图片详细信息"""
        try:
            image = self.db_manager.get_image_by_id(int(image_id))
            if not image:
                return {"error": "图片不存在"}
            
            return {"success": True, "image": image}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_photo_counts(self) -> Dict[str, Any]:
        """获取各类照片计数"""
        try:
            # 获取所有图片总数
            all_photos = self.db_manager.get_total_image_count()
            
            # 获取收藏图片数量
            favorites = len(self.db_manager.get_favorite_images())
            
            # 获取目录图片计数（当前目录，不包含子目录）
            directories = {}
            all_dirs = self.db_manager.get_directories()
            for dir_info in all_dirs:
                dir_path = dir_info["path"]
                # 使用单个目录计数，不包含子目录
                count = self.db_manager.get_image_count_in_directory(dir_path)
                directories[dir_path] = count
            
            # TODO: 后续可以根据标签或EXIF数据获取分类计数
            travel = 0
            food = 0
            birthday = 0
            family = 0
            
            return {
                "success": True,
                "all_photos": all_photos,
                "favorites": favorites,
                "directories": directories,
                "travel": travel,
                "food": food,
                "birthday": birthday,
                "family": family
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
