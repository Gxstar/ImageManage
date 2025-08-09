import os
import json
from typing import Dict, Any, List
from db import DatabaseManager

class Api:
    def __init__(self):
        self.db_manager = DatabaseManager()
    
    def get_directories(self) -> Dict[str, Any]:
        """获取所有已保存的目录"""
        try:
            directories = self.db_manager.get_directories()
            return {"directories": directories}
        except Exception as e:
            return {"error": str(e), "directories": []}
    
    def add_directory(self) -> Dict[str, Any]:
        """添加新的图片目录 - 使用原生文件夹选择对话框"""
        try:
            # 使用pywebview的create_file_dialog选择文件夹
            import webview
            selected_folders = webview.windows[0].create_file_dialog(
                webview.FOLDER_DIALOG,
                allow_multiple=False
            )
            
            if not selected_folders:
                return {"success": False, "error": "用户取消了选择"}
            
            # 处理create_file_dialog的返回值
            if isinstance(selected_folders, tuple):
                directory_path = selected_folders[0]
            elif isinstance(selected_folders, list):
                directory_path = selected_folders[0]
            else:
                directory_path = str(selected_folders)
            
            if not os.path.exists(directory_path):
                return {"success": False, "error": "目录不存在"}
            #截取目录的最终名字作为名字
            dir_name = os.path.basename(directory_path)
            self.db_manager.save_directory(directory_path, dir_name)
            return {"success": True, "message": "目录添加成功", "path": directory_path}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def remove_directory(self, directory_path: str) -> Dict[str, Any]:
        """移除目录"""
        try:
            self.db_manager.remove_directory(directory_path)
            return {"success": True, "message": "目录移除成功"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_images_in_directory(self, directory_path: str) -> Dict[str, Any]:
        """获取指定目录中的图片"""
        try:
            # 将相对路径转换为绝对路径
            resolved_path = self._resolve_directory_path(directory_path)
            
            if not resolved_path or not os.path.exists(resolved_path):
                return {"error": "目录不存在", "images": []}
            
            images = self.db_manager.get_images_in_directory(resolved_path)
            return {"images": images}
        except Exception as e:
            return {"error": f"获取图片失败: {str(e)}", "images": []}
    
    def get_all_images(self, limit: int = None, offset: int = 0) -> Dict[str, Any]:
        """获取所有图片 - 支持分页"""
        try:
            if limit is not None:
                limit = int(limit)
            if offset is not None:
                offset = int(offset)
            
            images = self.db_manager.get_all_images(limit=limit, offset=offset)
            total_count = self.db_manager.get_total_image_count()
            return {"images": images, "total": total_count, "offset": offset}
        except Exception as e:
            return {"error": str(e), "images": [], "total": 0, "offset": 0}

    def get_images_in_directory(self, directory_path: str, limit: int = None, offset: int = 0) -> Dict[str, Any]:
        """获取指定目录中的图片 - 支持分页"""
        try:
            # 将相对路径转换为绝对路径
            resolved_path = self._resolve_directory_path(directory_path)
            
            if not resolved_path or not os.path.exists(resolved_path):
                return {"error": "目录不存在", "images": [], "total": 0, "offset": 0}
            
            if limit is not None:
                limit = int(limit)
            if offset is not None:
                offset = int(offset)
            
            images = self.db_manager.get_images_in_directory(resolved_path, limit=limit, offset=offset)
            total_count = self.db_manager.get_image_count_in_directory(resolved_path)
            return {"images": images, "total": total_count, "offset": offset}
        except Exception as e:
            return {"error": f"获取图片失败: {str(e)}", "images": [], "total": 0, "offset": 0}
    
    def update_image_rating(self, file_path: str, rating: int) -> Dict[str, Any]:
        """更新图片评分"""
        try:
            self.db_manager.update_image_rating(file_path, rating)
            return {"success": True, "message": "评分更新成功"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def update_image_favorite(self, file_path: str, is_favorite: bool) -> Dict[str, Any]:
        """更新图片收藏状态"""
        try:
            self.db_manager.update_image_favorite(file_path, is_favorite)
            return {"success": True, "message": "收藏状态更新成功"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_favorite_images(self) -> Dict[str, Any]:
        """获取收藏的图片"""
        try:
            images = self.db_manager.get_favorite_images()
            return {"images": images}
        except Exception as e:
            return {"error": str(e), "images": []}
    
    def delete_image(self, file_path: str) -> Dict[str, Any]:
        """删除图片记录"""
        try:
            self.db_manager.delete_image(file_path)
            return {"success": True, "message": "图片删除成功"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _resolve_directory_path(self, directory_path: str) -> str:
        """将前端传递的相对路径转换为绝对路径"""
        try:
            # 如果已经是绝对路径，直接返回
            if os.path.isabs(directory_path):
                return directory_path
            
            # 获取所有已保存的目录
            directories = self.db_manager.get_directories()
            
            # 查找匹配的目录
            for dir_info in directories:
                base_path = dir_info["path"]
                
                # 检查是否是子目录
                full_path = os.path.join(base_path, directory_path)
                if os.path.exists(full_path):
                    return full_path
                
                # 检查是否是直接子目录
                if directory_path in base_path:
                    return base_path
            
            # 如果找不到匹配的目录，返回原始路径
            return directory_path
            
        except Exception as e:
            print(f"解析目录路径失败: {str(e)}")
            return directory_path

    def get_directory_tree(self, directory_path: str = None) -> Dict[str, Any]:
        """递归获取目录树结构"""
        try:
            if directory_path is None:
                # 获取所有根目录
                directories = self.db_manager.get_directories()
                tree = []
                for dir_info in directories:
                    root_path = dir_info["path"]
                    if os.path.exists(root_path):
                        tree.append(self._build_directory_tree(root_path))
                return {"tree": tree}
            else:
                # 获取指定目录的树
                resolved_path = self._resolve_directory_path(directory_path)
                if not os.path.exists(resolved_path):
                    return {"error": "目录不存在", "tree": []}
                tree = self._build_directory_tree(resolved_path)
                return {"tree": tree}
        except Exception as e:
            return {"error": str(e), "tree": []}

    def _build_directory_tree(self, path: str) -> Dict[str, Any]:
        """递归构建目录树结构"""
        try:
            tree = {
                "name": os.path.basename(path),
                "path": path,
                "type": "directory",
                "children": []
            }
            
            if os.path.isdir(path):
                for item in os.listdir(path):
                    # 跳过以"."开头的隐藏文件夹和文件
                    if item.startswith('.'):
                        continue
                        
                    item_path = os.path.join(path, item)
                    if os.path.isdir(item_path):
                        tree["children"].append(self._build_directory_tree(item_path))
                    elif item.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')):
                        tree["children"].append({
                            "name": item,
                            "path": item_path,
                            "type": "image"
                        })
            
            return tree
        except Exception as e:
            return {
                "name": os.path.basename(path),
                "path": path,
                "type": "directory",
                "error": str(e),
                "children": []
            }