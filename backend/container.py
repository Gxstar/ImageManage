"""
依赖容器 - 简化依赖管理，避免重复实例化
"""
from typing import Optional
from db import DatabaseManager

class Container:
    """轻量级依赖容器，管理共享实例"""
    
    _db_manager: Optional[DatabaseManager] = None
    
    @classmethod
    def get_db_manager(cls) -> DatabaseManager:
        """获取数据库管理器单例"""
        if cls._db_manager is None:
            cls._db_manager = DatabaseManager()
        return cls._db_manager
    
    @classmethod
    def reset(cls):
        """重置所有实例（用于测试）"""
        cls._db_manager = None

# 全局访问点
dependencies = Container()