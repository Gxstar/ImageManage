import os
import threading
import time
import logging
from pathlib import Path
from typing import List, Tuple

from PIL import Image

from db import DatabaseManager
from image_utils import ImageProcessor

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
        
    def start_scanning(self):
        """启动后台扫描线程"""
        if self.scan_thread is None or not self.scan_thread.is_alive():
            self.is_running = True
            self.scan_thread = threading.Thread(target=self._scan_worker, daemon=True)
            self.scan_thread.start()
            logger.info("后台图片扫描线程已启动")
    
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
                
                # 每30分钟扫描一次
                time.sleep(1800)
            except Exception as e:
                logger.error(f"后台扫描出错: {e}")
                time.sleep(300)  # 出错后等待5分钟再重试
    
    def _scan_all_directories(self):
        """扫描所有已存储的目录"""
        directories = self.db_manager.get_directories()
        total_scanned = 0
        
        for directory in directories:
            directory_path = directory['path']
            if not os.path.exists(directory_path):
                continue
                
            logger.info(f"开始扫描目录: {directory_path}")
            scanned_count = self._scan_directory(directory_path)
            total_scanned += scanned_count
            
        logger.info(f"本次扫描共处理 {total_scanned} 个文件")
    
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
            # 获取文件信息
            stat = os.stat(file_path)
            
            # 获取图片信息
            with Image.open(file_path) as img:
                width, height = img.size
                format_name = img.format
            
            # 获取EXIF数据
            exif_result = ImageProcessor.get_exif_data(file_path)
            exif_data = exif_result.get('exif', {}) if 'error' not in exif_result else None
            
            # 生成缩略图 - 使用更大尺寸确保清晰度
            thumbnail = ImageProcessor.generate_thumbnail(file_path, (400, 400))
            
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
            existing_image = self.db_manager.get_image_by_path(file_path)
            if existing_image:
                self.db_manager.update_image(file_path, image_data)
                # logger.info(f"更新图片: {file_path}")
            else:
                self.db_manager.add_image(**image_data)
                # logger.info(f"添加新图片: {file_path}")
                
            return True
            
        except Exception as e:
            # logger.error(f"处理图片 {file_path} 时出错: {e}")
            return False

# 全局扫描器实例
background_scanner = BackgroundScanner()