from .base import BaseDB
from .directory_manager import DirectoryManager
from .image_manager import ImageManager

class DatabaseManager:
    """向后兼容的数据库管理器，组合了目录和图片管理功能"""
    
    def __init__(self, db_path: str = "directories.db"):
        self.directory_manager = DirectoryManager(db_path)
        self.image_manager = ImageManager(db_path)
    
    # 目录相关方法（代理到directory_manager）
    def save_directory(self, dir_path: str, dir_name: str) -> bool:
        return self.directory_manager.save_directory(dir_path, dir_name)
    
    def get_directories(self):
        return self.directory_manager.get_directories()
    
    def remove_directory(self, directory_path: str):
        return self.directory_manager.remove_directory(directory_path)
    
    # 图片相关方法（代理到image_manager）
    def add_image(self, *args, **kwargs):
        return self.image_manager.add_image(*args, **kwargs)

    def get_image_by_path(self, *args, **kwargs):
        return self.image_manager.get_image_by_path(*args, **kwargs)

    def get_images_in_directory(self, *args, **kwargs):
        return self.image_manager.get_images_in_directory(*args, **kwargs)

    def get_image_count_in_directory(self, *args, **kwargs):
        return self.image_manager.get_image_count_in_directory(*args, **kwargs)

    def get_all_images(self, *args, **kwargs):
        return self.image_manager.get_all_images(*args, **kwargs)

    def get_total_image_count(self, *args, **kwargs):
        return self.image_manager.get_total_image_count(*args, **kwargs)

    def delete_image(self, *args, **kwargs):
        return self.image_manager.delete_image(*args, **kwargs)

    def update_image_favorite(self, *args, **kwargs):
        return self.image_manager.update_image_favorite(*args, **kwargs)

    def update_image_rating(self, *args, **kwargs):
        return self.image_manager.update_image_rating(*args, **kwargs)

    def update_image(self, *args, **kwargs):
        return self.image_manager.update_image(*args, **kwargs)

    def get_favorite_images(self, *args, **kwargs):
        return self.image_manager.get_favorite_images(*args, **kwargs)