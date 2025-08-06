import sqlite3
import os
from typing import Optional

class BaseDB:
    """基础数据库连接类"""
    
    def __init__(self, db_path: str = "../directories.db"):
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