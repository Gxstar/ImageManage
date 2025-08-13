import json
import os
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional

from .base import BaseDB
from exceptions import DatabaseException, ImageProcessingException

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
                  height: int = None, format: str = None, rating: int = None) -> bool:

        """添加图片到数据库"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                exif_json = json.dumps(exif_data) if exif_data else None
                
                # 插入基础信息到image_metadata表
                cursor.execute('''
                    INSERT OR REPLACE INTO image_metadata 
                    (filename, file_path, file_size, created_at, modified_at, 
                     exif_data, directory_path, width, height, format,rating)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?)
                ''', (
                    filename, file_path, file_size, created_at, modified_at,
                    exif_json, directory_path, width, height, format,rating
                ))
                
                # 获取插入的ID
                image_id = cursor.lastrowid
                
                # 插入缩略图到image_thumbnails表
                if thumbnail:
                    cursor.execute('''
                        INSERT OR REPLACE INTO image_thumbnails (image_id, thumbnail)
                        VALUES (?, ?)
                    ''', (image_id, thumbnail))
                
                conn.commit()
            return True
        except sqlite3.Error as e:
            raise DatabaseException(
                operation="add_image",
                message=f"添加图片到数据库失败: {str(e)}",
                details={"filename": filename, "file_path": file_path}
            )
        except json.JSONEncodeError as e:
            raise ImageProcessingException(
                operation="serialize_exif",
                message=f"EXIF数据序列化失败: {str(e)}",
                details={"filename": filename}
            )
    
    def get_image_by_path(self, file_path: str) -> Optional[Dict[str, Any]]:
        """根据文件路径获取图片信息"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, filename, file_path, file_size, created_at, modified_at,
                           exif_data, directory_path, width, height, 
                           format, is_favorite, rating, added_at
                    FROM image_metadata WHERE file_path = ?
                ''', (file_path,))
                
                row = cursor.fetchone()
                if row:
                    image_id = row[0]
                    
                    # 获取缩略图
                    cursor.execute('''
                        SELECT thumbnail FROM image_thumbnails
                        WHERE image_id = ?
                    ''', (image_id,))
                    thumbnail_row = cursor.fetchone()
                    thumbnail = thumbnail_row[0] if thumbnail_row else None
                    
                    return {
                        "id": image_id,
                        "filename": row[1], "file_path": row[2], "file_size": row[3],
                        "created_at": row[4], "modified_at": row[5], "thumbnail": thumbnail,
                        "thumbnail_url": f"/api/thumbnail/{image_id}",
                        "exif_data": json.loads(row[6]) if row[6] else {},
                        "directory_path": row[7], "width": row[8], "height": row[9],
                        "format": row[10], "is_favorite": bool(row[11]),
                        "rating": row[12], "added_at": row[13]
                    }
                return None
        except sqlite3.Error as e:
            raise DatabaseException(
                operation="get_image_by_path",
                message=f"查询图片信息失败: {str(e)}",
                details={"file_path": file_path}
            )
        except json.JSONDecodeError as e:
            raise ImageProcessingException(
                operation="parse_exif",
                message=f"EXIF数据解析失败: {str(e)}",
                details={"file_path": file_path}
            )
    
    def get_images_in_directory(self, directory_path: str, limit: int = None, offset: int = 0,
                               sort_by: str = "modified_at", sort_order: str = "desc") -> List[Dict[str, Any]]:
        """获取指定目录下的所有图片（不包括子目录） - 支持分页和排序"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # 构建排序SQL
                order_by = f"{sort_by} {sort_order.upper()}"
                
                query = f'''
                    SELECT m.id, m.filename, m.file_path, m.file_size, m.created_at, m.modified_at,
                           m.exif_data, m.directory_path, m.width, m.height,
                           m.format, m.is_favorite, m.rating, m.added_at
                    FROM image_metadata m
                    WHERE m.directory_path = ?
                    ORDER BY m.{order_by}
                '''

                params = [directory_path]
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
                        "exif_data": json.loads(row[6]) if row[6] else {},
                        "directory_path": row[7], "width": row[8], "height": row[9],
                        "format": row[10], "is_favorite": bool(row[11]),
                        "rating": row[12], "added_at": row[13]
                    })
                return images
        except sqlite3.Error as e:
            raise DatabaseException(
                operation="get_images_in_directory",
                message=f"获取目录图片失败: {str(e)}",
                details={"directory_path": directory_path, "limit": limit, "offset": offset}
            )
        except json.JSONDecodeError as e:
            raise ImageProcessingException(
                operation="parse_exif",
                message=f"EXIF数据解析失败: {str(e)}",
                details={"directory_path": directory_path}
            )

    def get_image_count_in_directory(self, directory_path: str) -> int:
        """获取指定目录下的图片总数（不包括子目录）"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT COUNT(*) FROM image_metadata WHERE directory_path = ?
                ''', (directory_path,))
                result = cursor.fetchone()
                return result[0] if result else 0
        except sqlite3.Error as e:
            raise DatabaseException(
                operation="get_image_count_in_directory",
                message=f"获取目录图片数量失败: {str(e)}",
                details={"directory_path": directory_path}
            )
    
    def get_all_images(self, limit: int = None, offset: int = 0,
                      sort_by: str = "modified_at", sort_order: str = "desc") -> List[Dict[str, Any]]:
        """获取所有图片 - 支持分页和排序"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # 构建排序SQL
                order_by = f"{sort_by} {sort_order.upper()}"
                
                query = f'''
                    SELECT m.id, m.filename, m.file_path, m.file_size, m.created_at, m.modified_at,
                           m.exif_data, m.directory_path, m.width, m.height,
                           m.format, m.is_favorite, m.rating, m.added_at
                    FROM image_metadata m
                    ORDER BY m.{order_by}
                '''

                params = []
                if limit is not None and limit > 0:
                    query += " LIMIT ? OFFSET ?"
                    params.extend([limit, offset])

                cursor.execute(query, params)
                
                images = []
                for row in cursor.fetchall():
                    images.append({
                        "id": row[0],
                        "filename": row[1], "file_path": row[2], "file_size": row[3],
                        "created_at": row[4], "modified_at": row[5], "thumbnail_url": f"/api/thumbnail/{row[0]}",
                        "exif_data": json.loads(row[6]) if row[6] else {},
                        "directory_path": row[7], "width": row[8], "height": row[9],
                        "format": row[10], "is_favorite": bool(row[11]),
                        "rating": row[12], "added_at": row[13]
                    })
                
                return images
        except sqlite3.Error as e:
            raise DatabaseException(
                operation="get_all_images",
                message=f"获取所有图片失败: {str(e)}",
                details={"limit": limit, "offset": offset, "sort_by": sort_by, "sort_order": sort_order}
            )
        except json.JSONDecodeError as e:
            raise ImageProcessingException(
                operation="parse_exif",
                message=f"EXIF数据解析失败: {str(e)}"
            )

    def get_total_image_count(self) -> int:
        """获取所有图片的总数"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM image_metadata')
                result = cursor.fetchone()
                return result[0] if result else 0
        except sqlite3.Error as e:
            raise DatabaseException(
                operation="get_total_image_count",
                message=f"获取图片总数失败: {str(e)}"
            )
    
    def delete_image(self, file_path: str) -> bool:
        """从数据库中删除图片"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # 先获取图片ID
                cursor.execute("SELECT id FROM image_metadata WHERE file_path = ?", (file_path,))
                row = cursor.fetchone()
                if not row:
                    return False
                
                image_id = row[0]
                
                # 删除缩略图
                cursor.execute("DELETE FROM image_thumbnails WHERE image_id = ?", (image_id,))
                
                # 删除基础信息
                cursor.execute("DELETE FROM image_metadata WHERE id = ?", (image_id,))
                
                conn.commit()
                return True
        except sqlite3.Error as e:
            raise DatabaseException(
                operation="delete_image",
                message=f"删除图片失败: {str(e)}",
                details={"file_path": file_path}
            )
    
    def update_image_favorite(self, image_id: int, is_favorite: bool) -> bool:
        """更新图片收藏状态"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('UPDATE image_metadata SET is_favorite = ? WHERE id = ?', (int(is_favorite), image_id))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            raise DatabaseException(
                operation="update_image_favorite",
                message=f"更新图片收藏状态失败: {str(e)}",
                details={"image_id": image_id, "is_favorite": is_favorite}
            )
    
    def toggle_favorite(self, image_id: int) -> bool:
        """切换图片收藏状态"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                # 先获取当前收藏状态
                cursor.execute('SELECT is_favorite FROM image_metadata WHERE id = ?', (image_id,))
                row = cursor.fetchone()
                if not row:
                    return False
                
                # 切换状态
                new_favorite = not row[0]
                cursor.execute('UPDATE image_metadata SET is_favorite = ? WHERE id = ?', (int(new_favorite), image_id))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            raise DatabaseException(
                operation="toggle_favorite",
                message=f"切换图片收藏状态失败: {str(e)}",
                details={"image_id": image_id}
            )
    
    def update_image_rating(self, image_id: int, rating: int) -> bool:
        """更新图片评分（仅更新数据库）"""
        try:
            # 更新数据库
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('UPDATE image_metadata SET rating = ? WHERE id = ?', (rating, image_id))
                conn.commit()
                
                if cursor.rowcount == 0:
                    print(f"数据库中未找到图片ID: {image_id}")
                    return False
            
            print(f"成功更新图片评分: ID={image_id}, 评分={rating}")
            return True
            
        except sqlite3.Error as e:
            raise DatabaseException(
                operation="update_image_rating",
                message=f"更新图片评分失败: {str(e)}",
                details={"image_id": image_id, "rating": rating}
            )
    
    def update_image(self, file_path: str, image_data: Dict[str, Any]) -> bool:
        """更新图片信息"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                exif_json = json.dumps(image_data.get('exif_data', {})) if image_data.get('exif_data') else None
                
                # 获取图片ID
                cursor.execute("SELECT id FROM image_metadata WHERE file_path = ?", (file_path,))
                row = cursor.fetchone()
                if not row:
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
                        format=image_data.get('format'),
                        rating=image_data.get('rating')
                    )
                
                image_id = row[0]
                
                # 更新基础信息
                cursor.execute('''
                    UPDATE image_metadata SET
                        filename = ?,
                        file_size = ?,
                        created_at = ?,
                        modified_at = ?,
                        exif_data = ?,
                        width = ?,
                        height = ?,
                        format = ?,
                        rating = ?

                    WHERE id = ?
                ''', (
                    image_data.get('filename'),
                    image_data.get('file_size'),
                    image_data.get('created_at'),
                    image_data.get('modified_at'),
                    exif_json,
                    image_data.get('width'),
                    image_data.get('height'),
                    image_data.get('format'),
                    image_data.get('rating'),

                    image_id
                ))
                
                # 更新缩略图（如果提供了新的缩略图）
                if image_data.get('thumbnail'):
                    cursor.execute('''
                        INSERT OR REPLACE INTO image_thumbnails (image_id, thumbnail)
                        VALUES (?, ?)
                    ''', (image_id, image_data.get('thumbnail')))
                
                conn.commit()
                return True
        except sqlite3.Error as e:
            raise DatabaseException(
                operation="update_image",
                message=f"更新图片失败: {str(e)}",
                details={"file_path": file_path}
            )
        except json.JSONEncodeError as e:
            raise ImageProcessingException(
                operation="serialize_exif",
                message=f"EXIF数据序列化失败: {str(e)}",
                details={"file_path": file_path}
            )
    
    def get_favorite_images(self) -> List[Dict[str, Any]]:
        """获取收藏的图片"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                query = '''
                    SELECT id, filename, file_path, file_size, created_at, modified_at, 
                           exif_data, directory_path, width, height, 
                           format, is_favorite, rating, added_at
                    FROM image_metadata WHERE is_favorite = 1
                    ORDER BY modified_at DESC
                '''

                cursor.execute(query)
                
                rows = cursor.fetchall()
                images = []
                for row in rows:
                    image_id = row[0]
                    
                    # 获取缩略图
                    cursor.execute('''
                        SELECT thumbnail FROM image_thumbnails
                        WHERE image_id = ?
                    ''', (image_id,))
                    thumbnail_row = cursor.fetchone()
                    thumbnail = thumbnail_row[0] if thumbnail_row else None
                    
                    images.append({
                        "id": image_id,
                        "filename": row[1], "file_path": row[2], "file_size": row[3],
                        "created_at": row[4], "modified_at": row[5], "thumbnail_url": f"/api/thumbnail/{image_id}",
                        "exif_data": json.loads(row[6]) if row[6] else {},
                        "directory_path": row[7], "width": row[8], "height": row[9],
                        "format": row[10], "is_favorite": bool(row[11]),
                        "rating": row[12], "added_at": row[13]
                    })
                return images
        except sqlite3.Error as e:
            raise DatabaseException(
                operation="get_favorite_images",
                message=f"获取收藏图片失败: {str(e)}"
            )
        except json.JSONDecodeError as e:
            raise ImageProcessingException(
                operation="parse_exif",
                message=f"EXIF数据解析失败: {str(e)}"
            )

    def get_image_by_id(self, image_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取图片信息"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, filename, file_path, file_size, created_at, modified_at, 
                           exif_data, directory_path, width, height, 
                           format, is_favorite, rating, added_at
                    FROM image_metadata WHERE id = ?
                ''', (image_id,))
                
                row = cursor.fetchone()
                if row:
                    return {
                        "id": row[0],
                        "filename": row[1], "file_path": row[2], "file_size": row[3],
                        "created_at": row[4], "modified_at": row[5],
                        "thumbnail_url": f"/api/thumbnail/{row[0]}",
                        "exif_data": json.loads(row[6]) if row[6] else {},
                        "directory_path": row[7], "width": row[8], "height": row[9],
                        "format": row[10], "is_favorite": bool(row[11]),
                        "rating": row[12], "added_at": row[13]
                    }
                return None
        except sqlite3.Error as e:
            raise DatabaseException(
                operation="get_image_by_id",
                message=f"根据ID获取图片失败: {str(e)}",
                details={"image_id": image_id}
            )
        except json.JSONDecodeError as e:
            raise ImageProcessingException(
                operation="parse_exif",
                message=f"EXIF数据解析失败: {str(e)}"
            )

    def get_thumbnail(self, image_id: int) -> Optional[bytes]:
        """获取图片缩略图"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT thumbnail FROM image_thumbnails WHERE image_id = ?', (image_id,))
                row = cursor.fetchone()
                return row[0] if row else None
        except sqlite3.Error as e:
            raise DatabaseException(
                operation="get_thumbnail",
                message=f"获取缩略图失败: {str(e)}",
                details={"image_id": image_id}
            )

    def get_thumbnail_by_id(self, image_id: int) -> Optional[bytes]:
        """根据ID获取缩略图bytes数据"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT thumbnail FROM image_thumbnails WHERE image_id = ?
                ''', (image_id,))
                
                row = cursor.fetchone()
                if row and row[0]:
                    return row[0]  # 直接返回bytes数据
                return None
        except sqlite3.Error as e:
            raise DatabaseException(
                operation="get_thumbnail_by_id",
                message=f"获取缩略图失败: {str(e)}",
                details={"image_id": image_id}
            )