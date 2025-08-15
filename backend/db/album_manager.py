import sqlite3
import json
from typing import Any, Dict, List, Optional
from datetime import datetime
from .base import BaseDB
from exceptions import DatabaseException, ImageProcessingException


class AlbumManager(BaseDB):
    """相册管理类 - 处理相册相关的数据库操作"""
    
    def __init__(self, db_path: str = None):
        super().__init__(db_path)
        self.init_album_tables()
    
    def init_album_tables(self):
        """初始化相册相关的数据库表"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 创建相册表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS albums (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT DEFAULT '',
                cover_image_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cover_image_id) REFERENCES image_metadata(id) ON DELETE SET NULL
            )
        ''')
        
        # 创建相册-图片关联表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS album_images (
                album_id INTEGER NOT NULL,
                image_id INTEGER NOT NULL,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sort_order INTEGER DEFAULT 0,
                PRIMARY KEY (album_id, image_id),
                FOREIGN KEY (album_id) REFERENCES albums(id) ON DELETE CASCADE,
                FOREIGN KEY (image_id) REFERENCES image_metadata(id) ON DELETE CASCADE
            )
        ''')
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_albums_name ON albums(name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_album_images_album ON album_images(album_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_album_images_image ON album_images(image_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_album_images_sort ON album_images(sort_order)')
        
        conn.commit()
        conn.close()
    
    def create_album(self, name: str, description: str = "", cover_image_id: Optional[int] = None) -> int:
        """创建新相册
        
        Args:
            name: 相册名称
            description: 相册描述
            cover_image_id: 封面图片ID
            
        Returns:
            新创建的相册ID
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO albums (name, description, cover_image_id)
                    VALUES (?, ?, ?)
                ''', (name, description, cover_image_id))
                
                album_id = cursor.lastrowid
                conn.commit()
                return album_id
        except sqlite3.Error as e:
            raise DatabaseException(
                operation="create_album",
                message=f"创建相册失败: {str(e)}",
                details={"name": name, "description": description, "cover_image_id": cover_image_id}
            )
    
    def update_album(self, album_id: int, name: str = None, description: str = None, 
                    cover_image_id: Optional[int] = None) -> bool:
        """更新相册信息
        
        Args:
            album_id: 相册ID
            name: 相册名称（可选）
            description: 相册描述（可选）
            cover_image_id: 封面图片ID（可选）
            
        Returns:
            是否更新成功
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                updates = []
                params = []
                
                if name is not None:
                    updates.append("name = ?")
                    params.append(name)
                
                if description is not None:
                    updates.append("description = ?")
                    params.append(description)
                
                if cover_image_id is not None:
                    updates.append("cover_image_id = ?")
                    params.append(cover_image_id)
                
                if updates:
                    updates.append("updated_at = CURRENT_TIMESTAMP")
                    query = f"UPDATE albums SET {', '.join(updates)} WHERE id = ?"
                    params.append(album_id)
                    
                    cursor.execute(query, params)
                    conn.commit()
                    return cursor.rowcount > 0
                
                return False
        except sqlite3.Error as e:
            raise DatabaseException(
                operation="update_album",
                message=f"更新相册失败: {str(e)}",
                details={"album_id": album_id, "name": name, "description": description, "cover_image_id": cover_image_id}
            )
    
    def delete_album(self, album_id: int) -> bool:
        """删除相册
        
        Args:
            album_id: 相册ID
            
        Returns:
            是否删除成功
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM albums WHERE id = ?', (album_id,))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            raise DatabaseException(
                operation="delete_album",
                message=f"删除相册失败: {str(e)}",
                details={"album_id": album_id}
            )
    
    def get_albums(self, include_stats: bool = False) -> List[Dict[str, Any]]:
        """获取所有相册
        
        Args:
            include_stats: 是否包含统计信息（图片数量等）
            
        Returns:
            相册列表
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if include_stats:
                    query = '''
                        SELECT a.id, a.name, a.description, a.cover_image_id, 
                               a.created_at, a.updated_at, COUNT(ai.image_id) as image_count
                        FROM albums a
                        LEFT JOIN album_images ai ON a.id = ai.album_id
                        GROUP BY a.id, a.name, a.description, a.cover_image_id, a.created_at, a.updated_at
                        ORDER BY a.created_at DESC
                    '''
                else:
                    query = '''
                        SELECT id, name, description, cover_image_id, created_at, updated_at
                        FROM albums
                        ORDER BY created_at DESC
                    '''
                
                cursor.execute(query)
                
                albums = []
                for row in cursor.fetchall():
                    album = {
                        "id": row[0],
                        "name": row[1],
                        "description": row[2],
                        "cover_image_id": row[3],
                        "created_at": row[4],
                        "updated_at": row[5]
                    }
                    
                    if include_stats:
                        album["image_count"] = row[6]
                    
                    albums.append(album)
                
                return albums
        except sqlite3.Error as e:
            raise DatabaseException(
                operation="get_albums",
                message=f"获取相册列表失败: {str(e)}"
            )
    
    def get_album_by_id(self, album_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取相册详情
        
        Args:
            album_id: 相册ID
            
        Returns:
            相册详情，包含图片数量统计
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                query = '''
                    SELECT a.id, a.name, a.description, a.cover_image_id, 
                           a.created_at, a.updated_at, COUNT(ai.image_id) as image_count
                    FROM albums a
                    LEFT JOIN album_images ai ON a.id = ai.album_id
                    WHERE a.id = ?
                    GROUP BY a.id, a.name, a.description, a.cover_image_id, a.created_at, a.updated_at
                '''
                
                cursor.execute(query, (album_id,))
                row = cursor.fetchone()
                
                if row:
                    return {
                        "id": row[0],
                        "name": row[1],
                        "description": row[2],
                        "cover_image_id": row[3],
                        "created_at": row[4],
                        "updated_at": row[5],
                        "image_count": row[6]
                    }
                
                return None
        except sqlite3.Error as e:
            raise DatabaseException(
                operation="get_album_by_id",
                message=f"获取相册详情失败: {str(e)}",
                details={"album_id": album_id}
            )
    
    def add_images_to_album(self, album_id: int, image_ids: List[int]) -> int:
        """将图片添加到相册
        
        Args:
            album_id: 相册ID
            image_ids: 图片ID列表
            
        Returns:
            成功添加的图片数量
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # 获取当前最大排序值
                cursor.execute('''
                    SELECT COALESCE(MAX(sort_order), 0) 
                    FROM album_images WHERE album_id = ?
                ''', (album_id,))
                max_order = cursor.fetchone()[0]
                
                added_count = 0
                for image_id in image_ids:
                    try:
                        cursor.execute('''
                            INSERT INTO album_images (album_id, image_id, sort_order)
                            VALUES (?, ?, ?)
                        ''', (album_id, image_id, max_order + 1))
                        max_order += 1
                        added_count += 1
                    except sqlite3.IntegrityError:
                        # 图片已存在于相册中，跳过
                        pass
                
                conn.commit()
                return added_count
        except sqlite3.Error as e:
            raise DatabaseException(
                operation="add_images_to_album",
                message=f"添加图片到相册失败: {str(e)}",
                details={"album_id": album_id, "image_ids": image_ids}
            )
    
    def remove_images_from_album(self, album_id: int, image_ids: List[int]) -> int:
        """从相册中移除图片
        
        Args:
            album_id: 相册ID
            image_ids: 图片ID列表
            
        Returns:
            成功移除的图片数量
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                placeholders = ','.join(['?' for _ in image_ids])
                query = f"DELETE FROM album_images WHERE album_id = ? AND image_id IN ({placeholders})"
                
                params = [album_id] + image_ids
                cursor.execute(query, params)
                
                conn.commit()
                return cursor.rowcount
        except sqlite3.Error as e:
            raise DatabaseException(
                operation="remove_images_from_album",
                message=f"从相册移除图片失败: {str(e)}",
                details={"album_id": album_id, "image_ids": image_ids}
            )
    
    def get_album_images(self, album_id: int, limit: int = None, offset: int = 0,
                        sort_by: str = "sort_order", sort_order: str = "asc") -> List[Dict[str, Any]]:
        """获取相册中的图片列表
        
        Args:
            album_id: 相册ID
            limit: 返回数量限制
            offset: 偏移量
            sort_by: 排序字段（sort_order, album_added_at, filename, created_at, file_size）
            sort_order: 排序方式（asc, desc）
        
        Returns:
            相册中的图片列表
        """
        # 导入image_manager来查询相册图片
        from .image_manager import ImageManager
        image_manager = ImageManager()
        
        return image_manager.query_images(
            album_id=album_id,
            sort_by=sort_by,
            sort_order=sort_order,
            limit=limit,
            offset=offset
        )
    
    def get_album_image_count(self, album_id: int) -> int:
        """获取相册中的图片数量
        
        Args:
            album_id: 相册ID
            
        Returns:
            相册中的图片数量
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT COUNT(*) 
                    FROM album_images 
                    WHERE album_id = ?
                ''', (album_id,))
                
                result = cursor.fetchone()
                return result[0] if result else 0
        except sqlite3.Error as e:
            raise DatabaseException(
                operation="get_album_image_count",
                message=f"获取相册图片数量失败: {str(e)}",
                details={"album_id": album_id}
            )
    
    def update_album_image_sort_order(self, album_id: int, image_orders: List[Dict[str, int]]) -> bool:
        """更新相册中图片的排序顺序
        
        Args:
            album_id: 相册ID
            image_orders: 图片排序信息列表，每个元素包含image_id和sort_order
            
        Returns:
            是否更新成功
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                for item in image_orders:
                    cursor.execute('''
                        UPDATE album_images 
                        SET sort_order = ? 
                        WHERE album_id = ? AND image_id = ?
                    ''', (item["sort_order"], album_id, item["image_id"]))
                
                conn.commit()
                return True
        except sqlite3.Error as e:
            raise DatabaseException(
                operation="update_album_image_sort_order",
                message=f"更新相册图片排序失败: {str(e)}",
                details={"album_id": album_id, "image_orders": image_orders}
            )
    
    def is_image_in_album(self, album_id: int, image_id: int) -> bool:
        """检查图片是否在相册中
        
        Args:
            album_id: 相册ID
            image_id: 图片ID
            
        Returns:
            图片是否在相册中
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT 1 
                    FROM album_images 
                    WHERE album_id = ? AND image_id = ?
                ''', (album_id, image_id))
                
                return cursor.fetchone() is not None
        except sqlite3.Error as e:
            raise DatabaseException(
                operation="is_image_in_album",
                message=f"检查图片是否在相册中失败: {str(e)}",
                details={"album_id": album_id, "image_id": image_id}
            )
    
    def search_albums(self, keyword: str) -> List[Dict[str, Any]]:
        """搜索相册
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            匹配的相册列表
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                query = '''
                    SELECT a.id, a.name, a.description, a.cover_image_id, 
                           a.created_at, a.updated_at, COUNT(ai.image_id) as image_count
                    FROM albums a
                    LEFT JOIN album_images ai ON a.id = ai.album_id
                    WHERE a.name LIKE ? OR a.description LIKE ?
                    GROUP BY a.id, a.name, a.description, a.cover_image_id, a.created_at, a.updated_at
                    ORDER BY a.created_at DESC
                '''
                
                search_pattern = f"%{keyword}%"
                cursor.execute(query, (search_pattern, search_pattern))
                
                albums = []
                for row in cursor.fetchall():
                    albums.append({
                        "id": row[0],
                        "name": row[1],
                        "description": row[2],
                        "cover_image_id": row[3],
                        "created_at": row[4],
                        "updated_at": row[5],
                        "image_count": row[6]
                    })
                
                return albums
        except sqlite3.Error as e:
            raise DatabaseException(
                operation="search_albums",
                message=f"搜索相册失败: {str(e)}",
                details={"keyword": keyword}
            )