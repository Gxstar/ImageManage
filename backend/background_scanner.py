import os
import threading
import time
import logging
from pathlib import Path
from typing import List, Dict
import hashlib

from PIL import Image

from container import dependencies
from image_utils import ImageProcessor
from exceptions import DatabaseException, ImageProcessingException, format_error_response

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BackgroundScanner:
    """智能后台图片扫描器 - 支持增量扫描和文件系统监控"""
    
    def __init__(self):
        self.db_manager = dependencies.get_db_manager()
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
        self.scan_thread = None
        self.is_running = False
        self.file_checksums = {}  # 缓存文件校验和
        self.last_scan_times = {}  # 记录每个目录的最后扫描时间
        
    def start_scanning(self):
        """启动智能后台扫描线程"""
        if self.scan_thread is None or not self.scan_thread.is_alive():
            self.is_running = True
            self.scan_thread = threading.Thread(target=self._scan_worker, daemon=True)
            self.scan_thread.start()
            logger.info("智能后台扫描线程已启动")
    
    def stop_scanning(self):
        """停止后台扫描"""
        self.is_running = False
        logger.info("后台扫描线程已停止")
    
    def _scan_worker(self):
        """智能扫描工作线程"""
        scan_count = 0
        while self.is_running:
            try:
                start_time = time.time()
                
                # 智能扫描：只处理有变化的文件
                changed_files = self._get_changed_files()
                if changed_files:
                    logger.info(f"发现 {len(changed_files)} 个变化的文件")
                    self._process_changed_files(changed_files)
                else:
                    logger.debug("未发现文件变化")
                
                scan_duration = time.time() - start_time
                scan_count += 1
                
                if changed_files:
                    logger.info(f"第{scan_count}次增量扫描完成，处理了 {len(changed_files)} 个文件，耗时{scan_duration:.2f}秒")
                
                # 动态调整扫描间隔：有变化时快速响应，无变化时降低频率
                if changed_files:
                    time.sleep(30)  # 有变化时30秒后再次检查
                else:
                    time.sleep(300)  # 无变化时5分钟后检查
                    
            except DatabaseException as e:
                logger.error(f"数据库错误: {e}")
                time.sleep(300)
            except ImageProcessingException as e:
                logger.error(f"图片处理错误: {e}")
                time.sleep(60)
            except Exception as e:
                logger.error(f"后台扫描出错: {e}")
                time.sleep(300)
    
    def _get_changed_files(self) -> List[Dict[str, str]]:
        """获取有变化的文件列表"""
        changed_files = []
        directories = self.db_manager.get_directories()
        
        for directory in directories:
            directory_path = directory['path']
            if not os.path.exists(directory_path):
                continue
                
            # 获取该目录下的所有图片文件
            current_files = self._get_directory_files(directory_path)
            
            # 检查新增或修改的文件
            for file_path in current_files:
                if self._is_file_changed(file_path):
                    changed_files.append({
                        'path': file_path,
                        'directory': directory_path
                    })
        
        return changed_files
    
    def _get_directory_files(self, directory_path: str) -> List[str]:
        """获取目录下的所有图片文件"""
        files = []
        try:
            for root, dirs, filenames in os.walk(directory_path):
                for filename in filenames:
                    if Path(filename).suffix.lower() in self.supported_formats:
                        files.append(os.path.join(root, filename))
        except DatabaseException as e:
            logger.error(f"数据库错误 - 获取目录文件列表失败: {directory_path} - {e}")
        except Exception as e:
            logger.error(f"获取目录文件列表失败: {directory_path} - {e}")
        return files
    
    def _is_file_changed(self, file_path: str) -> bool:
        """检查文件是否有变化"""
        try:
            if not os.path.exists(file_path):
                return False
                
            # 获取文件状态
            stat = os.stat(file_path)
            
            # 计算文件校验和
            hasher = hashlib.md5()
            with open(file_path, 'rb') as f:
                buf = f.read(8192)  # 只读取前8KB用于校验
                hasher.update(buf)
            current_checksum = hasher.hexdigest()
            
            # 获取数据库中的记录
            existing_image = self.db_manager.get_image_by_path(file_path)
            
            if not existing_image:
                # 新文件
                return True
            
            # 检查修改时间和文件大小
            db_modified_time = existing_image.get('modified_at', 0)
            db_file_size = existing_image.get('file_size', 0)
            
            file_changed = (
                abs(stat.st_mtime - db_modified_time) > 1 or  # 1秒容差
                stat.st_size != db_file_size or
                current_checksum != self.file_checksums.get(file_path)
            )
            
            # 更新缓存
            if file_changed:
                self.file_checksums[file_path] = current_checksum
            
            return file_changed
            
        except DatabaseException as e:
            logger.error(f"数据库错误 - 检查文件变化失败: {file_path} - {e}")
            return True  # 出错时假设文件有变化
        except Exception as e:
            logger.error(f"检查文件变化失败: {file_path} - {e}")
            return True  # 出错时假设文件有变化
    
    def _process_changed_files(self, changed_files: List[Dict[str, str]]):
        """批量处理变化的文件"""
        total_processed = 0
        
        for file_info in changed_files:
            try:
                if self._process_single_image(file_info['path']):
                    total_processed += 1
            except DatabaseException as e:
                logger.error(f"数据库错误 - 处理文件失败: {file_info['path']} - {e}")
            except ImageProcessingException as e:
                logger.error(f"图片处理错误 - 处理文件失败: {file_info['path']} - {e}")
            except Exception as e:
                logger.error(f"处理文件失败: {file_info['path']} - {e}")
        
        if total_processed > 0:
            logger.info(f"成功处理 {total_processed} 个变化的文件")
    
    def force_full_scan(self):
        """强制全量扫描（用于手动触发）"""
        logger.info("开始强制全量扫描...")
        start_time = time.time()
        
        directories = self.db_manager.get_directories()
        total_processed = 0
        
        for directory in directories:
            directory_path = directory['path']
            if not os.path.exists(directory_path):
                continue
                
            files = self._get_directory_files(directory_path)
            for file_path in files:
                if self._process_single_image(file_path):
                    total_processed += 1
        
        scan_duration = time.time() - start_time
        logger.info(f"全量扫描完成，共处理 {total_processed} 个文件，耗时{scan_duration:.2f}秒")
        
        return total_processed
    
    def _process_single_image(self, file_path: str) -> bool:
        """处理单个图片文件，优化版本"""
        try:
            # 快速检查文件是否存在和可读
            if not os.path.exists(file_path):
                return False
                
            # 获取文件信息
            stat = os.stat(file_path)
            
            # 检查文件大小，跳过异常大的文件（可能损坏或不是图片）
            if stat.st_size == 0 or stat.st_size > 100 * 1024 * 1024:  # 100MB限制
                return False
            
            # 获取图片信息 - 使用更轻量的方式
            with Image.open(file_path) as img:
                width, height = img.size
                format_name = img.format
                
                # 验证图片格式
                if format_name not in ['JPEG', 'PNG', 'GIF', 'BMP', 'TIFF', 'WEBP']:
                    return False
            
            # 获取EXIF数据 - 添加错误处理
            try:
                exif_result = ImageProcessor.get_exif_data(file_path)
                exif_data = exif_result.get('exif', {}) if 'error' not in exif_result else None
            except Exception:
                exif_data = None
            
            # 获取现有评分，如果图片已存在则保留原有评分
            existing_image = self.db_manager.get_image_by_path(file_path)
            rating = existing_image.get('rating', 0) if existing_image else 0

            # 生成缩略图 - 只在需要时生成
            should_generate_thumbnail = (
                not existing_image or 
                abs(stat.st_mtime - existing_image.get('modified_at', 0)) > 1
            )
            
            thumbnail = None
            if should_generate_thumbnail:
                thumbnail = ImageProcessor.generate_thumbnail(file_path, (400, 400))
            elif existing_image:
                # 复用现有缩略图
                thumbnail = existing_image.get('thumbnail')
            
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
                'exif_data': exif_data,
                'rating': rating
            }
            
            # 批量操作：更新或插入
            if existing_image:
                self.db_manager.update_image(file_path, image_data)
            else:
                self.db_manager.add_image(**image_data)
                
            return True
            
        except DatabaseException as e:
            logger.error(f"数据库错误 - 跳过文件 {file_path}: {str(e)}")
            return False
        except ImageProcessingException as e:
            logger.warning(f"图片处理错误 - 跳过文件 {file_path}: {str(e)}")
            return False
        except Exception as e:
            logger.debug(f"跳过文件 {file_path}: {str(e)}")
            return False
    
    def get_scan_status(self) -> Dict[str, any]:
        """获取扫描器状态"""
        return {
            'is_running': self.is_running,
            'supported_formats': list(self.supported_formats),
            'cached_checksums': len(self.file_checksums),
            'last_scan_times': self.last_scan_times
        }

# 全局扫描器实例
background_scanner = BackgroundScanner()