from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.transaction import TransactionModel
from datetime import datetime

# 定義 Blueprint，用來將路由分組，主入口 app.py 將會註冊此藍圖
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """
    首頁：顯示當月總結餘與收支明細清單。
    - 支援透過 URL 參數 `?month=YYYY-MM` 切換查詢月份。
    - 取得資料後回傳並渲染 `index.html`。
    """
    # 獲取篩選月份，若無則預設為當前月份
    selected_month = request.args.get('month', datetime.now().strftime('%Y-%m'))
    
    # 獲取所有交易，並依據月份篩選交易
    all_transactions = TransactionModel.get_all()
    transactions = [t for t in all_transactions if t['date'].startswith(selected_month)]
    
    # 獲取月度收支統計
    stats = TransactionModel.get_monthly_stats(selected_month)
    total_income = stats.get('total_income', 0)
    total_expense = stats.get('total_expense', 0)
    balance = total_income - total_expense
    
    return render_template(
        'index.html',
        transactions=transactions,
        total_income=total_income,
        total_expense=total_expense,
        balance=balance,
        selected_month=selected_month
    )

@main_bp.route('/transaction/new', methods=['GET'])
def new_transaction():
    """
    新增明細頁：純粹回傳一個空的新增表單。
    - 預設提供當前日期以利填寫。
    - 渲染 `add_record.html`。
    """
    default_date = datetime.now().strftime('%Y-%m-%d')
    # 為了方便與編輯頁面共用或簡化處理，初始化一個空的字典
    transaction = {
        'type': 'expense',
        'amount': '',
        'category': '',
        'date': default_date,
        'description': ''
    }
    return render_template('add_record.html', transaction=transaction)

@main_bp.route('/transaction', methods=['POST'])
def create_transaction():
    """
    新增邏輯：接收並處理來自 `add_record.html` 的 POST 表單送出。
    - 獲取 request.form 資料 (type, amount, category, date, description)
    - 基本驗證 (例如金額需為正數、必填欄位不為空)
    - 成功: 呼叫 Model 寫入庫，並 `redirect` 回首頁。
    - 失敗: 用 `flash` 顯示錯誤，並保留填寫資料重新渲染表單。
    """
    type_ = request.form.get('type')
    amount_str = request.form.get('amount')
    category = request.form.get('category', '').strip()
    date = request.form.get('date', '').strip()
    description = request.form.get('description', '').strip()

    # 回填資料字典，供驗證失敗時重新渲染
    transaction = {
        'type': type_,
        'amount': amount_str,
        'category': category,
        'date': date,
        'description': description
    }

    # 基本欄位驗證
    if not type_ or not amount_str or not category or not date:
        flash("所有必填欄位皆不可為空！", "danger")
        return render_template('add_record.html', transaction=transaction), 400

    if type_ not in ('income', 'expense'):
        flash("收支類型不正確！", "danger")
        return render_template('add_record.html', transaction=transaction), 400

    # 金額驗證
    try:
        amount = float(amount_str)
        if amount <= 0:
            flash("金額必須是大於零的數字！", "danger")
            return render_template('add_record.html', transaction=transaction), 400
    except ValueError:
        flash("請輸入有效的金額數字！", "danger")
        return render_template('add_record.html', transaction=transaction), 400

    # 新增至資料庫
    result = TransactionModel.create(type_, amount, category, date, description)
    if result is None:
        flash("資料庫寫入失敗，請稍後再試！", "danger")
        return render_template('add_record.html', transaction=transaction), 500

    flash("記帳成功！", "success")
    return redirect(url_for('main.index'))

@main_bp.route('/transaction/<int:id>/edit', methods=['GET'])
def edit_transaction(id):
    """
    編輯頁面：依據 ID 取出特定的一筆資料，並將資料填在畫面上。
    - 如果找不到該 ID，應處理 404 (Not Found)。
    - 取得資料後，將它帶給 `edit_record.html` 渲染。
    """
    transaction = TransactionModel.get_by_id(id)
    if not transaction:
        flash("找不到該筆交易紀錄！", "danger")
        return redirect(url_for('main.index'))
    return render_template('edit_record.html', transaction=transaction)

@main_bp.route('/transaction/<int:id>/update', methods=['POST'])
def update_transaction(id):
    """
    更新邏輯：接收來自 `edit_record.html` 的 POST 更新請求。
    - 檢查資料合法性，合法則修改資料庫內相對應 ID 的該筆資料。
    - 修改成功後透過 `redirect` 導回首頁。
    """
    # 確認交易紀錄存在
    existing = TransactionModel.get_by_id(id)
    if not existing:
        flash("欲更新的交易紀錄不存在！", "danger")
        return redirect(url_for('main.index'))

    type_ = request.form.get('type')
    amount_str = request.form.get('amount')
    category = request.form.get('category', '').strip()
    date = request.form.get('date', '').strip()
    description = request.form.get('description', '').strip()

    # 回填資料字典，供驗證失敗時重新渲染
    transaction = {
        'id': id,
        'type': type_,
        'amount': amount_str,
        'category': category,
        'date': date,
        'description': description
    }

    # 基本欄位驗證
    if not type_ or not amount_str or not category or not date:
        flash("所有必填欄位皆不可為空！", "danger")
        return render_template('edit_record.html', transaction=transaction), 400

    if type_ not in ('income', 'expense'):
        flash("收支類型不正確！", "danger")
        return render_template('edit_record.html', transaction=transaction), 400

    # 金額驗證
    try:
        amount = float(amount_str)
        if amount <= 0:
            flash("金額必須是大於零的數字！", "danger")
            return render_template('edit_record.html', transaction=transaction), 400
    except ValueError:
        flash("請輸入有效的金額數字！", "danger")
        return render_template('edit_record.html', transaction=transaction), 400

    # 更新資料庫
    success = TransactionModel.update(id, type_, amount, category, date, description)
    if not success:
        flash("更新失敗，請檢查輸入或資料庫連線！", "danger")
        return render_template('edit_record.html', transaction=transaction), 500

    flash("更新成功！", "success")
    return redirect(url_for('main.index'))

@main_bp.route('/transaction/<int:id>/delete', methods=['POST'])
def delete_transaction(id):
    """
    刪除邏輯：刪除指定 ID 的資料。
    - 為避免網址點擊產生非預期刪除，限定只能用 POST (由前端表單發動)。
    - 刪除完畢後 `redirect` 回首頁。
    """
    success = TransactionModel.delete(id)
    if not success:
        flash("刪除失敗，該交易可能已被刪除！", "danger")
    else:
        flash("刪除成功！", "success")
    return redirect(url_for('main.index'))
