import os
from flask import Flask

def create_app():
    """建立並設定 Flask 應用程式實例 (Application Factory)"""
    app = Flask(__name__, instance_relative_config=True)
    
    # 預設設定
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev_key_for_testing'),
        DATABASE=os.path.join(app.instance_path, 'database.db'),
    )
    
    # 確保 instance 資料夾存在，用於存放 SQLite 資料庫
    os.makedirs(app.instance_path, exist_ok=True)
    
    # 註冊路由藍圖 (Blueprints)
    from app.routes.main_routes import main_bp
    app.register_blueprint(main_bp)
    
    return app

def init_db():
    """初始化資料庫表結構"""
    from app.models.transaction import TransactionModel
    TransactionModel.create_table()
    print("Database table 'transactions' initialized successfully.")
