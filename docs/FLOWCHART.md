# 系統與使用者流程圖 (Flowchart) - 個人記帳簿

本文件延續 PRD 的功能需求與架構設計，將使用者的操作動線，以及系統內部的資料與狀態流動加以視覺化。

## 1. 使用者流程圖 (User Flow)

這張流程圖描述了當使用者進入「個人記帳簿」系統後，所能執行的各種主要操作路徑，涵蓋了明細的 CRUD (新增、讀取、修改、刪除) 與月度統計的切換。

```mermaid
flowchart LR
    A([使用者進入網站]) --> B[首頁 - 總覽儀表板]
    
    B -->|自動載入| B1[顯示總餘額、本月支出收入]
    B -->|統計| B2[顯示依類別加總之清單]
    
    B --> C{要執行什麼操作？}
    
    C -->|點擊「新增明細」| D[進入新增表單頁面]
    D --> E{填寫收支類別與金額}
    E -->|格式錯誤或未填| D
    E -->|成功送出表單| F[系統儲存資料]
    F -->|自動跳轉| B
    
    C -->|切換月份| G[載入特定月份歷史數據]
    G --> B
    
    C -->|點擊清單中的某一筆| H[進入編輯/刪除頁面]
    H --> I{要執行什麼操作？}
    I -->|修改內容並送出| F
    I -->|點擊刪除按鈕| J[系統執行刪除作業]
    J -->|自動跳轉| B
```

## 2. 系統序列圖 (Sequence Diagram)

以下以「使用者填寫並送出新增一筆收支紀錄」的情境為例，說明資料在前端瀏覽器與後端元件之間如何流動與互動。

```mermaid
sequenceDiagram
    autonumber
    actor User as 使用者
    participant Browser as 瀏覽器 (前端)
    participant Flask as Flask Route (Controller)
    participant Model as Database Model
    participant DB as SQLite

    User->>Browser: 點擊「新增」按鈕
    Browser->>Flask: HTTP GET /transaction/add
    Flask-->>Browser: 回傳新增表單 HTML 頁面
    User->>Browser: 填寫金額、類別、說明與日期並按下送出
    Browser->>Flask: HTTP POST /transaction/add (包含表單資料)
    
    Flask->>Flask: 驗證欄位是否齊全、金額不得為負數等
    
    alt 驗證失敗
        Flask-->>Browser: 返回原表單並顯示錯誤提示訊息 (HTML 返回)
    else 驗證成功
        Flask->>Model: 呼叫 add_transaction(data)
        Model->>DB: 執行 INSERT INTO transactions ...
        DB-->>Model: 寫入完成
        Model-->>Flask: 回傳執行成功
        Flask-->>Browser: 重新導向至首頁 (302 Redirect to /)
        Browser->>Flask: HTTP GET /
        Flask-->>Browser: 重新渲染帶有最新紀錄的首頁
    end
```

## 3. 功能清單對照表

根據 PRD 需求，以下整理出每個核心操作對應的網址路徑 (URL) 與 HTTP 傳遞方法。這可作為後續開始撰寫 Flask Route 與開發的一覽表。

| 功能名稱 | URL 路徑 | HTTP 方法 | 用途說明 |
| --- | --- | --- | --- |
| 首頁 (當月總覽) | `/` | GET | 渲染系統首頁，包含當下月份的結餘、統計與明細列 |
| 讀取新增表單 | `/transaction/add` | GET | 返回讓使用者填寫的新增明細表單頁面 |
| 送出新增資料 | `/transaction/add` | POST | 接收並驗證送來的新增資料，若成功則存入庫並跳回首頁 |
| 讀取編輯表單 | `/transaction/edit/<id>` | GET | 根據明細 ID 讀取該筆舊有資料，預填於表單畫面上 |
| 送出編輯資料 | `/transaction/edit/<id>` | POST | 更新特定的明細資料並存入資料庫 |
| 執行刪除作業 | `/transaction/delete/<id>` | POST | 刪除特定 ID 的收支資料。為了安全，建議不開放 GET 刪除 |
| 月份或時間切換 | `/stats/<year_month>` | GET | 將網址換成特定月份（例：`/stats/2026-04`），回傳該月的介面 |
