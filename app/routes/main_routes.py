from flask import Blueprint, render_template, request, redirect, url_for, flash
# 預先保留 Model 的引用 (未來實作時解開註解)
# from app.models.transaction import TransactionModel
# from datetime import datetime

# 定義 Blueprint，用來將路由分組，主入口 app.py 將會註冊此藍圖
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """
    首頁：顯示當月總結餘與收支明細清單。
    - 支援透過 URL 參數 `?month=YYYY-MM` 切換查詢月份。
    - 取得資料後回傳並渲染 `index.html`。
    """
    pass

@main_bp.route('/transaction/new', methods=['GET'])
def new_transaction():
    """
    新增明細頁：純粹回傳一個空的新增表單。
    - 渲染 `add_record.html`。
    """
    pass

@main_bp.route('/transaction', methods=['POST'])
def create_transaction():
    """
    新增邏輯：接收並處理來自 `add_record.html` 的 POST 表單送出。
    - 獲取 request.form 資料 (type, amount, category, date, description)
    - 基本驗證 (例如金額需為正數、必填欄位不為空)
    - 成功: 呼叫 Model 寫入庫，並 `redirect` 回首頁。
    - 失敗: 用 `flash` 顯示錯誤，並保留填寫資料重新渲染表單。
    """
    pass

@main_bp.route('/transaction/<int:id>/edit', methods=['GET'])
def edit_transaction(id):
    """
    編輯頁面：依據 ID 取出特定的一筆資料，並將資料填在畫面上。
    - 如果找不到該 ID，應處理 404 (Not Found)。
    - 取得資料後，將它帶給 `edit_record.html` 渲染。
    """
    pass

@main_bp.route('/transaction/<int:id>/update', methods=['POST'])
def update_transaction(id):
    """
    更新邏輯：接收來自 `edit_record.html` 的 POST 更新請求。
    - 檢查資料合法性，合法則修改資料庫內相對應 ID 的該筆資料。
    - 修改成功後透過 `redirect` 導回首頁。
    """
    pass

@main_bp.route('/transaction/<int:id>/delete', methods=['POST'])
def delete_transaction(id):
    """
    刪除邏輯：刪除指定 ID 的資料。
    - 為避免網址點擊產生非預期刪除，限定只能用 POST (由前端表單發動)。
    - 刪除完畢後 `redirect` 回首頁。
    """
    pass
