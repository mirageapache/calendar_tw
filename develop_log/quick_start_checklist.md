# 🚀 快速開始檢查清單

## ✅ 已完成
- [x] Django 專案建立
- [x] Models 定義（CalendarDay, Holiday, WorkdayAdjustment）
- [x] Serializers 建立
- [x] ViewSets 和 API Views
- [x] URL routing 設定
- [x] API 文件（drf-spectacular）
- [x] CORS 設定
- [x] 環境變數支援（python-dotenv）
- [x] 資料匯入指令（import_calendar_data）

## 🎯 接下來要做的事

### 方案 A：使用 CSV 匯入（推薦！適合有政府公開資料）

#### 1️⃣ 執行資料庫遷移（5 分鐘）
```powershell
cd calendarTW

# 執行 migrations 建立資料表
python manage.py migrate

# 建立管理員帳號
python manage.py createsuperuser
```

#### 2️⃣ 匯入 CSV 資料（2 分鐘）
```powershell
# 使用範例資料測試
python manage.py import_csv ..\sample_data\calendar_2026_sample.csv --type calendar --skip-header
python manage.py import_csv ..\sample_data\holidays_2026_sample.csv --type holiday --skip-header

# 或匯入你從政府公開資料平台下載的 CSV
python manage.py import_csv 你的檔案.csv --type calendar --encoding big5 --skip-header
```

#### 3️⃣ 啟動並測試（3 分鐘）
```powershell
python manage.py runserver 8200
# 開啟 http://localhost:8200/api/docs/
```

---

### 方案 B：使用程式碼產生資料（如果沒有 CSV）

#### 1️⃣ 建立 Supabase 專案（10 分鐘）
#### 1️⃣ 建立 Supabase 專案（10 分鐘）
- [ ] 前往 https://supabase.com/ 註冊/登入
- [ ] 建立新專案
- [ ] 設定專案名稱和密碼
- [ ] 選擇區域：Southeast Asia (Singapore)
- [ ] 等待專案建立完成
- [ ] 複製 Database Connection String (URI 格式)

### 2️⃣ 配置本地環境（5 分鐘）
```powershell
# 1. 安裝新套件
pip install -r requirements.txt

# 2. 建立 .env 檔案
Copy-Item .env.example .env

# 3. 編輯 .env，填入 Supabase 連線資訊
# DATABASE_URL=postgres://postgres.xxxxx:你的密碼@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres
```

### 3️⃣ 執行資料庫遷移（5 分鐘）
```powershell
cd calendarTW

# 執行 migrations
python manage.py migrate

# 建立管理員帳號
python manage.py createsuperuser
```

### 4️⃣ 匯入資料（2 分鐘）
```powershell
# 匯入 2026 年資料
python manage.py import_calendar_data --year 2026

# 或匯入多年資料
python manage.py import_calendar_data --start-year 2024 --end-year 2026
```

### 5️⃣ 啟動並測試（3 分鐘）
```powershell
# 啟動伺服器
python manage.py runserver 8200

# 開啟瀏覽器測試：
# - API 文件: http://localhost:8200/api/docs/
# - Admin: http://localhost:8200/admin/
# - API: http://localhost:8200/api/calendar-days/
```

---

## 📊 預期結果

完成後你應該有：
- ✅ Supabase PostgreSQL 資料庫
- ✅ 完整的日曆資料（365 筆/年）
- ✅ 台灣假日資料
- ✅ 可運作的 REST API
- ✅ API 文件介面

---

## 🆘 需要幫助？

參考詳細文件：[database_setup.md](./database_setup.md)

常用指令：
```powershell
# 查看資料庫狀態
python manage.py showmigrations

# 查看資料筆數
python manage.py shell
>>> from calendar_api.models import CalendarDay, Holiday
>>> print(f"日曆: {CalendarDay.objects.count()} 筆")
>>> print(f"假日: {Holiday.objects.count()} 筆")

# 清空資料重新匯入
>>> CalendarDay.objects.all().delete()
>>> Holiday.objects.all().delete()
>>> exit()
python manage.py import_calendar_data --year 2026
```

---

## 📝 筆記

目前狀態：
- Database: 待設定 Supabase
- Data: 準備匯入
- API: 已開發完成

下一個里程碑：
- [ ] 完成資料庫設定
- [ ] 匯入初始資料
- [ ] 測試 API 端點
- [ ] 準備前端開發 或 準備部署
