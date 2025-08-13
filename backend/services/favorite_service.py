"""收藏服务模块"""
from typing import Dict, Any, List

from db import DatabaseManager

class FavoriteService:
    def __init__(self):
        self.db_manager = DatabaseManager()
    
    def update_image_favorite(self, file_path: str, is_favorite: bool) -> Dict[str, Any]:
        """更新图片收藏状态"""
        try:
            self.db_manager.update_image_favorite(file_path, is_favorite)
            return {"success": True, "message": "收藏状态更新成功"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def toggle_image_favorite(self, image_id: int) -> Dict[str, Any]:
        """切换图片收藏状态"""
        try:
            success = self.db_manager.toggle_favorite(image_id)
            return {"success": success, "message": "收藏状态切换成功"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_favorite_images(self) -> Dict[str, Any]:
        """获取所有收藏的图片"""
        try:
            images = self.db_manager.get_favorite_images()
            return {
                "images": images,
                "total": len(images) if images else 0,
                "error": None
            }
        except Exception as e:
            return {
                "images": [],
                "total": 0,
                "error": str(e)
            }