# 📊 目前系統運作狀態說明

## 🗄️ 資料庫位置與狀態

### **目前使用的資料庫：SQLite（本地檔案）**

**檔案位置：**
```
c:\Users\user\Documents\my_repo\calendar_tw\calendarTW\db.sqlite3
```

**檔案資訊：**
- 📁 檔案名稱：`db.sqlite3`
- 📊 檔案大小：204,800 bytes (約 200KB)
- 📅 最後修改：2026/1/28 下午 03:04
- 📋 資料筆數：121 筆日曆資料 + 16 筆假日資料

---

## 🔄 系統運作流程

### **1. 開發環境設定**
```
你的電腦 (Windows)
├── Python 虛擬環境 (.venv)
├── Django 專案 (calendarTW/)
│   ├── 程式碼 (models.py, views.py, serializers.py)
│   ├── 設定 (settings.py)
│   └── 資料庫檔案 (db.sqlite3) ← 你的資料存在這裡
└── 環境變數 (.env)
```

### **2. 資料庫連線設定**
```python
# settings.py 中的設定
DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",  # ← 預設使用 SQLite
        conn_max_age=600,
        conn_health_checks=True,
    )
}
```

### **3. 環境變數控制**
```env
# .env 檔案 (目前 DATABASE_URL 被註解)
# DATABASE_URL=postgresql://...  # ← 註解中 = 使用 SQLite
DATABASE_URL=postgresql://...     # ← 取消註解 = 使用 Supabase
```

---

## 📈 資料流程圖

```
政府 CSV 檔案
    ↓ (import_gov_calendar 指令)
Django 管理指令
    ↓ (處理資料格式轉換)
Python 程式碼
    ↓ (建立模型實例)
Django ORM
    ↓ (SQL 語句)
SQLite 資料庫檔案 (db.sqlite3)
    ↓ (儲存資料)
你的硬碟
```

---

## 🎯 目前狀態總結

### ✅ **已完成的階段**
1. **資料庫建立**：SQLite 資料庫已建立並包含資料表結構
2. **資料匯入**：2026年政府假日資料已成功匯入
3. **API 服務**：Django REST API 已啟動並可查詢資料
4. **前端介面**：Swagger UI 可測試 API

### 🔄 **目前的運作模式**
- **資料庫**：本地 SQLite 檔案
- **伺服器**：Django 開發伺服器 (http://localhost:8200)
- **資料來源**：政府公開資料 CSV 檔案
- **API 狀態**：正常運作中

### 🔜 **下一個階段：切換到 Supabase**
當網路正常時，可以：
1. 取消註解 `.env` 中的 `DATABASE_URL`
2. 執行 `python manage.py migrate` 建立 Supabase 資料表
3. 重新匯入資料到 Supabase
4. 資料會從本地 SQLite 移轉到雲端 PostgreSQL

---

## 📋 快速檢查指令

### 檢查資料庫狀態
```powershell
cd calendarTW
python manage.py shell
```
```python
from calendar_api.models import CalendarDay, Holiday
print(f"日曆資料: {CalendarDay.objects.count()} 筆")
print(f"假日資料: {Holiday.objects.count()} 筆")
```

### 檢查資料庫檔案
```powershell
# 檔案位置
Get-Item calendarTW/db.sqlite3

# 檔案大小
(Get-Item calendarTW/db.sqlite3).Length
```

### 測試 API
```
GET http://localhost:8200/api/calendar-days/?year=2026
GET http://localhost:8200/api/holidays/
GET http://localhost:8200/api/docs/
```

---

## 💡 重要提醒

### **SQLite vs PostgreSQL**
- **SQLite**：本地檔案，適合開發測試，檔案小，無需網路
- **PostgreSQL (Supabase)**：雲端資料庫，適合生產環境，多人共用

### **資料安全**
- SQLite 檔案 (`db.sqlite3`) 包含所有資料
- 不要刪除這個檔案，除非要重新開始
- 檔案會自動備份在 `.gitignore` 中（不會提交到 Git）

### **切換資料庫**
目前使用 SQLite 是因為：
1. 網路連線問題（無法連到 Supabase）
2. 方便本地開發測試
3. 不需要額外設定

當要部署到生產環境時，再切換到 Supabase。

---

## 🚀 接下來你可以做的事

1. **繼續開發**：API 已經可以正常使用
2. **測試功能**：使用 Swagger UI 測試各種 API
3. **匯入更多資料**：匯入 2017-2025 年的資料
4. **開發前端**：連接 API 建立使用者介面
5. **切換到 Supabase**：當網路正常時切換到雲端資料庫

你的資料現在安全地儲存在本地 SQLite 檔案中，API 服務正常運作中！🎉