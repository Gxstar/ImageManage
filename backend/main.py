import webview
from api import Api

def main():
    window=webview.create_window(
        title='测试窗口',
        url='http://localhost:5173',
        width=1200,
        height=800,
        js_api=Api()
        )
    webview.start(debug=True)

if __name__ == "__main__":
    main()
