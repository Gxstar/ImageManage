# 相册功能使用指南

## 架构概述
相册功能采用三层架构设计：
- **数据库层**: `db/album_manager.py` - 数据库操作
- **业务逻辑层**: `services/album_service.py` - 业务逻辑和验证
- **接口层**: `api.py` - 对外API接口

## 数据库结构
相册功能主要涉及两个表：
- `albums`: 存储相册基本信息
- `album_images`: 存储相册与图片的关联关系

## API接口使用

### 初始化API
```python
from api import Api

# 创建API实例
api = Api()
```

### 创建相册
```python
# 创建新相册
result = api.create_album("我的旅行", "2024年春季旅行照片")
if result["success"]:
    album_id = result["album_id"]
    print(f"相册创建成功，ID: {album_id}")

# 创建带封面的相册
result = api.create_album("精选", "最喜欢的照片", cover_image_id=123)
```

### 获取相册列表
```python
# 获取所有相册
result = api.get_all_albums(include_stats=True)
if result["success"]:
    albums = result["albums"]
    total = result["total"]
    print(f"共有 {total} 个相册")
```

### 获取相册详情
```python
# 获取单个相册详情
result = api.get_album_details(album_id)
if result["success"]:
    album = result["album"]
    print(f"相册名称: {album['name']}")
    print(f"图片数量: {album['image_count']}")
```

### 更新相册信息
```python
# 更新相册名称和描述
result = api.update_album(album_id, name="新名称", description="新描述")

# 更新封面图片
result = api.update_album(album_id, cover_image_id=456)
```

### 删除相册
```python
result = api.delete_album(album_id)
if result["success"]:
    print("相册删除成功")
```

### 搜索相册
```python
# 搜索相册
result = api.search_albums("旅行")
if result["success"]:
    albums = result["albums"]
    print(f"找到 {len(albums)} 个匹配的相册")
```

## 图片管理接口

### 添加图片到相册
```python
# 添加多张图片到相册
image_ids = [101, 102, 103]
result = api.add_images_to_album(album_id, image_ids)
if result["success"]:
    print(f"成功添加 {result['added_count']} 张图片")
```

### 从相册移除图片
```python
# 从相册移除图片
image_ids_to_remove = [101, 102]
result = api.remove_images_from_album(album_id, image_ids_to_remove)
if result["success"]:
    print(f"成功移除 {result['removed_count']} 张图片")
```

### 获取相册中的图片
```python
# 获取相册中的所有图片
result = api.get_album_images(album_id, limit=20, offset=0)
if result["success"]:
    images = result["images"]
    total = result["total"]
    album_info = result["album_info"]
    print(f"相册 {album_info['name']} 中有 {total} 张图片")

# 按文件名排序获取图片
result = api.get_album_images(album_id, sort_by="filename", sort_order="asc")
```

### 更新图片排序
```python
# 设置图片排序顺序
image_orders = [
    {"image_id": 101, "sort_order": 1},
    {"image_id": 102, "sort_order": 2},
    {"image_id": 103, "sort_order": 3}
]
result = api.update_album_image_sort_order(album_id, image_orders)
```

## 数据库层使用（高级用法）
如果需要直接操作数据库层，可以使用：

```python
from db.album_manager import AlbumManager

# 创建相册管理器实例
album_manager = AlbumManager()

# 所有API接口中的方法都可以直接使用
album_id = album_manager.create_album("测试相册")
```

## 错误处理
所有API接口都返回统一格式的响应：

```python
# 成功响应
{
    "success": True,
    "data": {...},  # 或其他相关字段
    "message": "操作成功"
}

# 错误响应
{
    "success": False,
    "error": "错误描述"
}
```

## 完整示例

```python
from api import Api

def create_and_manage_album():
    api = Api()
    
    # 1. 创建相册
    result = api.create_album("日本旅行", "2024年4月日本之行")
    if not result["success"]:
        print(f"创建失败: {result['error']}")
        return
    
    album_id = result["album_id"]
    
    # 2. 获取一些图片（假设我们有图片ID）
    images_result = api.get_all_images(limit=10)
    if images_result["success"] and images_result["images"]:
        image_ids = [img["id"] for img in images_result["images"][:5]]
        
        # 3. 添加图片到相册
        add_result = api.add_images_to_album(album_id, image_ids)
        if add_result["success"]:
            print(f"添加了 {add_result['added_count']} 张图片")
    
    # 4. 获取相册详情
    details_result = api.get_album_details(album_id)
    if details_result["success"]:
        album = details_result["album"]
        print(f"相册 '{album['name']}' 现在有 {album['image_count']} 张图片")
    
    # 5. 搜索相册
    search_result = api.search_albums("旅行")
    if search_result["success"]:
        print(f"搜索到 {search_result['total']} 个相关相册")
    
    return album_id
```

## 架构优势
1. **清晰的职责分离**: 数据库层负责数据存储，服务层负责业务逻辑，API层负责接口暴露
2. **统一的错误处理**: 所有异常都在服务层处理，返回统一的响应格式
3. **参数验证**: 服务层进行参数验证，保证数据完整性
4. **易于测试**: 各层独立，便于单元测试和集成测试