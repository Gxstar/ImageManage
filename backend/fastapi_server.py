import os
import threading
import urllib.parse
import mimetypes
from pathlib import Path
from typing import Dict

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from db.image_manager import ImageManager


def read_file_safely(file_path: str) -> bytes:
    """安全地读取文件内容"""
    try:
        with open(file_path, 'rb') as f:
            return f.read()
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"File not found or cannot be read: {str(e)}")


def get_media_type(file_path: str) -> str:
    """根据文件扩展名获取媒体类型"""
    media_type, _ = mimetypes.guess_type(file_path)
    return media_type or "application/octet-stream"

app = FastAPI(title="Image Manager API", version="1.0.0")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

image_manager = ImageManager()

@app.get("/api/image/{image_id}")
async def get_image(image_id: int):
    """获取原始图片数据"""
    image = image_manager.get_image_by_id(image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    file_path = image.get('file_path')
    if not file_path:
        raise HTTPException(status_code=404, detail="Image file path not found")
    
    image_data = read_file_safely(file_path)
    media_type = get_media_type(file_path)
    
    return Response(content=image_data, media_type=media_type)

@app.get("/api/thumbnail/{image_id}")
async def get_thumbnail(image_id: int):
    """获取图片缩略图"""
    thumbnail_data = image_manager.get_thumbnail_by_id(image_id)
    if not thumbnail_data:
        raise HTTPException(status_code=404, detail="Thumbnail not found")
    
    return Response(content=thumbnail_data, media_type="image/jpeg")

class FastAPIServer:
    def __init__(self, host="127.0.0.1", port=8324):
        self.host = host
        self.port = port
        self.server_thread = None
        self.is_running = False
    
    def start(self):
        """启动FastAPI服务器"""
        if self.is_running:
            return
        
        def run_server():
            uvicorn.run(
                app,
                host=self.host,
                port=self.port,
                log_level="info",
                access_log=False
            )
        
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        self.is_running = True
        print(f"FastAPI server started on http://{self.host}:{self.port}")
    
    def stop(self):
        """停止FastAPI服务器"""
        # 由于uvicorn没有简单的停止方法，这里只是标记状态
        self.is_running = False
        print("FastAPI server stopped")
    
    def get_base_url(self):
        """获取服务器基础URL"""
        return f"http://{self.host}:{self.port}"

# 创建全局服务器实例
fastapi_server = FastAPIServer()

if __name__ == "__main__":
    fastapi_server.start()
    
    # 保持服务器运行
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("服务器已停止")
        fastapi_server.stop()