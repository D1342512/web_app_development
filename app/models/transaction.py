import sqlite3
import os

# 設定 SQLite DB 的絕對路徑至 /instance/database.db
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'instance', 'database.db')

def get_db_connection():
    """取得資料庫連線，並設定 row_factory"""
    # 確保 instance 目錄存在
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # 允許透過欄位名稱像 dict 一樣讀取 row
    return conn

class TransactionModel:
    @classmethod
    def create_table(cls):
        """讀取 database/schema.sql 並建立資料表"""
        conn = get_db_connection()
        try:
            schema_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'database', 'schema.sql')
            if os.path.exists(schema_path):
                with open(schema_path, 'r', encoding='utf-8') as f:
                    conn.executescript(f.read())
            else:
                # 備用保底建表語法
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS transactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
                        amount REAL NOT NULL,
                        category TEXT NOT NULL,
                        date TEXT NOT NULL,
                        description TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    );
                ''')
            conn.commit()
        finally:
            conn.close()

    @classmethod
    def create(cls, type_, amount, category, date, description=""):
        """新增一筆明細"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO transactions (type, amount, category, date, description)
                VALUES (?, ?, ?, ?, ?)
            ''', (type_, amount, category, date, description))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    @classmethod
    def get_all(cls, order='DESC'):
        """取得所有的收支紀錄 (預設依日期降冪排序)"""
        conn = get_db_connection()
        try:
            sort_order = 'DESC' if order.upper() == 'DESC' else 'ASC'
            cursor = conn.execute(f"SELECT * FROM transactions ORDER BY date {sort_order}, id {sort_order}")
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    @classmethod
    def get_by_id(cls, transaction_id):
        """依據 ID 取得單筆明細"""
        conn = get_db_connection()
        try:
            cursor = conn.execute("SELECT * FROM transactions WHERE id = ?", (transaction_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    @classmethod
    def update(cls, transaction_id, type_, amount, category, date, description=""):
        """更新明細內容"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE transactions
                SET type = ?, amount = ?, category = ?, date = ?, description = ?
                WHERE id = ?
            ''', (type_, amount, category, date, description, transaction_id))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    @classmethod
    def delete(cls, transaction_id):
        """刪除明細"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    @classmethod
    def get_monthly_stats(cls, year_month):
        """取得輸入月份的收支統計 (year_month 格式: 'YYYY-MM')"""
        conn = get_db_connection()
        try:
            cursor = conn.execute('''
                SELECT 
                    SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) as total_income,
                    SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) as total_expense
                FROM transactions
                WHERE date LIKE ?
            ''', (f"{year_month}%",))
            row = cursor.fetchone()
            return dict(row) if row else {'total_income': 0, 'total_expense': 0}
        finally:
            conn.close()
