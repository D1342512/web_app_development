import os
from dotenv import load_dotenv
from app import create_app

# 優先載入根目錄下的 .env 環境變數設定
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    load_dotenv()

# 呼叫應用程式工廠建立 Flask app 實例
app = create_app()

if __name__ == '__main__':
    # 根據環境變數決定是否開啟偵錯模式 (預設開啟以利開發)
    debug_mode = os.environ.get('FLASK_DEBUG', '1') == '1'
    app.run(host='127.0.0.1', port=5000, debug=debug_mode)
