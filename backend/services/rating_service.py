"""评分服务模块"""
from typing import Dict, Any

from container import dependencies
from exceptions import DatabaseException, ValidationException, format_error_response

class RatingService:
    def __init__(self):
        self.db_manager = dependencies.get_db_manager()
    
    def update_image_rating(self, image_id: int, rating: int) -> Dict[str, Any]:
        """更新图片评分"""
        try:
            if not image_id or int(image_id) <= 0:
                raise ValidationException(
                    field="image_id",
                    message="图片ID无效",
                    details={"image_id": image_id}
                )
                
            if rating is None or not isinstance(rating, int) or rating < 0 or rating > 5:
                raise ValidationException(
                    field="rating",
                    message="评分必须在0-5之间",
                    details={"rating": rating}
                )
                
            self.db_manager.update_image_rating(int(image_id), int(rating))
            return {"success": True, "message": "评分更新成功"}
        except ValidationException as e:
            return format_error_response(e)
        except Exception as e:
            return format_error_response(DatabaseException(
                operation="update_image_rating",
                message="更新评分失败",
                details={"image_id": image_id, "rating": rating, "error": str(e)}
            ))