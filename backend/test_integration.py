#!/usr/bin/env python3
"""
集成测试：验证album_manager使用query_images方法获取相册图片
"""

import sys
import os

# 添加backend目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.album_manager import AlbumManager
from db.image_manager import ImageManager

def test_album_integration():
    """测试相册和图片的集成"""
    print("=== 开始集成测试 ===")
    
    album_manager = AlbumManager()
    image_manager = ImageManager()
    
    try:
        # 1. 创建测试相册
        print("1. 创建测试相册...")
        album_id = album_manager.create_album(
            name="集成测试相册",
            description="用于验证query_images集成的测试相册"
        )
        print(f"   相册创建成功，ID: {album_id}")
        
        # 2. 检查是否有图片可以添加到相册
        print("2. 检查可用图片...")
        all_images = image_manager.query_images(limit=5)
        print(f"   找到 {len(all_images)} 张图片")
        
        if all_images:
            # 3. 添加图片到相册
            print("3. 添加图片到相册...")
            image_ids = [img["id"] for img in all_images[:2]]  # 添加前2张
            album_manager.add_images_to_album(album_id, image_ids)
            print(f"   成功添加 {len(image_ids)} 张图片到相册")
            
            # 4. 使用album_manager的get_album_images方法（现在应该使用query_images）
            print("4. 测试get_album_images方法...")
            album_images = album_manager.get_album_images(album_id)
            print(f"   相册中包含 {len(album_images)} 张图片")
            
            # 5. 验证排序功能
            print("5. 测试排序功能...")
            sorted_by_name = album_manager.get_album_images(album_id, sort_by="filename")
            print(f"   按文件名排序: {[img['filename'] for img in sorted_by_name]}")
            
            sorted_by_order = album_manager.get_album_images(album_id, sort_by="sort_order")
            print(f"   按排序字段排序: {[img.get('sort_order', 'N/A') for img in sorted_by_order]}")
            
            # 6. 验证query_images的album_id参数
            print("6. 验证query_images的album_id参数...")
            direct_query = image_manager.query_images(album_id=album_id)
            print(f"   直接查询相册图片: {len(direct_query)} 张")
            
            # 7. 清理测试数据
            print("7. 清理测试数据...")
            album_manager.delete_album(album_id)
            print("   测试相册已删除")
            
            print("\n=== 集成测试完成 ===")
            return True
        else:
            print("   没有可用的图片进行测试，跳过图片相关测试")
            album_manager.delete_album(album_id)
            print("   测试相册已删除")
            print("\n=== 集成测试完成（无图片测试）===")
            return True
            
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_album_integration()
    sys.exit(0 if success else 1)