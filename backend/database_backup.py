# 原始数据库操作的备份

import sqlite3
import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path: str = "directories.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库表结构"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建目录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS directories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建图片表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                file_path TEXT UNIQUE NOT NULL,
                file_size INTEGER,
                created_at TIMESTAMP,
                modified_at TIMESTAMP,
                thumbnail BLOB,
                exif_data TEXT,
                directory_path TEXT,
                width INTEGER,
                height INTEGER,
                format TEXT,
                is_favorite BOOLEAN DEFAULT 0,
                rating REAL DEFAULT 0,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (directory_path) REFERENCES directories(path) ON DELETE CASCADE
            )
        ''')
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_images_directory ON images(directory_path)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_images_path ON images(file_path)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_images_filename ON images(filename)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_images_favorite ON images(is_favorite)')
        
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
        except Exception as e:
            print(f"保存目录失败: {str(e)}")
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
    
    def add_image(self, filename: str, file_path: str, file_size: int = None, 
                  created_at: datetime = None, modified_at: datetime = None,
                  thumbnail: bytes = None, exif_data: Dict[str, Any] = None,
                  directory_path: str = None, width: int = None, 
                  height: int = None, format: str = None) -> bool:
        """添加图片到数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            exif_json = json.dumps(exif_data) if exif_data else None
            
            cursor.execute('''
                INSERT OR REPLACE INTO images 
                (filename, file_path, file_size, created_at, modified_at, 
                 thumbnail, exif_data, directory_path, width, height, format)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                filename,
                file_path,
                file_size,
                created_at,
                modified_at,
                thumbnail,
                exif_json,
                directory_path,
                width,
                height,
                format
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"添加图片失败: {str(e)}")
            return False
    
    def get_image_by_path(self, file_path: str) -> Optional[Dict[str, Any]]:
        """根据文件路径获取图片信息"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT filename, file_path, file_size, created_at, modified_at, 
                       thumbnail, exif_data, directory_path, width, height, 
                       format, is_favorite, rating, added_at
                FROM images 
                WHERE file_path = ?
            ''', (file_path,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    "filename": row[0],
                    "file_path": row[1],
                    "file_size": row[2],
                    "created_at": row[3],
                    "modified_at": row[4],
                    "thumbnail": row[5],
                    "exif_data": json.loads(row[6]) if row[6] else {},
                    "directory_path": row[7],
                    "width": row[8],
                    "height": row[9],
                    "format": row[10],
                    "is_favorite": bool(row[11]),
                    "rating": row[12],
                    "added_at": row[13]
                }
            return None
        except Exception as e:
            print(f"获取图片失败: {str(e)}")
            return None
    
    def get_images_in_directory(self, directory_path: str) -> List[Dict[str, Any]]:
        """获取指定目录下的所有图片"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT filename, file_path, file_size, created_at, modified_at, 
                       thumbnail, exif_data, directory_path, width, height, 
                       format, is_favorite, rating, added_at
                FROM images 
                WHERE directory_path = ? 
                ORDER BY modified_at DESC
            ''', (directory_path,))
            
            rows = cursor.fetchall()
            conn.close()
            
            images = []
            for row in rows:
                images.append({
                    "filename": row[0],
                    "file_path": row[1],
                    "file_size": row[2],
                    "created_at": row[3],
                    "modified_at": row[4],
                    "thumbnail": row[5],
                    "exif_data": json.loads(row[6]) if row[6] else {},
                    "directory_path": row[7],
                    "width": row[8],
                    "height": row[9],
                    "format": row[10],
                    "is_favorite": bool(row[10]),
                    "rating": row[11],
                    "added_at": row[12]
                })
            
            return images
        except Exception as e:
            print(f"获取目录图片失败: {str(e)}")
            return []
    
    def get_all_images(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """获取所有图片"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = '''
                SELECT filename, file_path, file_size, created_at, modified_at, 
                       thumbnail, exif_data, directory_path, width, height, 
                       format, is_favorite, rating, added_at
                FROM images 
                ORDER BY modified_at DESC
            '''
            
            if limit:
                query += f" LIMIT {limit}"
            
            cursor.execute(query)
            rows = cursor.fetchall()
            conn.close()
            
            images = []
            for row in rows:
                images.append({
                    "filename": row[0],
                    "file_path": row[1],
                    "file_size": row[2],
                    "created_at": row[3],
                    "modified_at": row[4],
                    "thumbnail": row[5],
                    "exif_data": json.loads(row[6]) if row[6] else {},
                    "directory_path": row[7],
                    "width": row[8],
                    "height": row[9],
                    "format": row[10],
                    "is_favorite": bool(row[10]),
                    "rating": row[11],
                    "added_at": row[12]
                })
            
            return images
        except Exception as e:
            print(f"获取所有图片失败: {str(e)}")
            return []
    
    def delete_image(self, file_path: str) -> bool:
        """从数据库中删除图片"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM images WHERE file_path = ?", (file_path,))
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            return deleted_count > 0
        except Exception as e:
            print(f"删除图片失败: {str(e)}")
            return False
    
    def update_image_favorite(self, file_path: str, is_favorite: bool) -> bool:
        """更新图片收藏状态"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("UPDATE images SET is_favorite = ? WHERE file_path = ?", 
                         (is_favorite, file_path))
            updated = cursor.rowcount > 0
            conn.commit()
            conn.close()
            return updated
        except Exception as e:
            print(f"更新收藏状态失败: {str(e)}")
            return False
    
    def update_image_rating(self, file_path: str, rating: float) -> bool:
        """更新图片评分"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("UPDATE images SET rating = ? WHERE file_path = ?", 
                         (rating, file_path))
            updated = cursor.rowcount > 0
            conn.commit()
            conn.close()
            return updated
        except Exception as e:
            print(f"更新评分失败: {str(e)}")
            return False
    
    def get_favorite_images(self) -> List[Dict[str, Any]]:
        """获取收藏的图片"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT filename, file_path, file_size, created_at, modified_at, 
                       thumbnail, exif_data, directory_path, width, height, 
                       format, is_favorite, rating, added_at
                FROM images 
                WHERE is_favorite = 1 
                ORDER BY added_at DESC
            ''')
            
            rows = cursor.fetchall()
            conn.close()
            
            images = []
            for row in rows:
                images.append({
                    "filename": row[0],
                    "file_path": row[1],
                    "file_size": row[2],
                    "created_at": row[3],
                    "modified_at": row[4],
                    "thumbnail": row[5],
                    "exif_data": json.loads(row[6]) if row[6] else {},
                    "directory_path": row[7],
                    "width": row[8],
                    "height": row[9],
                    "format": row[10],
                    "is_favorite": bool(row[10]),
                    "rating": row[11],
                    "added_at": row[12]
                })
            
            return images
        except Exception as e:
            print(f"获取收藏图片失败: {str(e)}")
            return []