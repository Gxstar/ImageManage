#!/usr/bin/env python3
"""
数据库迁移脚本
将旧数据库结构迁移到新的分表结构
"""

import os
import sys
import sqlite3
from pathlib import Path

# 添加backend目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from db.base import BaseDB

def migrate_database():
    """执行数据库迁移"""
    db_path = os.path.join(os.path.dirname(__file__), 'backend', 'data', 'images.db')
    
    if not os.path.exists(db_path):
        print("数据库文件不存在，无需迁移")
        return
    
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查旧表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='images'")
        if not cursor.fetchone():
            print("旧表不存在，无需迁移")
            return
        
        # 检查新表是否已经存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='image_metadata'")
        if cursor.fetchone():
            print("新表已存在，跳过迁移")
            return
        
        print("开始数据库迁移...")
        
        # 创建新的表结构
        base_db = BaseDB()
        base_db.init_database()
        
        # 迁移数据
        cursor.execute('''
            SELECT id, filename, file_path, file_size, created_at, modified_at,
                   thumbnail, exif_data, directory_path, width, height, 
                   format, is_favorite, rating, added_at
            FROM images
        ''')
        
        old_images = cursor.fetchall()
        
        if not old_images:
            print("旧表中没有数据，无需迁移")
            return
        
        print(f"发现 {len(old_images)} 条旧数据，开始迁移...")
        
        # 开始事务
        conn.execute('BEGIN TRANSACTION')
        
        migrated_count = 0
        for row in old_images:
            try:
                # 插入基础信息到image_metadata表
                cursor.execute('''
                    INSERT INTO image_metadata 
                    (filename, file_path, file_size, created_at, modified_at,
                     exif_data, directory_path, width, height, format, 
                     is_favorite, rating, added_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row[1], row[2], row[3], row[4], row[5],
                    row[7], row[8], row[9], row[10], row[11],
                    row[12], row[13], row[14]
                ))
                
                # 获取新插入的ID
                new_id = cursor.lastrowid
                
                # 插入缩略图到image_thumbnails表
                if row[6]:  # thumbnail
                    cursor.execute('''
                        INSERT INTO image_thumbnails (image_id, thumbnail)
                        VALUES (?, ?)
                    ''', (new_id, row[6]))
                
                migrated_count += 1
                
                if migrated_count % 50 == 0:
                    print(f"已迁移 {migrated_count}/{len(old_images)} 条数据")
                    
            except Exception as e:
                print(f"迁移单条数据失败: {str(e)}")
                continue
        
        # 重命名旧表为备份
        cursor.execute("ALTER TABLE images RENAME TO images_backup")
        
        # 提交事务
        conn.commit()
        
        print(f"数据库迁移完成！共迁移 {migrated_count} 条数据")
        print("旧表已重命名为 images_backup")
        
    except Exception as e:
        conn.rollback()
        print(f"数据库迁移失败: {str(e)}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()