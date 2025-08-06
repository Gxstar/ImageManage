import sqlite3
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from .base import BaseDB

class ImageManager(BaseDB):
    """图片管理类"""
    
    def add_image(self, filename: str, file_path: str, file_size: int = None, 
                  created_at: datetime = None, modified_at: datetime = None,
                  thumbnail: bytes = None, exif_data: Dict[str, Any] = None,
                  directory_path: str = None, width: int = None, 
                  height: int = None, format: str = None) -> bool:
        """添加图片到数据库"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                exif_json = json.dumps(exif_data) if exif_data else None
                
                cursor.execute('''
                    INSERT OR REPLACE INTO images 
                    (filename, file_path, file_size, created_at, modified_at, 
                     thumbnail, exif_data, directory_path, width, height, format)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    filename, file_path, file_size, created_at, modified_at,
                    thumbnail, exif_json, directory_path, width, height, format
                ))
                conn.commit()
            return True
        except Exception as e:
            print(f"添加图片失败: {str(e)}")
            return False
    
    def get_image_by_path(self, file_path: str) -> Optional[Dict[str, Any]]:
        """根据文件路径获取图片信息"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT filename, file_path, file_size, created_at, modified_at, 
                           thumbnail, exif_data, directory_path, width, height, 
                           format, is_favorite, rating, added_at
                    FROM images WHERE file_path = ?
                ''', (file_path,))
                
                row = cursor.fetchone()
                if row:
                    return {
                        "filename": row[0], "file_path": row[1], "file_size": row[2],
                        "created_at": row[3], "modified_at": row[4], "thumbnail": row[5],
                        "exif_data": json.loads(row[6]) if row[6] else {},
                        "directory_path": row[7], "width": row[8], "height": row[9],
                        "format": row[10], "is_favorite": bool(row[11]),
                        "rating": row[12], "added_at": row[13]
                    }
                return None
        except Exception as e:
            print(f"获取图片失败: {str(e)}")
            return None
    
    def get_images_in_directory(self, directory_path: str) -> List[Dict[str, Any]]:
        """获取指定目录下的所有图片"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT filename, file_path, file_size, created_at, modified_at, 
                           thumbnail, exif_data, directory_path, width, height, 
                           format, is_favorite, rating, added_at
                    FROM images WHERE directory_path = ? ORDER BY modified_at DESC
                ''', (directory_path,))
                
                rows = cursor.fetchall()
                return [{
                    "filename": row[0], "file_path": row[1], "file_size": row[2],
                    "created_at": row[3], "modified_at": row[4], "thumbnail": row[5],
                    "exif_data": json.loads(row[6]) if row[6] else {},
                    "directory_path": row[7], "width": row[8], "height": row[9],
                    "format": row[10], "is_favorite": bool(row[11]),
                    "rating": row[12], "added_at": row[13]
                } for row in rows]
        except Exception as e:
            print(f"获取目录图片失败: {str(e)}")
            return []
    
    def get_all_images(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """获取所有图片"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                query = '''
                    SELECT filename, file_path, file_size, created_at, modified_at, 
                           thumbnail, exif_data, directory_path, width, height, 
                           format, is_favorite, rating, added_at
                    FROM images ORDER BY modified_at DESC
                '''
                if limit:
                    query += f" LIMIT {limit}"
                
                cursor.execute(query)
                rows = cursor.fetchall()
                return [{
                    "filename": row[0], "file_path": row[1], "file_size": row[2],
                    "created_at": row[3], "modified_at": row[4], "thumbnail": row[5],
                    "exif_data": json.loads(row[6]) if row[6] else {},
                    "directory_path": row[7], "width": row[8], "height": row[9],
                    "format": row[10], "is_favorite": bool(row[11]),
                    "rating": row[12], "added_at": row[13]
                } for row in rows]
        except Exception as e:
            print(f"获取所有图片失败: {str(e)}")
            return []
    
    def delete_image(self, file_path: str) -> bool:
        """从数据库中删除图片"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM images WHERE file_path = ?", (file_path,))
                deleted = cursor.rowcount > 0
                conn.commit()
                return deleted
        except Exception as e:
            print(f"删除图片失败: {str(e)}")
            return False
    
    def update_image_favorite(self, file_path: str, is_favorite: bool) -> bool:
        """更新图片收藏状态"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE images SET is_favorite = ? WHERE file_path = ?", 
                             (is_favorite, file_path))
                updated = cursor.rowcount > 0
                conn.commit()
                return updated
        except Exception as e:
            print(f"更新收藏状态失败: {str(e)}")
            return False
    
    def update_image_rating(self, file_path: str, rating: float) -> bool:
        """更新图片评分"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE images SET rating = ? WHERE file_path = ?", 
                             (rating, file_path))
                updated = cursor.rowcount > 0
                conn.commit()
                return updated
        except Exception as e:
            print(f"更新评分失败: {str(e)}")
            return False
    
    def update_image(self, file_path: str, image_data: Dict[str, Any]) -> bool:
        """更新图片信息"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                exif_json = json.dumps(image_data.get('exif_data', {})) if image_data.get('exif_data') else None
                
                cursor.execute('''
                    UPDATE images SET
                        filename = ?,
                        file_size = ?,
                        created_at = ?,
                        modified_at = ?,
                        thumbnail = ?,
                        exif_data = ?,
                        width = ?,
                        height = ?,
                        format = ?
                    WHERE file_path = ?
                ''', (
                    image_data.get('filename'),
                    image_data.get('file_size'),
                    image_data.get('created_at'),
                    image_data.get('modified_at'),
                    image_data.get('thumbnail'),
                    exif_json,
                    image_data.get('width'),
                    image_data.get('height'),
                    image_data.get('format'),
                    file_path
                ))
                
                updated = cursor.rowcount > 0
                if not updated:
                    # 如果文件不存在，则添加新记录
                    return self.add_image(
                        filename=image_data.get('filename'),
                        file_path=file_path,
                        file_size=image_data.get('file_size'),
                        created_at=image_data.get('created_at'),
                        modified_at=image_data.get('modified_at'),
                        thumbnail=image_data.get('thumbnail'),
                        exif_data=image_data.get('exif_data'),
                        directory_path=image_data.get('directory_path'),
                        width=image_data.get('width'),
                        height=image_data.get('height'),
                        format=image_data.get('format')
                    )
                
                conn.commit()
                return True
        except Exception as e:
            print(f"更新图片失败: {str(e)}")
            return False
    
    def get_favorite_images(self) -> List[Dict[str, Any]]:
        """获取收藏的图片"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT filename, file_path, file_size, created_at, modified_at, 
                           thumbnail, exif_data, directory_path, width, height, 
                           format, is_favorite, rating, added_at
                    FROM images WHERE is_favorite = 1 ORDER BY added_at DESC
                ''')
                
                rows = cursor.fetchall()
                return [{
                    "filename": row[0], "file_path": row[1], "file_size": row[2],
                    "created_at": row[3], "modified_at": row[4], "thumbnail": row[5],
                    "exif_data": json.loads(row[6]) if row[6] else {},
                    "directory_path": row[7], "width": row[8], "height": row[9],
                    "format": row[10], "is_favorite": bool(row[10]),
                    "rating": row[11], "added_at": row[12]
                } for row in rows]
        except Exception as e:
            print(f"获取收藏图片失败: {str(e)}")
            return []