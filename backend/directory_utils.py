import os
from typing import List, Dict, Any

class DirectoryManager:
    @staticmethod
    def build_directory_structure(root_path: str) -> Dict[str, Any]:
        """构建目录结构"""
        try:
            root_name = os.path.basename(root_path)
            
            def scan_directory(path: str, name: str) -> Dict[str, Any]:
                try:
                    subdirs = []
                    if os.path.isdir(path):
                        for item in os.listdir(path):
                            # 跳过以"."开头的隐藏文件夹
                            if item.startswith('.'):
                                continue
                            item_path = os.path.join(path, item)
                            if os.path.isdir(item_path):
                                subdirs.append(scan_directory(item_path, item))
                    
                    return {
                        "name": name,
                        "path": path,
                        "expanded": False,
                        "subdirectories": subdirs
                    }
                except PermissionError:
                    return {
                        "name": name,
                        "path": path,
                        "expanded": False,
                        "subdirectories": []
                    }
            
            return scan_directory(root_path, root_name)
            
        except Exception as e:
            return {
                "name": os.path.basename(root_path),
                "path": root_path,
                "expanded": False,
                "subdirectories": [],
                "error": str(e)
            }
    
    @staticmethod
    def get_images_in_directory(directory_path: str, image_extensions: set = None) -> List[Dict[str, Any]]:
        """获取指定目录中的图片文件信息"""
        if image_extensions is None:
            image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.raw', '.heic', '.heif'}
        
        images = []
        if not os.path.exists(directory_path):
            return images
        
        for root, dirs, files in os.walk(directory_path):
            # 过滤掉隐藏文件夹
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for file in files:
                file_path = os.path.join(root, file)
                file_ext = os.path.splitext(file)[1].lower()
                
                if file_ext in image_extensions:
                    try:
                        stat = os.stat(file_path)
                        images.append({
                            "name": file,
                            "path": file_path,
                            "size": stat.st_size,
                            "created_at": stat.st_ctime,
                            "modified_at": stat.st_mtime
                        })
                    except (OSError, IOError):
                        continue
        
        # 按修改时间降序排列
        images.sort(key=lambda x: x["modified_at"], reverse=True)
        return images