# CSV 匯入指南

## 📋 概述

本專案提供了 `import_csv` 管理指令，可以直接從 CSV 檔案匯入台灣日曆資料到資料庫。

## 🚀 快速開始

### 步驟 1：執行資料庫遷移（首次使用）

```powershell
cd calendarTW
python manage.py migrate
```

這會在 Supabase（或本地 SQLite）建立所需的資料表。

### 步驟 2：準備 CSV 檔案

將從政府公開資料平台下載的 CSV 檔案放到專案目錄。

### 步驟 3：匯入資料

```powershell
# 基本用法
python manage.py import_csv 路徑/檔案名稱.csv --type calendar --skip-header

# 指定編碼（如果是 Big5）
python manage.py import_csv 資料.csv --type holiday --encoding big5 --skip-header
```

---

## 📝 CSV 格式說明

### 1. 日曆資料 (--type calendar)

**基本格式（最少需要）：**
```csv
日期
2026-01-01
2026-01-02
2026-01-03
```

**完整格式：**
```csv
日期,是否假日,假日名稱,是否補班,說明
2026-01-01,true,中華民國開國紀念日,false,
2026-01-02,false,,,
2026-01-03,false,,,
2026-02-14,false,,,一般工作日
```

**欄位說明：**
- `日期`: 必填，格式可以是 `2026-01-01`、`2026/01/01`、`20260101`
- `是否假日`: true/false 或 1/0 或 是/否
- `假日名稱`: 假日的名稱
- `是否補班`: true/false 或 1/0 或 是/否
- `說明`: 備註說明

### 2. 假日資料 (--type holiday)

**基本格式：**
```csv
日期,假日名稱
2026-01-01,中華民國開國紀念日
2026-02-28,和平紀念日
2026-04-04,兒童節及清明節
```

**完整格式：**
```csv
日期,假日名稱,假日類型,是否農曆,說明
2026-01-01,中華民國開國紀念日,national,false,國定假日
2026-01-27,春節,national,true,農曆正月初一
2026-02-28,和平紀念日,national,false,
```

**欄位說明：**
- `日期`: 必填
- `假日名稱`: 必填
- `假日類型`: national (國定假日) / flexible (彈性放假) / adjusted (調整放假)
- `是否農曆`: true/false
- `說明`: 備註

### 3. 補班日資料 (--type workday)

```csv
日期,說明,補哪一天
2026-01-23,補班,2026-01-26
```

---

## 💡 使用範例

### 範例 1：匯入政府公開資料平台的行事曆

假設你下載了「中華民國 115 年政府行政機關辦公日曆表」CSV 檔：

```powershell
# 如果檔案有標題列，使用 --skip-header
python manage.py import_csv 115年行事曆.csv --type calendar --encoding big5 --skip-header

# 或使用 UTF-8 編碼
python manage.py import_csv calendar_2026.csv --type calendar --skip-header
```

### 範例 2：只匯入假日資料

```powershell
python manage.py import_csv holidays_2026.csv --type holiday --skip-header
```

### 範例 3：自動偵測編碼

指令會自動嘗試以下編碼：
1. 你指定的編碼
2. utf-8-sig (UTF-8 with BOM)
3. utf-8
4. big5
5. cp950

```powershell
# 不指定編碼，讓程式自動偵測
python manage.py import_csv 資料.csv --type calendar --skip-header
```

---

## 🛠️ 完整指令參數

```
python manage.py import_csv <CSV檔案路徑> [選項]

必要參數:
  csv_file              CSV 檔案路徑

選項:
  --type {calendar,holiday,workday}
                        資料類型 (預設: calendar)
                        - calendar: 日曆日期資料
                        - holiday: 假日資料  
                        - workday: 補班日資料

  --encoding ENCODING   CSV 檔案編碼 (預設: utf-8-sig)
                        常用: utf-8, utf-8-sig, big5, cp950

  --skip-header         跳過第一行標題列
```

---

## ✅ 完整流程範例

```powershell
# 1. 確保在正確的目錄
cd c:\Users\user\Documents\my_repo\calendar_tw\calendarTW

# 2. 執行資料庫遷移（首次）
python manage.py migrate

# 3. 建立管理員帳號（首次）
python manage.py createsuperuser

# 4. 匯入日曆資料
python manage.py import_csv ..\data\calendar_2026.csv --type calendar --skip-header

# 5. 匯入假日資料
python manage.py import_csv ..\data\holidays_2026.csv --type holiday --skip-header

# 6. 啟動伺服器查看結果
python manage.py runserver 8200

# 7. 開啟瀏覽器測試
# http://localhost:8200/api/calendar-days/
# http://localhost:8200/api/holidays/
# http://localhost:8200/admin/
```

---

## 📊 驗證匯入結果

### 方法 1：使用 Django Shell
```powershell
python manage.py shell
```

```python
from calendar_api.models import CalendarDay, Holiday

# 檢查匯入筆數
print(f"日曆資料: {CalendarDay.objects.count()} 筆")
print(f"假日資料: {Holiday.objects.count()} 筆")

# 檢查 2026 年的假日
holidays_2026 = Holiday.objects.filter(year=2026)
for h in holidays_2026:
    print(f"{h.date} - {h.name}")

# 檢查某個日期
from datetime import date
day = CalendarDay.objects.get(date=date(2026, 1, 1))
print(f"日期: {day.date}")
print(f"是否假日: {day.is_holiday}")
print(f"假日名稱: {day.holiday_name}")
```

### 方法 2：使用 API
```
GET http://localhost:8200/api/calendar-days/?year=2026&is_holiday=true
GET http://localhost:8200/api/holidays/by-year/2026/
```

### 方法 3：使用 Django Admin
1. 前往 http://localhost:8200/admin/
2. 登入後可以瀏覽和編輯資料

---

## 🔧 常見問題

### Q1: 編碼錯誤怎麼辦？
嘗試指定正確的編碼：
```powershell
# 政府資料常用 Big5
python manage.py import_csv 檔案.csv --encoding big5 --skip-header

# 如果是 UTF-8 with BOM
python manage.py import_csv 檔案.csv --encoding utf-8-sig --skip-header
```

### Q2: 日期格式無法識別？
指令支援多種日期格式：
- `2026-01-01` (推薦)
- `2026/01/01`
- `20260101`
- `01/01/2026`
- `01-01-2026`

如果都不行，請調整 CSV 中的日期格式為 `YYYY-MM-DD`

### Q3: 匯入後發現資料錯誤？
可以重新匯入，指令會自動更新（update_or_create）：
```powershell
# 重新匯入會覆蓋舊資料
python manage.py import_csv 更新後的檔案.csv --type calendar --skip-header
```

### Q4: 如何清空資料重新匯入？
```powershell
python manage.py shell
```
```python
from calendar_api.models import CalendarDay, Holiday, WorkdayAdjustment

# 刪除所有資料（小心使用！）
CalendarDay.objects.all().delete()
Holiday.objects.all().delete()
WorkdayAdjustment.objects.all().delete()
```

---

## 📁 CSV 檔案範例

專案中提供了範例檔案供參考：

### calendar_sample.csv
```csv
日期,是否假日,假日名稱,是否補班,說明
2026-01-01,true,中華民國開國紀念日,false,
2026-01-02,false,,,
2026-01-03,false,,,
2026-01-23,false,,true,補 1/26 春節假期
2026-01-26,true,農曆除夕,false,
2026-01-27,true,春節,false,
2026-02-28,true,和平紀念日,false,
```

### holidays_sample.csv
```csv
日期,假日名稱,假日類型,是否農曆
2026-01-01,中華民國開國紀念日,national,false
2026-01-26,農曆除夕,national,true
2026-01-27,春節,national,true
2026-01-28,春節,national,true
2026-02-28,和平紀念日,national,false
2026-04-03,兒童節,national,false
2026-04-04,清明節,national,false
```

---

## 🌐 政府公開資料來源

- [政府資料開放平臺](https://data.gov.tw/)
- 搜尋關鍵字：「行事曆」、「國定假日」、「辦公日曆」
- [人事行政總處 - 政府行政機關辦公日曆表](https://www.dgpa.gov.tw/information?uid=10&pid=7925)

---

## 🎯 下一步

匯入資料後，你可以：
1. ✅ 使用 API 查詢資料
2. ✅ 開發前端應用程式
3. ✅ 設定定期更新資料
4. ✅ 部署到正式環境
