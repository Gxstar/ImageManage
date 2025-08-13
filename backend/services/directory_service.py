"""目录服务模块"""
import os
import webview
from typing import Dict, Any

from container import dependencies
from exceptions import DatabaseException, ValidationException, format_error_response

class DirectoryService:
    def __init__(self):
        self.db_manager = dependencies.get_db_manager()
    
    def get_directories(self) -> Dict[str, Any]:
        """获取所有已保存的目录"""
        try:
            directories = self.db_manager.get_directories()
            return {"success": True, "directories": directories}
        except Exception as e:
            return format_error_response(DatabaseException(
                operation="get_directories",
                message="获取目录列表失败",
                details={"error": str(e)}
            ))
    
    def add_directory(self) -> Dict[str, Any]:
        """添加新的图片目录 - 使用原生文件夹选择对话框"""
        try:
            # 使用pywebview的create_file_dialog选择文件夹
            selected_folders = webview.windows[0].create_file_dialog(
                webview.FOLDER_DIALOG,
                allow_multiple=False
            )
            
            if not selected_folders:
                return {"success": False, "message": "用户取消了选择"}
            
            # 处理create_file_dialog的返回值
            if isinstance(selected_folders, tuple):
                directory_path = selected_folders[0]
            elif isinstance(selected_folders, list):
                directory_path = selected_folders[0]
            else:
                directory_path = str(selected_folders)
            
            if not os.path.exists(directory_path):
                raise ValidationException(
                    field="directory_path",
                    message="指定的目录不存在",
                    details={"path": directory_path}
                )
            
            # 截取目录的最终名字作为名字
            dir_name = os.path.basename(directory_path)
            self.db_manager.save_directory(directory_path, dir_name)
            return {"success": True, "message": "目录添加成功", "path": directory_path}
            
        except ValidationException as e:
            return format_error_response(e)
        except Exception as e:
            return format_error_response(DatabaseException(
                operation="add_directory",
                message="添加目录失败",
                details={"error": str(e)}
            ))
    
    def remove_directory(self, directory_path: str) -> Dict[str, Any]:
        """删除指定的目录"""
        try:
            self.db_manager.remove_directory(directory_path)
            return {"success": True, "message": "目录删除成功"}
        except Exception as e:
            return format_error_response(DatabaseException(
                operation="remove_directory",
                message="删除目录失败",
                details={"path": directory_path, "error": str(e)}
            ))
    
    def get_directory_tree(self, directory_path: str = None, max_depth: int = 2) -> Dict[str, Any]:
        """获取目录树结构，支持深度限制和性能优化"""
        try:
            if directory_path is None:
                # 获取所有根目录
                directories = self.db_manager.get_directories()
                tree = []
                for dir_info in directories:
                    root_path = dir_info["path"]
                    if os.path.exists(root_path):
                        tree.append(self._build_directory_tree_fast(root_path, max_depth))
                return {"success": True, "tree": tree}
            else:
                # 获取指定目录的树
                resolved_path = self._resolve_directory_path(directory_path)
                if not os.path.exists(resolved_path):
                    raise ValidationException(
                        field="directory_path",
                        message="指定的目录不存在",
                        details={"path": resolved_path}
                    )
                tree = self._build_directory_tree_fast(resolved_path, max_depth)
                return {"success": True, "tree": tree}
                
        except ValidationException as e:
            return format_error_response(e)
        except Exception as e:
            return format_error_response(DatabaseException(
                operation="get_directory_tree",
                message="获取目录树失败",
                details={"error": str(e)}
            ))

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
            # 记录日志但不抛出异常，保持向后兼容
            print(f"解析目录路径失败: {str(e)}")
            return directory_path

    def _build_directory_tree_fast(self, path: str, max_depth: int = 2, current_depth: int = 0) -> Dict[str, Any]:
        """快速构建目录树结构，支持深度限制和懒加载"""
        try:
            tree = {
                "name": os.path.basename(path),
                "path": path,
                "type": "directory",
                "children": [],
                "has_subdirs": False,
                "image_count": 0  # 添加图片计数
            }
            
            # 计算当前目录的图片数量（不包含子目录）
            tree["image_count"] = self._get_directory_image_count(path)
            
            # 如果达到最大深度，只标记是否有子目录，不实际加载
            if current_depth >= max_depth:
                try:
                    # 快速检查是否有子目录
                    items = os.listdir(path)
                    for item in items:
                        if not item.startswith('.'):
                            item_path = os.path.join(path, item)
                            if os.path.isdir(item_path):
                                tree["has_subdirs"] = True
                                break
                    return tree
                except:
                    return tree
            
            if os.path.isdir(path):
                try:
                    items = sorted(os.listdir(path))
                    for item in items:
                        if item.startswith('.'):
                            continue
                            
                        item_path = os.path.join(path, item)
                        if os.path.isdir(item_path):
                            tree["children"].append(
                                self._build_directory_tree_fast(item_path, max_depth, current_depth + 1)
                            )
                            tree["has_subdirs"] = True
                except (PermissionError, OSError):
                    # 处理权限错误或无法访问的目录
                    pass
            
            return tree
        except Exception as e:
            return {
                "name": os.path.basename(path),
                "path": path,
                "type": "directory",
                "error": str(e),
                "children": [],
                "has_subdirs": False,
                "image_count": 0
            }
    
    def _get_directory_image_count(self, directory_path: str) -> int:
        """获取单个目录内的图片数量（不包含子目录）"""
        try:
            return self.db_manager.get_image_count_in_directory(directory_path)
        except Exception as e:
            # 记录日志但不抛出异常，保持向后兼容
            print(f"计算目录图片数量失败: {str(e)}")
            return 0