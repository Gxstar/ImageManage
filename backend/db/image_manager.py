import sqlite3
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from .base import BaseDB

class ImageManager(BaseDB):
    """图片管理类"""
    def __init__(self, db_path: str = None):
        """初始化ImageManager
        
        Args:
            db_path: 数据库文件路径，如果为None则使用默认路径
        """
        if db_path is None:
            # 使用相对于项目根目录的路径
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(current_dir))
            db_path = os.path.join(project_root, 'directories.db')
        super().__init__(db_path)
    
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
                    SELECT id, filename, file_path, file_size, created_at, modified_at, 
                           thumbnail, exif_data, directory_path, width, height, 
                           format, is_favorite, rating, added_at
                    FROM images WHERE file_path = ?
                ''', (file_path,))
                
                row = cursor.fetchone()
                if row:
                    return {
                        "id": row[0],
                        "filename": row[1], "file_path": row[2], "file_size": row[3],
                        "created_at": row[4], "modified_at": row[5], "thumbnail_url": f"/api/thumbnail/{row[0]}",
                        "exif_data": json.loads(row[7]) if row[7] else {},
                        "directory_path": row[8], "width": row[9], "height": row[10],
                        "format": row[11], "is_favorite": bool(row[12]),
                        "rating": row[13], "added_at": row[14]
                    }
                return None
        except Exception as e:
            print(f"获取图片失败: {str(e)}")
            return None
    
    def get_images_in_directory(self, directory_path: str, limit: int = None, offset: int = 0) -> List[Dict[str, Any]]:
        """获取指定目录及其子目录下的所有图片 - 支持分页"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                directory_pattern = directory_path.rstrip('\\/') + '%'
                query = '''
                    SELECT id, filename, file_path, file_size, created_at, modified_at,
                           thumbnail, exif_data, directory_path, width, height,
                           format, is_favorite, rating, added_at
                    FROM images WHERE directory_path LIKE ? ORDER BY modified_at DESC
                '''

                params = [directory_pattern]
                if limit is not None and limit > 0:
                    query += " LIMIT ? OFFSET ?"
                    params.extend([limit, offset])

                cursor.execute(query, params)

                rows = cursor.fetchall()
                images = []
                for row in rows:
                    images.append({
                        "id": row[0],
                        "filename": row[1], "file_path": row[2], "file_size": row[3],
                        "created_at": row[4], "modified_at": row[5], "thumbnail_url": f"/api/thumbnail/{row[0]}",
                        "exif_data": json.loads(row[7]) if row[7] else {},
                        "directory_path": row[8], "width": row[9], "height": row[10],
                        "format": row[11], "is_favorite": bool(row[12]),
                        "rating": row[13], "added_at": row[14]
                    })
                return images
        except Exception as e:
            print(f"获取目录图片失败: {str(e)}")
            return []

    def get_image_count_in_directory(self, directory_path: str) -> int:
        """获取指定目录及其子目录下的图片总数"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                # 使用 LIKE 来匹配目录及其子目录，处理Windows反斜杠
                directory_pattern = directory_path.rstrip('\\/') + '%'
                cursor.execute('''
                    SELECT COUNT(*) FROM images WHERE directory_path LIKE ?
                ''', (directory_pattern,))
                result = cursor.fetchone()
                return result[0] if result else 0
        except Exception as e:
            print(f"获取目录图片数量失败: {str(e)}")
            return 0
    
    def get_all_images(self, limit: Optional[int] = None, offset: int = 0) -> List[Dict[str, Any]]:
        """获取所有图片 - 支持分页"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                query = '''
                    SELECT id, filename, file_path, file_size, created_at, modified_at, 
                           thumbnail, exif_data, directory_path, width, height, 
                           format, is_favorite, rating, added_at
                    FROM images ORDER BY modified_at DESC
                '''
                params = []
                if limit is not None and limit > 0:
                    query += " LIMIT ? OFFSET ?"
                    params.extend([limit, offset])
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                images = []
                for row in rows:
                    images.append({
                        "id": row[0],
                        "filename": row[1], "file_path": row[2], "file_size": row[3],
                        "created_at": row[4], "modified_at": row[5], "thumbnail_url": f"/api/thumbnail/{row[0]}",
                        "exif_data": json.loads(row[7]) if row[7] else {},
                        "directory_path": row[8], "width": row[9], "height": row[10],
                        "format": row[11], "is_favorite": bool(row[12]),
                        "rating": row[13], "added_at": row[14]
                    })
                return images
        except Exception as e:
            print(f"获取所有图片失败: {str(e)}")
            return []

    def get_total_image_count(self) -> int:
        """获取所有图片的总数"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM images')
                result = cursor.fetchone()
                return result[0] if result else 0
        except Exception as e:
            print(f"获取图片总数失败: {str(e)}")
            return 0
    
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
                    SELECT id, filename, file_path, file_size, created_at, modified_at, 
                           thumbnail, exif_data, directory_path, width, height, 
                           format, is_favorite, rating, added_at
                    FROM images WHERE is_favorite = 1 ORDER BY added_at DESC
                ''')
                
                rows = cursor.fetchall()
                images = []
                for row in rows:
                    images.append({
                        "id": row[0],
                        "filename": row[1], "file_path": row[2], "file_size": row[3],
                        "created_at": row[4], "modified_at": row[5], "thumbnail_url": f"/api/thumbnail/{row[0]}",
                        "exif_data": json.loads(row[7]) if row[7] else {},
                        "directory_path": row[8], "width": row[9], "height": row[10],
                        "format": row[11], "is_favorite": bool(row[12]),
                        "rating": row[13], "added_at": row[14]
                    })
                return images
        except Exception as e:
            print(f"获取收藏图片失败: {str(e)}")
            return []

    def get_image_by_id(self, image_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取图片信息"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, filename, file_path, file_size, created_at, modified_at, 
                           thumbnail, exif_data, directory_path, width, height, 
                           format, is_favorite, rating, added_at
                    FROM images WHERE id = ?
                ''', (image_id,))
                
                row = cursor.fetchone()
                if row:
                    return {
                        "id": row[0],
                        "filename": row[1], "file_path": row[2], "file_size": row[3],
                        "created_at": row[4], "modified_at": row[5], "thumbnail": row[6],
                        "thumbnail_url": f"/api/thumbnail/{row[0]}",
                        "exif_data": json.loads(row[7]) if row[7] else {},
                        "directory_path": row[8], "width": row[9], "height": row[10],
                        "format": row[11], "is_favorite": bool(row[12]),
                        "rating": row[13], "added_at": row[14]
                    }
                return None
        except Exception as e:
            print(f"根据ID获取图片失败: {str(e)}")
            return None

    def get_thumbnail_by_id(self, image_id: int) -> Optional[bytes]:
        """根据ID获取缩略图bytes数据"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT thumbnail FROM images WHERE id = ?
                ''', (image_id,))
                
                row = cursor.fetchone()
                if row and row[0]:
                    return row[0]  # 直接返回bytes数据
                return None
        except Exception as e:
            print(f"获取缩略图失败: {str(e)}")
            return None