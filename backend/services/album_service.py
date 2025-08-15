from typing import Dict, Any, List, Optional
from db.album_manager import AlbumManager
from exceptions import DatabaseException, ValidationException


class AlbumService:
    """相册服务类 - 处理相册相关的业务逻辑"""
    
    def __init__(self):
        self.album_manager = AlbumManager()
    
    def create_album(self, name: str, description: str = "", cover_image_id: Optional[int] = None) -> Dict[str, Any]:
        """创建新相册
        
        Args:
            name: 相册名称
            description: 相册描述
            cover_image_id: 封面图片ID
            
        Returns:
            包含相册信息的响应
        """
        try:
            if not name or not name.strip():
                raise ValidationException("相册名称不能为空")
            
            name = name.strip()
            if len(name) > 100:
                raise ValidationException("相册名称不能超过100个字符")
            
            album_id = self.album_manager.create_album(name, description, cover_image_id)
            
            return {
                "success": True,
                "album_id": album_id,
                "message": f"相册 '{name}' 创建成功"
            }
            
        except ValidationException as e:
            return {"success": False, "error": str(e)}
        except DatabaseException as e:
            return {"success": False, "error": f"创建相册失败: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": f"未知错误: {str(e)}"}
    
    def get_all_albums(self, include_stats: bool = True) -> Dict[str, Any]:
        """获取所有相册
        
        Args:
            include_stats: 是否包含统计信息
            
        Returns:
            相册列表
        """
        try:
            albums = self.album_manager.get_albums(include_stats=include_stats)
            return {
                "success": True,
                "albums": albums,
                "total": len(albums)
            }
            
        except DatabaseException as e:
            return {"success": False, "error": f"获取相册列表失败: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": f"未知错误: {str(e)}"}
    
    def get_album_details(self, album_id: int) -> Dict[str, Any]:
        """获取相册详情
        
        Args:
            album_id: 相册ID
            
        Returns:
            相册详情信息
        """
        try:
            album = self.album_manager.get_album_by_id(album_id)
            if not album:
                return {"success": False, "error": "相册不存在"}
            
            return {
                "success": True,
                "album": album
            }
            
        except DatabaseException as e:
            return {"success": False, "error": f"获取相册详情失败: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": f"未知错误: {str(e)}"}
    
    def update_album(self, album_id: int, name: str = None, description: str = None, 
                    cover_image_id: Optional[int] = None) -> Dict[str, Any]:
        """更新相册信息
        
        Args:
            album_id: 相册ID
            name: 相册名称
            description: 相册描述
            cover_image_id: 封面图片ID
            
        Returns:
            更新结果
        """
        try:
            if name is not None:
                name = name.strip()
                if not name:
                    raise ValidationException("相册名称不能为空")
                if len(name) > 100:
                    raise ValidationException("相册名称不能超过100个字符")
            
            updated = self.album_manager.update_album(album_id, name, description, cover_image_id)
            
            if updated:
                return {
                    "success": True,
                    "message": "相册信息更新成功"
                }
            else:
                return {
                    "success": False,
                    "error": "相册不存在或无需更新"
                }
                
        except ValidationException as e:
            return {"success": False, "error": str(e)}
        except DatabaseException as e:
            return {"success": False, "error": f"更新相册失败: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": f"未知错误: {str(e)}"}
    
    def delete_album(self, album_id: int) -> Dict[str, Any]:
        """删除相册
        
        Args:
            album_id: 相册ID
            
        Returns:
            删除结果
        """
        try:
            deleted = self.album_manager.delete_album(album_id)
            
            if deleted:
                return {
                    "success": True,
                    "message": "相册删除成功"
                }
            else:
                return {
                    "success": False,
                    "error": "相册不存在"
                }
                
        except DatabaseException as e:
            return {"success": False, "error": f"删除相册失败: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": f"未知错误: {str(e)}"}
    
    def search_albums(self, keyword: str) -> Dict[str, Any]:
        """搜索相册
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            匹配的相册列表
        """
        try:
            if not keyword or not keyword.strip():
                return {"success": True, "albums": [], "total": 0}
            
            keyword = keyword.strip()
            if len(keyword) > 100:
                raise ValidationException("搜索关键词不能超过100个字符")
            
            albums = self.album_manager.search_albums(keyword)
            return {
                "success": True,
                "albums": albums,
                "total": len(albums)
            }
            
        except ValidationException as e:
            return {"success": False, "error": str(e)}
        except DatabaseException as e:
            return {"success": False, "error": f"搜索相册失败: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": f"未知错误: {str(e)}"}
    
    def add_images_to_album(self, album_id: int, image_ids: List[int]) -> Dict[str, Any]:
        """将图片添加到相册
        
        Args:
            album_id: 相册ID
            image_ids: 图片ID列表
            
        Returns:
            添加结果
        """
        try:
            if not image_ids:
                return {"success": True, "message": "没有图片需要添加", "added_count": 0}
            
            # 验证相册是否存在
            album = self.album_manager.get_album_by_id(album_id)
            if not album:
                return {"success": False, "error": "相册不存在"}
            
            # 去重
            image_ids = list(set(image_ids))
            
            added_count = self.album_manager.add_images_to_album(album_id, image_ids)
            
            return {
                "success": True,
                "message": f"成功添加 {added_count} 张图片到相册",
                "added_count": added_count,
                "total_images": album.get("image_count", 0) + added_count
            }
            
        except DatabaseException as e:
            return {"success": False, "error": f"添加图片到相册失败: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": f"未知错误: {str(e)}"}
    
    def remove_images_from_album(self, album_id: int, image_ids: List[int]) -> Dict[str, Any]:
        """从相册中移除图片
        
        Args:
            album_id: 相册ID
            image_ids: 图片ID列表
            
        Returns:
            移除结果
        """
        try:
            if not image_ids:
                return {"success": True, "message": "没有图片需要移除", "removed_count": 0}
            
            # 验证相册是否存在
            album = self.album_manager.get_album_by_id(album_id)
            if not album:
                return {"success": False, "error": "相册不存在"}
            
            removed_count = self.album_manager.remove_images_from_album(album_id, image_ids)
            
            return {
                "success": True,
                "message": f"成功从相册移除 {removed_count} 张图片",
                "removed_count": removed_count,
                "total_images": max(0, album.get("image_count", 0) - removed_count)
            }
            
        except DatabaseException as e:
            return {"success": False, "error": f"从相册移除图片失败: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": f"未知错误: {str(e)}"}
    
    def get_album_images(self, album_id: int, limit: int = 50, offset: int = 0,
                        sort_by: str = "added_at", sort_order: str = "asc") -> Dict[str, Any]:
        """获取相册中的图片
        
        Args:
            album_id: 相册ID
            limit: 返回数量限制
            offset: 偏移量
            sort_by: 排序字段
            sort_order: 排序顺序
            
        Returns:
            相册中的图片列表
        """
        try:
            # 验证相册是否存在
            album = self.album_manager.get_album_by_id(album_id)
            if not album:
                return {"success": False, "error": "相册不存在"}
            
            # 验证排序参数
            valid_sort_fields = ["added_at", "filename", "created_at", "modified_at"]
            if sort_by not in valid_sort_fields:
                sort_by = "added_at"
            
            if sort_order.lower() not in ["asc", "desc"]:
                sort_order = "asc"
            
            images = self.album_manager.get_album_images(
                album_id, limit, offset, sort_by, sort_order
            )
            
            total_count = self.album_manager.get_album_image_count(album_id)
            
            return {
                "success": True,
                "images": images,
                "total": total_count,
                "album_info": album
            }
            
        except DatabaseException as e:
            return {"success": False, "error": f"获取相册图片失败: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": f"未知错误: {str(e)}"}
    
    def update_image_sort_order(self, album_id: int, image_orders: List[Dict[str, int]]) -> Dict[str, Any]:
        """更新相册中图片的排序顺序
        
        Args:
            album_id: 相册ID
            image_orders: 图片排序信息列表
            
        Returns:
            更新结果
        """
        try:
            if not image_orders:
                return {"success": True, "message": "没有图片需要更新排序"}
            
            # 验证相册是否存在
            album = self.album_manager.get_album_by_id(album_id)
            if not album:
                return {"success": False, "error": "相册不存在"}
            
            # 验证数据结构
            for item in image_orders:
                if not isinstance(item, dict) or "image_id" not in item or "sort_order" not in item:
                    return {"success": False, "error": "排序数据格式错误"}
            
            updated = self.album_manager.update_album_image_sort_order(album_id, image_orders)
            
            if updated:
                return {
                    "success": True,
                    "message": "图片排序更新成功"
                }
            else:
                return {
                    "success": False,
                    "error": "更新排序失败"
                }
                
        except DatabaseException as e:
            return {"success": False, "error": f"更新图片排序失败: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": f"未知错误: {str(e)}"}