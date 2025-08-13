import threading
import webview
from fastapi_server import fastapi_server
from background_scanner import background_scanner
from api import Api

def initialize_background_tasks():
    """初始化后台任务"""
    # 启动FastAPI服务器
    fastapi_server.start()
    # 启动后台图片扫描
    background_scanner.start_scanning()

def main():
    # 创建额外线程执行数据库初始化和后台扫描
    init_thread = threading.Thread(target=initialize_background_tasks, daemon=True)
    init_thread.start()
    # 创建窗口
    window = webview.create_window(
        title='图片管理器',
        # 开发模式: 'http://localhost:5173'
        # 生产模式: '../frontend/dist/index.html'
        url='http://localhost:5173',
        width=1200,
        height=800,
        js_api=Api()
    )
    webview.start(debug=True)
    
    # 停止后台扫描（当窗口关闭时）
    background_scanner.stop_scanning()

if __name__ == "__main__":
    main()
