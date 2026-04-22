# 路由與頁面設計 (ROUTES) - 個人記帳簿

本文件盤點系統中所需的 Flask 路由 (Routes) 陣列，包含對應的 URL 路徑、HTTP 傳遞方法以及 Jinja2 模板，做為前後端實作或團隊分工的參考。

## 1. 路由總覽表格

| 功能 | HTTP 方法 | URL 路徑 | 對應模板 | 說明 |
| --- | --- | --- | --- | --- |
| 首頁與清單 | GET | `/` | `index.html` | 呈現當月收支統計與明細清單。可透過參數 `?month=YYYY-MM` 切換。 |
| 新增表單頁面 | GET | `/transaction/new` | `add_record.html` | 呈現一個讓使用者輸入新資料的空白表單。 |
| 建立新明細 | POST | `/transaction` | — | 接收並驗證表單資料，寫入資料庫後 Redirect 導向首頁。 |
| 編輯表單頁面 | GET | `/transaction/<id>/edit`| `edit_record.html`| 讀取特定 id 的原明細，填入表單供修改。 |
| 更新明細內容 | POST | `/transaction/<id>/update`| — | 接收表單更新請求，核對後存入資料庫再 Redirect 導向首頁。 |
| 刪除單筆紀錄 | POST | `/transaction/<id>/delete`| — | 確實刪除該紀錄，完成後 Redirect 導向首頁。 |

> 備註：在一般較嚴謹的 RESTful API 中，更新通常用 PUT，刪除為 DELETE；但由於我們是純 Server-side 渲染的 HTML Form 架構，原生 HTML `<form>` 只支援 GET 與 POST，因此刪除與更新動作均透過 POST 路由實作。

## 2. 每個路由的詳細邏輯說明

### 首頁 (`/`)
- **輸入**：URL 參數 `month`，用以過濾特定月份（格式: 2026-04），若沒給則以 `datetime.now()` 當下月份為預設。
- **處理邏輯**：
  1. 呼叫 `TransactionModel.get_all()` (我們可在 Model 層內實作進階的方法 `get_by_month()` 以過濾資料) 
  2. 呼叫 `TransactionModel.get_monthly_stats(month)` 取出總結餘與收支加總。
- **輸出**：將資料包裹為變數傳給 `index.html`。

### 新增與建立 (`/transaction/new` 與 `/transaction` POST)
- **錯誤處理原則**：
  如果使用者送出的金錢為負數或是標題空白，我們在 POST 路由內不應讓系統崩潰。我們應該儲存錯誤訊息（利用 Flask 的 `flash()` 功能）並中斷寫入行為，然後呼叫 `render_template` 將其帶回填寫頁面，並透過預填保留原本輸入到一半的正確資料。
- **成功處置**：順暢地寫入 SQLite 後，回報成功並 `redirect(url_for('main.index'))`。

### 編輯與更新 (`/transaction/<id>/edit` 與 `/transaction/<id>/update`)
- **異常邏輯**：如果使用者輸入或是嘗試點擊一個已經刪除或不存在的 ID（例如：`/transaction/999/edit`），路由必須立刻捕捉並回傳 `404 Not Found` 或是導回首頁並跳出警告，不可往後繼續執行，以免引發伺服器錯誤 (500 Error)。

## 3. Jinja2 模板 (Templates) 清單設計

在 `app/templates/` 裡我們規劃以下網頁結構檔案，其中將運用到區塊繼承（Template Inheritance）。

| 檔案名稱 | 繼承自 | 職責 |
| --- | --- | --- |
| **`base.html`** | (為底層) | 所有網頁的主版型骨架。包含 `<head>` 區塊 (CSS, JS 引入)、上方的導航列 (Navbar、標題) 等等。包含 `{% block content %}{% endblock %}` 來容納子頁面。 |
| **`index.html`** | `base.html` | 首頁呈現。分為上方儀表板（綠色結餘、紅色支出），以及下方使用 `<table>` 或卡片結構列出的收支明細表。 |
| **`add_record.html`** | `base.html` | 新增用的表格畫面。包含輸入數字、下拉選單 (收/支類型、分類)、日期選擇器與備註。 |
| **`edit_record.html`** | `base.html` | 高度同上，但輸入框預設必須填入原有的 `value="..."` 屬性。 |

## 4. 路由骨架程式碼
完成的骨架已經位於 `app/routes/main_routes.py`。
此處先建立好 Python 的 `@app.route` 函式裝飾與 Docstring 定義，為我們下一步實作與測試奠定了分工基礎。
