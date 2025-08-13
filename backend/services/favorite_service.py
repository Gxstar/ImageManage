"""收藏服务模块"""
from typing import Dict, Any, List

from container import dependencies
from exceptions import DatabaseException, ValidationException, format_error_response

class FavoriteService:
    def __init__(self):
        self.db_manager = dependencies.get_db_manager()
    
    def update_image_favorite(self, file_path: str, is_favorite: bool) -> Dict[str, Any]:
        """更新图片收藏状态"""
        try:
            if not file_path:
                raise ValidationException(
                    field="file_path",
                    message="文件路径不能为空",
                    details={"path": file_path}
                )
                
            self.db_manager.update_image_favorite(file_path, is_favorite)
            return {"success": True, "message": "收藏状态更新成功"}
        except ValidationException as e:
            return format_error_response(e)
        except Exception as e:
            return format_error_response(DatabaseException(
                operation="update_image_favorite",
                message="更新收藏状态失败",
                details={"path": file_path, "is_favorite": is_favorite, "error": str(e)}
            ))
    
    def toggle_image_favorite(self, image_id: int) -> Dict[str, Any]:
        """切换图片收藏状态"""
        try:
            if not image_id or int(image_id) <= 0:
                raise ValidationException(
                    field="image_id",
                    message="图片ID无效",
                    details={"image_id": image_id}
                )
                
            success = self.db_manager.toggle_favorite(int(image_id))
            return {"success": success, "message": "收藏状态切换成功"}
        except ValidationException as e:
            return format_error_response(e)
        except Exception as e:
            return format_error_response(DatabaseException(
                operation="toggle_image_favorite",
                message="切换收藏状态失败",
                details={"image_id": image_id, "error": str(e)}
            ))
    
    def get_favorite_images(self) -> Dict[str, Any]:
        """获取所有收藏的图片"""
        try:
            images = self.db_manager.get_favorite_images()
            return {
                "success": True,
                "images": images,
                "total": len(images) if images else 0,
                "error": None
            }
        except Exception as e:
            return format_error_response(DatabaseException(
                operation="get_favorite_images",
                message="获取收藏图片失败",
                details={"error": str(e)}
            ))