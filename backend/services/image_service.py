"""图片服务模块"""
import os
from typing import Dict, Any

from container import dependencies
from exceptions import DatabaseException, ValidationException, format_error_response

class ImageService:
    def __init__(self):
        self.db_manager = dependencies.get_db_manager()
    
    def get_all_images(self, limit: int = None, offset: int = 0) -> Dict[str, Any]:
        """获取所有图片 - 支持分页"""
        try:
            images = self.db_manager.get_all_images(limit=int(limit) if limit else None, offset=int(offset))
            total = self.db_manager.get_total_image_count()
            
            return {"success": True, "images": images, "total": total, "offset": int(offset)}
        except Exception as e:
            return format_error_response(DatabaseException(
                operation="get_all_images",
                message="获取图片列表失败",
                details={"error": str(e), "limit": limit, "offset": offset}
            ))

    def get_images_in_directory(self, directory_path: str, limit: int = None, offset: int = 0) -> Dict[str, Any]:
        """获取指定目录下的所有图片 - 支持分页"""
        try:
            if not directory_path:
                raise ValidationException(
                    field="directory_path",
                    message="目录路径不能为空",
                    details={"path": directory_path}
                )
                
            images = self.db_manager.get_images_in_directory(directory_path, limit=limit, offset=offset)
            total = self.db_manager.get_image_count_in_directory(directory_path)
            
            return {"success": True, "images": images, "total": total, "offset": int(offset)}
        except ValidationException as e:
            return format_error_response(e)
        except Exception as e:
            return format_error_response(DatabaseException(
                operation="get_images_in_directory",
                message="获取目录图片失败",
                details={"error": str(e), "directory_path": directory_path, "limit": limit, "offset": offset}
            ))
    

    
    def delete_image(self, file_path: str) -> Dict[str, Any]:
        """删除图片记录"""
        try:
            if not file_path:
                raise ValidationException(
                    field="file_path",
                    message="文件路径不能为空",
                    details={"path": file_path}
                )
                
            self.db_manager.delete_image(file_path)
            return {"success": True, "message": "图片删除成功"}
        except ValidationException as e:
            return format_error_response(e)
        except Exception as e:
            return format_error_response(DatabaseException(
                operation="delete_image",
                message="删除图片失败",
                details={"path": file_path, "error": str(e)}
            ))

    def get_image_details(self, image_id: int) -> Dict[str, Any]:
        """获取图片详细信息"""
        try:
            if not image_id or int(image_id) <= 0:
                raise ValidationException(
                    field="image_id",
                    message="图片ID无效",
                    details={"image_id": image_id}
                )
                
            image = self.db_manager.get_image_by_id(int(image_id))
            if not image:
                raise ValidationException(
                    field="image_id",
                    message="图片不存在",
                    details={"image_id": image_id}
                )
            
            return {"success": True, "image": image}
        except ValidationException as e:
            return format_error_response(e)
        except Exception as e:
            return format_error_response(DatabaseException(
                operation="get_image_details",
                message="获取图片详情失败",
                details={"image_id": image_id, "error": str(e)}
            ))
    
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
            return format_error_response(DatabaseException(
                operation="get_photo_counts",
                message="获取照片计数失败",
                details={"error": str(e)}
            ))
