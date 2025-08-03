import sqlite3
import os
from typing import List, Dict, Any

class DatabaseManager:
    def __init__(self, db_path: str = "directories.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS directories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
    
    def save_directory(self, dir_path: str, dir_name: str) -> bool:
        """保存目录到数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR IGNORE INTO directories (path, name) VALUES (?, ?)",
                (dir_path, dir_name)
            )
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False
    
    def get_directories(self) -> List[Dict[str, Any]]:
        """获取所有保存的目录"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT path, name FROM directories ORDER BY created_at DESC")
            rows = cursor.fetchall()
            conn.close()
            
            return [{"path": row[0], "name": row[1]} for row in rows]
        except Exception as e:
            return [{"error": f"获取目录失败: {str(e)}"}]
    
    def remove_directory(self, directory_path: str) -> Dict[str, Any]:
        """从数据库中移除目录记录"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM directories WHERE path = ?", (directory_path,))
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            if deleted_count > 0:
                return {"success": True, "message": "目录已移除"}
            else:
                return {"success": False, "message": "目录不存在"}
                
        except Exception as e:
            return {"success": False, "message": f"移除目录失败: {str(e)}"}