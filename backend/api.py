import os
import json
from typing import Dict, Any, List

from services.directory_service import DirectoryService
from services.image_service import ImageService
from services.favorite_service import FavoriteService
from services.rating_service import RatingService

class Api:
    def __init__(self):
        self.directory_service = DirectoryService()
        self.image_service = ImageService()
        self.favorite_service = FavoriteService()
        self.rating_service = RatingService()
    
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
    
    def _resolve_directory_path(self, directory_path: str) -> str:
        """将前端传递的相对路径转换为绝对路径"""
        return self.directory_service._resolve_directory_path(directory_path)

    def get_directory_tree(self, directory_path: str = None, max_depth: int = 2) -> Dict[str, Any]:
        """获取目录树结构，支持深度限制和性能优化"""
        return self.directory_service.get_directory_tree(directory_path, max_depth)

    def _build_directory_tree_fast(self, path: str, max_depth: int = 2, current_depth: int = 0) -> Dict[str, Any]:
        """快速构建目录树结构，支持深度限制和懒加载"""
        return self.directory_service._build_directory_tree_fast(path, max_depth, current_depth)

    def get_image_details(self, image_id: int) -> Dict[str, Any]:
        """获取图片详细信息"""
        return self.image_service.get_image_details(image_id)
