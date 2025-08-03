import webview
import os
import json
from typing import List, Dict, Any

from database import DatabaseManager
from directory_utils import DirectoryManager
from image_utils import ImageProcessor

class Api:
    def __init__(self):
        self.window = None
        self.db_manager = DatabaseManager()
        self.dir_manager = DirectoryManager()
        self.image_processor = ImageProcessor()
    
    def test_log(self):
        return "这是一条来自后端的日志"
    
    def select_directory(self) -> Dict[str, Any]:
        """选择目录对话框"""
        try:
            # 使用pywebview的目录选择对话框
            selected_dir = webview.windows[0].create_file_dialog(
                webview.FOLDER_DIALOG
            )
            
            if selected_dir and len(selected_dir) > 0:
                dir_path = selected_dir[0]
                dir_name = os.path.basename(dir_path)
                
                # 保存到数据库
                if self.db_manager.save_directory(dir_path, dir_name):
                    return {
                        "success": True,
                        "path": dir_path,
                        "name": dir_name
                    }
            
            return {"success": False, "message": "未选择目录"}
            
        except Exception as e:
            return {"success": False, "message": f"选择目录失败: {str(e)}"}
    
    def get_directories(self) -> List[Dict[str, Any]]:
        """获取所有保存的目录结构"""
        try:
            directories = []
            db_directories = self.db_manager.get_directories()
            
            for dir_info in db_directories:
                if "error" in dir_info:
                    return [dir_info]
                
                dir_path = dir_info["path"]
                if os.path.exists(dir_path):
                    dir_structure = self.dir_manager.build_directory_structure(dir_path)
                    directories.append(dir_structure)
            
            return directories
            
        except Exception as e:
            return [{"error": f"获取目录失败: {str(e)}"}]
    
    def remove_directory(self, directory_path: str) -> Dict[str, Any]:
        """从数据库中移除目录记录"""
        return self.db_manager.remove_directory(directory_path)
    
    def get_images_in_directory(self, directory_path: str) -> Dict[str, Any]:
        """获取指定目录中的图片"""
        try:
            if not os.path.exists(directory_path):
                return {"error": "目录不存在", "images": []}
            
            images = self.dir_manager.get_images_in_directory(directory_path)
            
            # 为每个图片添加缩略图
            for image in images:
                image["thumbnail"] = self.image_processor.generate_thumbnail(image["path"])
            
            return {"images": images}
            
        except Exception as e:
            return {"error": f"获取图片失败: {str(e)}", "images": []}
    
    def get_all_images(self) -> Dict[str, Any]:
        """获取所有目录中的图片"""
        try:
            all_images = []
            db_directories = self.db_manager.get_directories()
            
            for dir_info in db_directories:
                if "error" in dir_info:
                    continue
                
                dir_path = dir_info["path"]
                if os.path.exists(dir_path):
                    images = self.dir_manager.get_images_in_directory(dir_path)
                    for image in images:
                        image["thumbnail"] = self.image_processor.generate_thumbnail(image["path"])
                    all_images.extend(images)
            
            # 按修改时间降序排列
            all_images.sort(key=lambda x: x["modified_at"], reverse=True)
            
            return {"images": all_images}
            
        except Exception as e:
            return {"error": f"获取所有图片失败: {str(e)}", "images": []}
    
    def get_exif_data(self, image_path: str) -> Dict[str, Any]:
        """获取图片的EXIF信息"""
        return self.image_processor.get_exif_data(image_path)