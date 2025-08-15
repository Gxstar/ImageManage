import os
from typing import Dict, Any, List, Optional

from services.directory_service import DirectoryService
from services.image_service import ImageService
from services.favorite_service import FavoriteService
from services.rating_service import RatingService
from services.album_service import AlbumService

class Api:
    def __init__(self):
        self.directory_service = DirectoryService()
        self.image_service = ImageService()
        self.favorite_service = FavoriteService()
        self.rating_service = RatingService()
        self.album_service = AlbumService()
    
    def get_directories(self) -> Dict[str, Any]:
        """获取所有已保存的目录"""
        return self.directory_service.get_directories()
    
    def add_directory(self) -> Dict[str, Any]:
        """添加新的图片目录 - 使用原生文件夹选择对话框"""
        return self.directory_service.add_directory()
    
    def remove_directory(self, directory_path: str) -> Dict[str, Any]:
        """移除目录"""
        return self.directory_service.remove_directory(directory_path)
    
    def get_all_images(self, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """获取所有图片 - 支持分页"""
        return self.image_service.get_all_images(limit, offset)

    def get_images_in_directory(self, directory_path: str, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """获取指定目录中的图片 - 支持分页"""
        try:
            limit = int(limit)
            offset = int(offset)
            return self.image_service.get_images_in_directory(directory_path, limit, offset)
        except Exception as e:
            return {"error": str(e), "images": [], "total": 0}
    
    def update_image_rating(self, image_id: int, rating: int) -> Dict[str, Any]:
        """更新图片评分"""
        return self.rating_service.update_image_rating(image_id, rating)
    
    def update_image_favorite(self, file_path: str, is_favorite: bool) -> Dict[str, Any]:
        """更新图片收藏状态"""
        return self.favorite_service.update_image_favorite(file_path, is_favorite)
    
    def toggle_image_favorite(self, image_id: int) -> Dict[str, Any]:
        """切换图片收藏状态"""
        return self.favorite_service.toggle_image_favorite(image_id)
    
    def get_favorite_images(self) -> Dict[str, Any]:
        """获取所有收藏的图片"""
        try:
            return self.favorite_service.get_favorite_images()
        except Exception as e:
            return {"error": str(e), "images": [], "total": 0}
    
    def delete_image(self, file_path: str) -> Dict[str, Any]:
        """从数据库中删除图片记录"""
        return self.image_service.delete_image(file_path)
    
    def get_directory_tree(self, directory_path: str = None, max_depth: int = 2) -> Dict[str, Any]:
        """获取目录树结构，支持深度限制和性能优化"""
        return self.directory_service.get_directory_tree(directory_path, max_depth)

    def get_image_details(self, image_id: int) -> Dict[str, Any]:
        """获取图片详细信息"""
        return self.image_service.get_image_details(image_id)

    def get_photo_counts(self) -> Dict[str, Any]:
        """获取各类照片计数"""
        return self.image_service.get_photo_counts()
    
    def trigger_background_scan(self) -> Dict[str, Any]:
        """手动触发后台扫描"""
        try:
            from background_scanner import background_scanner
            total_processed = background_scanner.force_full_scan()
            return {"success": True, "processed": total_processed}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # 相册相关接口
    def create_album(self, name: str, description: str = "", cover_image_id: Optional[int] = None) -> Dict[str, Any]:
        """创建新相册"""
        return self.album_service.create_album(name, description, cover_image_id)

    def get_all_albums(self, include_stats: bool = True) -> Dict[str, Any]:
        """获取所有相册"""
        return self.album_service.get_all_albums(include_stats)

    def get_album_details(self, album_id: int) -> Dict[str, Any]:
        """获取相册详情"""
        try:
            album_id = int(album_id)
            return self.album_service.get_album_details(album_id)
        except ValueError:
            return {"success": False, "error": "相册ID必须是数字"}

    def update_album(self, album_id: int, name: str = None, description: str = None, 
                    cover_image_id: Optional[int] = None) -> Dict[str, Any]:
        """更新相册信息"""
        try:
            album_id = int(album_id)
            if cover_image_id is not None:
                cover_image_id = int(cover_image_id)
            return self.album_service.update_album(album_id, name, description, cover_image_id)
        except ValueError:
            return {"success": False, "error": "相册ID和图片ID必须是数字"}

    def delete_album(self, album_id: int) -> Dict[str, Any]:
        """删除相册"""
        try:
            album_id = int(album_id)
            return self.album_service.delete_album(album_id)
        except ValueError:
            return {"success": False, "error": "相册ID必须是数字"}

    def search_albums(self, keyword: str) -> Dict[str, Any]:
        """搜索相册"""
        return self.album_service.search_albums(keyword)

    def add_images_to_album(self, album_id: int, image_ids: List[int]) -> Dict[str, Any]:
        """将图片添加到相册"""
        try:
            album_id = int(album_id)
            if isinstance(image_ids, str):
                # 处理可能的字符串输入
                image_ids = [int(x.strip()) for x in image_ids.split(",")]
            elif not isinstance(image_ids, list):
                image_ids = [int(image_ids)]
            else:
                image_ids = [int(x) for x in image_ids]
            
            return self.album_service.add_images_to_album(album_id, image_ids)
        except ValueError:
            return {"success": False, "error": "相册ID和图片ID必须是数字"}
        except Exception as e:
            return {"success": False, "error": f"参数格式错误: {str(e)}"}

    def remove_images_from_album(self, album_id: int, image_ids: List[int]) -> Dict[str, Any]:
        """从相册中移除图片"""
        try:
            album_id = int(album_id)
            if isinstance(image_ids, str):
                image_ids = [int(x.strip()) for x in image_ids.split(",")]
            elif not isinstance(image_ids, list):
                image_ids = [int(image_ids)]
            else:
                image_ids = [int(x) for x in image_ids]
            
            return self.album_service.remove_images_from_album(album_id, image_ids)
        except ValueError:
            return {"success": False, "error": "相册ID和图片ID必须是数字"}
        except Exception as e:
            return {"success": False, "error": f"参数格式错误: {str(e)}"}

    def get_album_images(self, album_id: int, limit: int = 50, offset: int = 0,
                        sort_by: str = "added_at", sort_order: str = "asc") -> Dict[str, Any]:
        """获取相册中的图片"""
        try:
            album_id = int(album_id)
            limit = int(limit)
            offset = int(offset)
            
            return self.album_service.get_album_images(album_id, limit, offset, sort_by, sort_order)
        except ValueError:
            return {"success": False, "error": "参数必须是数字"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def update_album_image_sort_order(self, album_id: int, image_orders: List[Dict[str, int]]) -> Dict[str, Any]:
        """更新相册中图片的排序顺序"""
        try:
            album_id = int(album_id)
            return self.album_service.update_image_sort_order(album_id, image_orders)
        except ValueError:
            return {"success": False, "error": "相册ID必须是数字"}
        except Exception as e:
            return {"success": False, "error": str(e)}
