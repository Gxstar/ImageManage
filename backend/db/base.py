import os
import sqlite3
from typing import Any, Dict, List, Optional

class BaseDB:
    """基础数据库连接类"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'directories.db')
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """初始化数据库表结构"""
        conn = self.get_connection()
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
        
        # 创建图片基础信息表（不包含缩略图）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS image_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                file_path TEXT UNIQUE NOT NULL,
                file_size INTEGER,
                created_at TIMESTAMP,
                modified_at TIMESTAMP,
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
        
        # 创建缩略图表（仅包含缩略图数据）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS image_thumbnails (
                image_id INTEGER PRIMARY KEY,
                thumbnail BLOB,
                FOREIGN KEY (image_id) REFERENCES image_metadata(id) ON DELETE CASCADE
            )
        ''')
        
        # 创建旧表迁移检查
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='images'")
        if cursor.fetchone():
            # 如果旧表存在，执行数据迁移
            self.migrate_old_table(cursor, conn)
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_image_metadata_directory ON image_metadata(directory_path)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_image_metadata_path ON image_metadata(file_path)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_image_metadata_filename ON image_metadata(filename)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_image_metadata_favorite ON image_metadata(is_favorite)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_image_metadata_modified ON image_metadata(modified_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_image_metadata_created ON image_metadata(created_at)')
        
        conn.commit()
        conn.close()
    
    def migrate_old_table(self, cursor, conn):
        """从旧表迁移数据到新表结构"""
        try:
            print("检测到旧表结构，开始数据迁移...")
            
            # 1. 从旧表获取所有数据
            cursor.execute('''
                SELECT id, filename, file_path, file_size, created_at, modified_at,
                       thumbnail, exif_data, directory_path, width, height,
                       format, is_favorite, rating, added_at
                FROM images
            ''')
            
            rows = cursor.fetchall()
            if not rows:
                print("旧表无数据，跳过迁移")
                return
            
            print(f"发现 {len(rows)} 条记录需要迁移")
            
            # 2. 迁移到新的分表结构
            for row in rows:
                # 插入基础信息到image_metadata表
                cursor.execute('''
                    INSERT INTO image_metadata 
                    (id, filename, file_path, file_size, created_at, modified_at,
                     exif_data, directory_path, width, height, format, is_favorite, rating, added_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row[0], row[1], row[2], row[3], row[4], row[5],
                    row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14]
                ))
                
                # 插入缩略图到image_thumbnails表
                if row[6]:  # thumbnail 不为空
                    cursor.execute('''
                        INSERT INTO image_thumbnails (image_id, thumbnail)
                        VALUES (?, ?)
                    ''', (row[0], row[6]))
            
            # 3. 删除旧表（重命名备份）
            cursor.execute('ALTER TABLE images RENAME TO images_backup')
            
            print("数据迁移完成，旧表已重命名为images_backup")
            
        except Exception as e:
            print(f"数据迁移失败: {str(e)}")
            conn.rollback()
            raise