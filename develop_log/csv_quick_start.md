# 🚀 CSV 匯入快速指南

你已經完成了 Supabase 設定！現在可以直接匯入 CSV 資料了。

## ✅ 你已經完成
- [x] 建立 Supabase 專案
- [x] 設定本地 .env 連線字串
- [x] 安裝必要套件

## 📝 接下來 3 個步驟（約 5 分鐘）

### 步驟 1：建立資料表（首次使用）

```powershell
# 進入 Django 專案目錄
cd calendarTW

# 執行資料庫遷移（在 Supabase 建立資料表）
python manage.py migrate

# 建立管理員帳號
python manage.py createsuperuser
# 輸入帳號、Email、密碼
```

**預期結果：**
```
Operations to perform:
  Apply all migrations: admin, auth, calendar_api, contenttypes, sessions
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  ...
  Applying calendar_api.0001_initial... OK
✓ 成功！Supabase 中的資料表已建立
```

---

### 步驟 2：匯入 CSV 資料

#### 選項 A：使用範例資料測試

```powershell
# 匯入範例日曆資料（16 筆）
python manage.py import_csv ..\sample_data\calendar_2026_sample.csv --type calendar --skip-header

# 匯入範例假日資料（11 筆）
python manage.py import_csv ..\sample_data\holidays_2026_sample.csv --type holiday --skip-header
```

#### 選項 B：匯入你的 CSV 檔案

```powershell
# 如果你從政府公開資料平台下載了 CSV
# 例如：「中華民國 115 年政府行政機關辦公日曆表.csv」

# 匯入（政府資料通常是 Big5 編碼）
python manage.py import_csv 你的檔案路徑.csv --type calendar --encoding big5 --skip-header

# 如果不確定編碼，程式會自動嘗試多種編碼
python manage.py import_csv 你的檔案.csv --type calendar --skip-header
```

**預期結果：**
```
開始匯入 CSV 檔案: ..\sample_data\calendar_2026_sample.csv
資料類型: calendar
檔案編碼: utf-8-sig

✓ 成功讀取檔案 (使用編碼: utf-8-sig)
總共 17 行資料

開始匯入日曆資料...
  處理進度: 16 筆...

✅ 日曆資料匯入完成！
  新增: 16 筆
  更新: 0 筆
```

---

### 步驟 3：啟動伺服器並測試

```powershell
# 啟動開發伺服器
python manage.py runserver 8200
```

**測試 API：**
1. **API 文件**: http://localhost:8200/api/docs/
2. **查詢所有日期**: http://localhost:8200/api/calendar-days/
3. **查詢假日**: http://localhost:8200/api/calendar-days/?is_holiday=true
4. **Django Admin**: http://localhost:8200/admin/

---

## 🎯 CSV 格式說明

### 日曆資料格式（最簡單）
```csv
日期,是否假日,假日名稱
2026-01-01,true,中華民國開國紀念日
2026-01-02,false,
2026-01-03,false,
```

### 假日資料格式
```csv
日期,假日名稱
2026-01-01,中華民國開國紀念日
2026-02-28,和平紀念日
2026-10-10,國慶日
```

詳細說明請參考：[csv_import_guide.md](./csv_import_guide.md)

---

## 🔍 驗證資料

### 方法 1：API 查詢
```
GET http://localhost:8200/api/calendar-days/
GET http://localhost:8200/api/holidays/
```

### 方法 2：Django Shell
```powershell
python manage.py shell
```
```python
from calendar_api.models import CalendarDay, Holiday

# 查看匯入的筆數
print(f"日曆: {CalendarDay.objects.count()} 筆")
print(f"假日: {Holiday.objects.count()} 筆")

# 查看 2026 年假日
for h in Holiday.objects.filter(year=2026):
    print(f"{h.date} - {h.name}")
```

### 方法 3：Supabase Dashboard
1. 登入 Supabase
2. 進入專案
3. 點擊左側 "Table Editor"
4. 選擇 `calendar_api_calendarday` 或 `calendar_api_holiday` 表
5. 可以直接看到匯入的資料

---

## ❓ 常見問題

**Q: 連線 Supabase 失敗？**
- 檢查網路連線
- 確認 `.env` 中的 `DATABASE_URL` 正確
- 確認 Supabase 專案狀態正常

**Q: 如果想先用本地 SQLite 測試？**
```powershell
# 暫時註解掉 .env 中的 DATABASE_URL
# DATABASE_URL=...

# 執行 migrate 和 import_csv
python manage.py migrate
python manage.py import_csv ..\sample_data\calendar_2026_sample.csv --type calendar --skip-header
```

**Q: CSV 編碼錯誤？**
嘗試不同編碼：
```powershell
--encoding utf-8      # UTF-8
--encoding utf-8-sig  # UTF-8 with BOM
--encoding big5       # 繁體中文 Big5（政府資料常用）
--encoding cp950      # Windows 繁體中文
```

**Q: 需要更新資料？**
直接重新匯入即可，程式會自動更新 (update_or_create)

---

## ✨ 完成！

匯入成功後，你現在有：
- ✅ Supabase PostgreSQL 資料庫
- ✅ 完整的資料表結構
- ✅ 日曆和假日資料
- ✅ 可運作的 REST API
- ✅ API 文件介面

**下一步建議：**
1. 匯入完整年份的資料（2024-2030）
2. 開發前端應用程式
3. 部署到正式環境
