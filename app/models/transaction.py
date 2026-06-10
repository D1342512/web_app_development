import sqlite3
import os
import sys

# 設定 SQLite DB 的絕對路徑至 /instance/database.db
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'instance', 'database.db')

def get_db_connection():
    """取得資料庫連線，並設定 row_factory。
    
    Returns:
        sqlite3.Connection: 資料庫連線實例。
    """
    try:
        # 確保 instance 目錄存在
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # 允許透過欄位名稱像 dict 一樣讀取 row
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}", file=sys.stderr)
        raise e

class TransactionModel:
    @classmethod
    def create_table(cls):
        """讀取 database/schema.sql 並建立資料表。
        
        Raises:
            sqlite3.Error: 當 SQL 語法執行失敗時拋出。
        """
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
            print("Table 'transactions' checked/created successfully.")
        except sqlite3.Error as e:
            print(f"Error creating table: {e}", file=sys.stderr)
            conn.rollback()
            raise e
        finally:
            conn.close()

    @classmethod
    def create(cls, type_, amount, category, date, description=""):
        """新增一筆收支明細。
        
        Args:
            type_ (str): 收支類型，需為 'income' 或 'expense'。
            amount (float): 收支金額，需為正數。
            category (str): 款項分類。
            date (str): 交易發生日期，格式為 YYYY-MM-DD。
            description (str, optional): 交易備註。預設為 ""。
            
        Returns:
            int: 成功時回傳新插入紀錄的 id (lastrowid)，失敗時回傳 None。
        """
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO transactions (type, amount, category, date, description)
                VALUES (?, ?, ?, ?, ?)
            ''', (type_, amount, category, date, description))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error creating transaction: {e}", file=sys.stderr)
            conn.rollback()
            return None
        finally:
            conn.close()

    @classmethod
    def get_all(cls, order='DESC'):
        """取得所有的收支紀錄。
        
        Args:
            order (str, optional): 排序方向。'DESC' 為依日期降冪，'ASC' 為升冪。預設為 'DESC'。
            
        Returns:
            list: 包含每筆明細字典 (dict) 的清單，失敗時回傳空清單 []。
        """
        conn = get_db_connection()
        try:
            sort_order = 'DESC' if order.upper() == 'DESC' else 'ASC'
            cursor = conn.execute(f"SELECT * FROM transactions ORDER BY date {sort_order}, id {sort_order}")
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Error getting all transactions: {e}", file=sys.stderr)
            return []
        finally:
            conn.close()

    @classmethod
    def get_by_id(cls, transaction_id):
        """依據 ID 取得單筆明細。
        
        Args:
            transaction_id (int): 收支明細的 ID。
            
        Returns:
            dict: 包含該筆明細欄位的字典，若無此 ID 或失敗則回傳 None。
        """
        conn = get_db_connection()
        try:
            cursor = conn.execute("SELECT * FROM transactions WHERE id = ?", (transaction_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            print(f"Error getting transaction by ID {transaction_id}: {e}", file=sys.stderr)
            return None
        finally:
            conn.close()

    @classmethod
    def update(cls, transaction_id, type_, amount, category, date, description=""):
        """更新明細內容。
        
        Args:
            transaction_id (int): 欲更新的收支明細 ID。
            type_ (str): 收支類型，需為 'income' 或 'expense'。
            amount (float): 收支金額，需為正數。
            category (str): 款項分類。
            date (str): 交易發生日期，格式為 YYYY-MM-DD。
            description (str, optional): 交易備註。預設為 ""。
            
        Returns:
            bool: 更新成功回傳 True，無更新、找不到 ID 或失敗時回傳 False。
        """
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
        except sqlite3.Error as e:
            print(f"Error updating transaction ID {transaction_id}: {e}", file=sys.stderr)
            conn.rollback()
            return False
        finally:
            conn.close()

    @classmethod
    def delete(cls, transaction_id):
        """刪除明細。
        
        Args:
            transaction_id (int): 欲刪除的收支明細 ID。
            
        Returns:
            bool: 刪除成功回傳 True，找不到 ID 或失敗時回傳 False。
        """
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error deleting transaction ID {transaction_id}: {e}", file=sys.stderr)
            conn.rollback()
            return False
        finally:
            conn.close()

    @classmethod
    def get_monthly_stats(cls, year_month):
        """取得輸入月份的收支總計。
        
        Args:
            year_month (str): 查詢的年月，格式為 'YYYY-MM'。
            
        Returns:
            dict: 包含 'total_income' 與 'total_expense' 的字典。若失敗或無資料則回傳預設值 0。
        """
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
            total_income = row['total_income'] if row and row['total_income'] is not None else 0
            total_expense = row['total_expense'] if row and row['total_expense'] is not None else 0
            return {'total_income': total_income, 'total_expense': total_expense}
        except sqlite3.Error as e:
            print(f"Error getting monthly stats for {year_month}: {e}", file=sys.stderr)
            return {'total_income': 0, 'total_expense': 0}
        finally:
            conn.close()
