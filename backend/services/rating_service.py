"""评分服务模块"""
from typing import Dict, Any

from db import DatabaseManager

class RatingService:
    def __init__(self):
        self.db_manager = DatabaseManager()
    
    def update_image_rating(self, image_id: int, rating: int) -> Dict[str, Any]:
        """更新图片评分"""
        try:
            self.db_manager.update_image_rating(image_id, rating)
            return {"success": True, "message": "评分更新成功"}
        except Exception as e:
            return {"success": False, "error": str(e)}