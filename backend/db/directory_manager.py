import sqlite3
from typing import Any, Dict, List

from .base import BaseDB

class DirectoryManager(BaseDB):
    """目录管理类"""
    
    def save_directory(self, dir_path: str, dir_name: str) -> bool:
        """保存目录到数据库"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR IGNORE INTO directories (path, name) VALUES (?, ?)",
                    (dir_path, dir_name)
                )
                conn.commit()
            return True
        except Exception as e:
            print(f"保存目录失败: {str(e)}")
            return False
    
    def get_directories(self) -> List[Dict[str, Any]]:
        """获取所有保存的目录"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT path, name FROM directories ORDER BY created_at DESC")
                rows = cursor.fetchall()
                return [{"path": row[0], "name": row[1]} for row in rows]
        except Exception as e:
            return [{"error": f"获取目录失败: {str(e)}"}]
    
    def remove_directory(self, directory_path: str) -> Dict[str, Any]:
        """从数据库中移除目录记录"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM directories WHERE path = ?", (directory_path,))
                deleted_count = cursor.rowcount
                conn.commit()
                
                if deleted_count > 0:
                    return {"success": True, "message": "目录已移除"}
                else:
                    return {"success": False, "message": "目录不存在"}
                    
        except Exception as e:
            return {"success": False, "message": f"移除目录失败: {str(e)}"}
    
    def directory_exists(self, directory_path: str) -> bool:
        """检查目录是否已存在"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1 FROM directories WHERE path = ?", (directory_path,))
                return cursor.fetchone() is not None
        except Exception:
            return False