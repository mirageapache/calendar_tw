# 資料庫設定與部署指南

## 📋 目錄
1. [Supabase 設定](#1-supabase-設定)
2. [本地開發環境配置](#2-本地開發環境配置)
3. [執行資料庫遷移](#3-執行資料庫遷移)
4. [匯入初始資料](#4-匯入初始資料)
5. [驗證設定](#5-驗證設定)

---

## 1. Supabase 設定

### 1.1 建立 Supabase 專案
1. 前往 [Supabase](https://supabase.com/) 並登入
2. 點擊 "New Project"
3. 填寫專案資訊：
   - **Name**: calendar-tw (或你喜歡的名稱)
   - **Database Password**: 設定一個強密碼（請記住！）
   - **Region**: Southeast Asia (Singapore) - 選擇最近的區域
   - **Pricing Plan**: Free (開發測試用)

4. 等待專案建立完成（約 2-3 分鐘）

### 1.2 取得連線資訊
1. 進入專案後，點擊左側選單的 **"Database"**
2. 點擊上方的 **"Connection string"** 頁籤
3. 選擇 **"URI"** 格式
4. 複製連線字串，格式如下：
   ```
   postgres://postgres.xxxxxxxxxxxxx:[YOUR-PASSWORD]@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres
   ```
5. 將 `[YOUR-PASSWORD]` 替換成你設定的密碼

---

## 2. 本地開發環境配置

### 2.1 安裝相依套件
```powershell
# 進入專案目錄
cd c:\Users\user\Documents\my_repo\calendar_tw

# 安裝 Python 套件（包含新增的 python-dotenv）
pip install -r requirements.txt
```

### 2.2 建立環境變數檔案
1. 複製範例檔案：
```powershell
Copy-Item .env.example .env
```

2. 編輯 `.env` 檔案，填入以下資訊：
```env
# Django 設定
SECRET_KEY=your-secret-key-here-change-this-in-production
DEBUG=True

# 資料庫設定 (Supabase PostgreSQL)
# 將下面的連線字串替換成你從 Supabase 取得的連線字串
DATABASE_URL=postgres://postgres.xxxxxxxxxxxxx:your-password@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres

# CORS 設定（允許前端存取）
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8200
```

### 2.3 產生新的 SECRET_KEY（建議）
```powershell
# 執行 Python 指令產生新的 SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
將產生的字串複製到 `.env` 檔案的 `SECRET_KEY=` 後面

---

## 3. 執行資料庫遷移

### 3.1 檢查 migrations
```powershell
# 進入 Django 專案目錄
cd calendarTW

# 檢查現有的 migrations
python manage.py showmigrations
```

### 3.2 建立 migrations（如果需要）
```powershell
# 如果有模型變更，建立新的 migration
python manage.py makemigrations

# 查看將要執行的 SQL
python manage.py sqlmigrate calendar_api 0001
```

### 3.3 執行 migrations 到 Supabase
```powershell
# 執行資料庫遷移
python manage.py migrate

# 看到類似以下訊息表示成功：
# Operations to perform:
#   Apply all migrations: admin, auth, calendar_api, contenttypes, sessions
# Running migrations:
#   Applying contenttypes.0001_initial... OK
#   Applying auth.0001_initial... OK
#   Applying admin.0001_initial... OK
#   ...
#   Applying calendar_api.0001_initial... OK
```

### 3.4 建立超級使用者
```powershell
# 建立 Django admin 管理員帳號
python manage.py createsuperuser

# 按照提示輸入：
# - Username: admin
# - Email: your-email@example.com
# - Password: (輸入密碼，不會顯示)
# - Password (again): (再次輸入確認)
```

---

## 4. 匯入初始資料

### 4.1 匯入 2026 年資料
```powershell
# 匯入單一年份資料
python manage.py import_calendar_data --year 2026
```

### 4.2 匯入多年資料
```powershell
# 匯入 2024-2026 年資料
python manage.py import_calendar_data --start-year 2024 --end-year 2026
```

### 4.3 查看匯入結果
執行成功後會看到類似訊息：
```
開始匯入 2026 年資料...
  📅 日曆日期: 新增 365 筆, 更新 0 筆
  🎉 假日資料: 新增 11 筆, 更新 0 筆
✅ 2026 年資料匯入完成！
```

---

## 5. 驗證設定

### 5.1 啟動開發伺服器
```powershell
# 啟動 Django 開發伺服器
python manage.py runserver 8200
```

### 5.2 測試 API
開啟瀏覽器或使用工具測試以下端點：

1. **API 文件**
   - Swagger UI: http://localhost:8200/api/docs/
   - ReDoc: http://localhost:8200/api/redoc/

2. **查詢日曆資料**
   ```
   GET http://localhost:8200/api/calendar-days/
   GET http://localhost:8200/api/calendar-days/by-date/2026-01-01/
   ```

3. **查詢假日資料**
   ```
   GET http://localhost:8200/api/holidays/
   GET http://localhost:8200/api/holidays/by-year/2026/
   ```

4. **Django Admin**
   - http://localhost:8200/admin/
   - 使用前面建立的超級使用者帳號登入

### 5.3 驗證資料庫連線
```powershell
# 進入 Django shell
python manage.py shell

# 執行以下 Python 指令
>>> from calendar_api.models import CalendarDay, Holiday
>>> CalendarDay.objects.count()  # 應該顯示匯入的日期筆數
>>> Holiday.objects.count()  # 應該顯示匯入的假日筆數
>>> exit()
```

---

## 🐳 使用 Docker（選擇性）

如果你想使用 Docker 部署：

### 更新 docker-compose.yml
在 `environment` 區段加入 DATABASE_URL：
```yaml
environment:
  - PYTHONUNBUFFERED=1
  - DEBUG=True
  - DATABASE_URL=postgres://postgres.xxxxx:password@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres
```

### 啟動 Docker
```powershell
# 建立並啟動容器
docker-compose up --build

# 在容器中執行 migrations
docker-compose exec web python manage.py migrate

# 在容器中建立超級使用者
docker-compose exec web python manage.py createsuperuser

# 在容器中匯入資料
docker-compose exec web python manage.py import_calendar_data --year 2026
```

---

## ⚠️ 注意事項

1. **安全性**
   - 絕對不要將 `.env` 檔案提交到 Git
   - 在正式環境中設定強密碼
   - 正式環境要將 `DEBUG=False`

2. **Supabase 限制**
   - Free plan 有連線數限制
   - 注意資料庫大小限制

3. **假日資料**
   - 目前 `import_calendar_data.py` 只有 2026 年的假日資料
   - 需要手動更新其他年份的假日資料
   - 建議參考政府行政院人事行政總處公告

4. **時區設定**
   - 目前 `settings.py` 的 `TIME_ZONE = "UTC"`
   - 如需要，可改為 `TIME_ZONE = "Asia/Taipei"`

---

## 🔧 常見問題

### Q1: 連線 Supabase 失敗？
- 檢查 DATABASE_URL 格式是否正確
- 確認密碼沒有特殊字元問題（需要 URL encode）
- 檢查網路連線
- 確認 Supabase 專案狀態正常

### Q2: Migration 失敗？
- 先執行 `python manage.py showmigrations` 查看狀態
- 如果有衝突，可能需要手動調整 migrations
- 確保資料庫連線正常

### Q3: 如何重新匯入資料？
```powershell
# 刪除現有資料（小心使用！）
python manage.py shell
>>> from calendar_api.models import CalendarDay, Holiday, WorkdayAdjustment
>>> CalendarDay.objects.all().delete()
>>> Holiday.objects.all().delete()
>>> WorkdayAdjustment.objects.all().delete()
>>> exit()

# 重新匯入
python manage.py import_calendar_data --year 2026
```

---

## 📚 下一步

完成資料庫設定後，你可以：
1. ✅ 開發前端介面連接 API
2. ✅ 調整 API 功能和欄位
3. ✅ 新增更多年份的假日資料
4. ✅ 部署到正式環境（Render, Heroku, AWS 等）
5. ✅ 設定 CI/CD 自動化部署
