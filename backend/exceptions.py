"""
统一异常处理框架
"""

class ImageManagerException(Exception):
    """图片管理器基础异常类"""
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "GENERAL_ERROR"
        self.details = details or {}

class FileNotFoundException(ImageManagerException):
    """文件未找到异常"""
    def __init__(self, file_path: str, message: str = None):
        super().__init__(
            message or f"文件未找到: {file_path}",
            error_code="FILE_NOT_FOUND",
            details={"file_path": file_path}
        )

class DatabaseException(ImageManagerException):
    """数据库操作异常"""
    def __init__(self, operation: str, message: str = None, details: dict = None):
        super().__init__(
            message or f"数据库操作失败: {operation}",
            error_code="DATABASE_ERROR",
            details={"operation": operation, **(details or {})}
        )

class ImageProcessingException(ImageManagerException):
    """图片处理异常"""
    def __init__(self, operation: str, message: str = None, details: dict = None):
        super().__init__(
            message or f"图片处理失败: {operation}",
            error_code="IMAGE_PROCESSING_ERROR",
            details={"operation": operation, **(details or {})}
        )

class ValidationException(ImageManagerException):
    """数据验证异常"""
    def __init__(self, field: str, message: str = None, details: dict = None):
        super().__init__(
            message or f"数据验证失败: {field}",
            error_code="VALIDATION_ERROR",
            details={"field": field, **(details or {})}
        )

class ScanException(ImageManagerException):
    """扫描异常"""
    def __init__(self, directory: str, message: str = None, details: dict = None):
        super().__init__(
            message or f"目录扫描失败: {directory}",
            error_code="SCAN_ERROR",
            details={"directory": directory, **(details or {})}
        )

import logging
import traceback
from typing import Any, Dict, Optional
from functools import wraps

logger = logging.getLogger(__name__)

def handle_exception(
    default_return=None,
    log_level: int = logging.ERROR,
    reraise: bool = False,
    error_message: str = None
):
    """统一异常处理装饰器
    
    Args:
        default_return: 异常时的默认返回值
        log_level: 日志级别
        reraise: 是否重新抛出异常
        error_message: 自定义错误消息
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ImageManagerException as e:
                # 已知的业务异常，记录警告级别
                logger.warning(f"{error_message or func.__name__} failed: {e.message}")
                if reraise:
                    raise
                return default_return
            except Exception as e:
                # 未知异常，记录错误级别和完整堆栈
                logger.error(
                    f"{error_message or func.__name__} failed with unexpected error: {str(e)}",
                    exc_info=True
                )
                if reraise:
                    raise ImageManagerException(
                        f"操作失败: {str(e)}",
                        error_code="UNEXPECTED_ERROR"
                    )
                return default_return
        return wrapper
    return decorator

def safe_execute(
    func,
    *args,
    default_return=None,
    error_message: str = None,
    **kwargs
):
    """安全执行函数的工具方法
    
    Args:
        func: 要执行的函数
        *args: 位置参数
        default_return: 异常时的默认返回值
        error_message: 自定义错误消息
        **kwargs: 关键字参数
        
    Returns:
        函数执行结果或默认值
    """
    try:
        return func(*args, **kwargs)
    except ImageManagerException as e:
        logger.warning(f"{error_message or func.__name__} failed: {e.message}")
        return default_return
    except Exception as e:
        logger.error(
            f"{error_message or func.__name__} failed: {str(e)}",
            exc_info=True
        )
        return default_return

def format_error_response(error: Exception) -> Dict[str, Any]:
    """格式化错误响应
    
    Args:
        error: 异常对象
        
    Returns:
        格式化的错误信息
    """
    if isinstance(error, ImageManagerException):
        return {
            "success": False,
            "error": {
                "message": error.message,
                "code": error.error_code,
                "details": error.details
            }
        }
    else:
        return {
            "success": False,
            "error": {
                "message": str(error),
                "code": "UNEXPECTED_ERROR",
                "details": {}
            }
        }