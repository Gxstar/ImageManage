import os
import threading
import time
from pathlib import Path
from typing import List, Tuple
from PIL import Image
from db import DatabaseManager
from image_utils import ImageProcessor
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BackgroundScanner:
    """后台图片扫描器"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
        self.scan_thread = None
        self.is_running = False
        self.directory_cache = {}  # 缓存目录修改时间
        
    def start_scanning(self):
        """启动后台扫描线程"""
        if self.scan_thread is None or not self.scan_thread.is_alive():
            self._initialize_directory_cache()
            self.is_running = True
            self.scan_thread = threading.Thread(target=self._scan_worker, daemon=True)
            self.scan_thread.start()
            logger.info("后台图片扫描线程已启动")
    
    def _initialize_directory_cache(self):
        """初始化目录缓存"""
        try:
            directories = self.db_manager.get_directories()
            for directory in directories:
                directory_path = directory['path']
                if os.path.exists(directory_path):
                    self.directory_cache[directory_path] = os.path.getmtime(directory_path)
            logger.info(f"已初始化 {len(self.directory_cache)} 个目录的缓存")
        except Exception as e:
            logger.error(f"初始化目录缓存失败: {e}")
    
    def stop_scanning(self):
        """停止后台扫描"""
        self.is_running = False
        logger.info("后台图片扫描线程已停止")
    
    def _scan_worker(self):
        """后台扫描工作线程"""
        scan_count = 0
        while self.is_running:
            try:
                start_time = time.time()
                self._scan_all_directories()
                scan_duration = time.time() - start_time
                scan_count += 1
                
                logger.info(f"第{scan_count}次扫描完成，耗时{scan_duration:.2f}秒")
                
                # 每2小时扫描一次，根据扫描时长动态调整
                sleep_time = max(7200 - scan_duration, 60)  # 至少等待1分钟
                time.sleep(sleep_time)
            except Exception as e:
                logger.error(f"后台扫描出错: {e}")
                time.sleep(300)  # 出错后等待5分钟再重试
    
    def _scan_all_directories(self):
        """扫描所有已存储的目录，智能检测变化"""
        directories = self.db_manager.get_directories()
        total_scanned = 0
        
        for directory in directories:
            directory_path = directory['path']
            if not os.path.exists(directory_path):
                continue
                
            # 检查目录是否有变化
            if not self._should_scan_directory(directory_path):
                continue
                
            logger.info(f"检测到目录变化，开始扫描: {directory_path}")
            scanned_count = self._scan_directory(directory_path)
            total_scanned += scanned_count
            
            # 更新缓存
            self._update_directory_cache(directory_path)
            
        logger.info(f"本次扫描共处理 {total_scanned} 个文件")
    
    def _should_scan_directory(self, directory_path: str) -> bool:
        """判断是否需要扫描目录"""
        try:
            # 获取目录最后修改时间
            current_mtime = os.path.getmtime(directory_path)
            last_mtime = self.directory_cache.get(directory_path, 0)
            
            # 如果目录修改时间变化大于1秒，需要重新扫描
            return abs(current_mtime - last_mtime) > 1.0
        except (OSError, KeyError):
            return True
    
    def _update_directory_cache(self, directory_path: str):
        """更新目录缓存"""
        try:
            self.directory_cache[directory_path] = os.path.getmtime(directory_path)
        except OSError:
            pass
    
    def _scan_directory(self, directory_path: str) -> int:
        """扫描指定目录及其子目录，返回扫描的文件数量"""
        scanned_count = 0
        
        # 获取所有子目录
        all_dirs = []
        for root, dirs, files in os.walk(directory_path):
            all_dirs.append(root)
        
        # 扫描每个目录
        for dir_path in all_dirs:
            scanned_count += self._scan_single_directory(dir_path)
            
        return scanned_count
    
    def _scan_single_directory(self, dir_path: str) -> int:
        """扫描单个目录中的图片，返回处理的文件数量"""
        processed_count = 0
        try:
            files = os.listdir(dir_path)
            
            for filename in files:
                file_path = os.path.join(dir_path, filename)
                
                # 检查是否为支持的图片格式
                if Path(filename).suffix.lower() in self.supported_formats:
                    if self._process_image(file_path):
                        processed_count += 1
                    
        except Exception as e:
            logger.error(f"扫描目录 {dir_path} 时出错: {e}")
            
        return processed_count
    
    def _process_image(self, file_path: str) -> bool:
        """处理单个图片文件，返回是否成功处理"""
        try:
            # 检查文件是否已存在
            existing_image = self.db_manager.get_image_by_path(file_path)
            
            # 获取文件信息
            stat = os.stat(file_path)
            
            # 更精确的变化检测：检查修改时间和文件大小
            is_modified = False
            if not existing_image:
                is_modified = True
            else:
                # 检查修改时间（允许1秒误差）
                time_changed = abs(existing_image['modified_at'] - stat.st_mtime) > 1.0
                # 检查文件大小
                size_changed = existing_image['file_size'] != stat.st_size
                is_modified = time_changed or size_changed
            
            if not is_modified:
                return False  # 文件未变化，跳过处理
                
            # 添加小延迟避免CPU过度占用
            time.sleep(0.01)
            
            # 获取图片信息
            with Image.open(file_path) as img:
                width, height = img.size
                format_name = img.format
            
            # 获取EXIF数据
            exif_result = ImageProcessor.get_exif_data(file_path)
            exif_data = exif_result.get('exif', {}) if 'error' not in exif_result else None
            
            # 生成缩略图
            thumbnail = ImageProcessor.generate_thumbnail(file_path, (150, 150))
            
            # 准备图片数据
            image_data = {
                'filename': os.path.basename(file_path),
                'file_path': file_path,
                'file_size': stat.st_size,
                'created_at': stat.st_ctime,
                'modified_at': stat.st_mtime,
                'directory_path': os.path.dirname(file_path),
                'width': width,
                'height': height,
                'format': format_name,
                'thumbnail': thumbnail,
                'exif_data': exif_data
            }
            
            # 保存到数据库
            if existing_image:
                # 更新现有记录
                self.db_manager.update_image(file_path, image_data)
                logger.info(f"更新图片: {file_path}")
            else:
                # 添加新记录
                self.db_manager.add_image(**image_data)
                logger.info(f"添加新图片: {file_path}")
                
            return True
            
        except Exception as e:
            logger.error(f"处理图片 {file_path} 时出错: {e}")
            return False

# 全局扫描器实例
background_scanner = BackgroundScanner()