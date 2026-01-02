# Calendar API 端點說明文件

## 📍 API 基礎路徑
所有 API 端點都以 `/api/` 為前綴

---

## 🗓️ CalendarDay (日曆日期) API

### 標準 CRUD 端點
| 方法 | 端點 | 說明 |
|------|------|------|
| GET | `/api/calendar-days/` | 取得所有日期列表 |
| POST | `/api/calendar-days/` | 建立新日期 |
| GET | `/api/calendar-days/{id}/` | 取得特定日期詳情 |
| PUT | `/api/calendar-days/{id}/` | 更新日期資訊 |
| PATCH | `/api/calendar-days/{id}/` | 部分更新日期資訊 |
| DELETE | `/api/calendar-days/{id}/` | 刪除日期 |

### 自訂查詢端點
| 端點 | 說明 | 範例 |
|------|------|------|
| `/api/calendar-days/by-date/{date}/` | 根據日期查詢 | `/api/calendar-days/by-date/2026-01-01/` |
| `/api/calendar-days/month/{year}/{month}/` | 查詢指定年月 | `/api/calendar-days/month/2026/1/` |
| `/api/calendar-days/holidays/` | 查詢所有假日 | `/api/calendar-days/holidays/?year=2026` |
| `/api/calendar-days/workdays/` | 查詢所有補班日 | `/api/calendar-days/workdays/?year=2026` |

### 過濾參數
- `year` - 年份
- `month` - 月份
- `is_weekend` - 是否為週末
- `is_holiday` - 是否為假日
- `is_workday` - 是否為補班日

**範例：** `/api/calendar-days/?year=2026&month=1&is_holiday=true`

---

## 🎉 Holiday (假日) API

### 標準 CRUD 端點
| 方法 | 端點 | 說明 |
|------|------|------|
| GET | `/api/holidays/` | 取得所有假日列表 |
| POST | `/api/holidays/` | 建立新假日 |
| GET | `/api/holidays/{id}/` | 取得特定假日詳情 |
| PUT | `/api/holidays/{id}/` | 更新假日資訊 |
| PATCH | `/api/holidays/{id}/` | 部分更新假日資訊 |
| DELETE | `/api/holidays/{id}/` | 刪除假日 |

### 自訂查詢端點
| 端點 | 說明 | 範例 |
|------|------|------|
| `/api/holidays/year/{year}/` | 查詢指定年份假日 | `/api/holidays/year/2026/` |
| `/api/holidays/lunar/` | 查詢農曆假日 | `/api/holidays/lunar/?year=2026` |
| `/api/holidays/national/` | 查詢國定假日 | `/api/holidays/national/?year=2026` |

### 過濾參數
- `year` - 年份
- `holiday_type` - 假日類型 (national/flexible/adjusted)
- `is_lunar` - 是否為農曆假日

**範例：** `/api/holidays/?year=2026&holiday_type=national`

---

## 💼 WorkdayAdjustment (補班日) API

### 標準 CRUD 端點
| 方法 | 端點 | 說明 |
|------|------|------|
| GET | `/api/workday-adjustments/` | 取得所有補班日列表 |
| POST | `/api/workday-adjustments/` | 建立新補班日 |
| GET | `/api/workday-adjustments/{id}/` | 取得特定補班日詳情 |
| PUT | `/api/workday-adjustments/{id}/` | 更新補班日資訊 |
| PATCH | `/api/workday-adjustments/{id}/` | 部分更新補班日資訊 |
| DELETE | `/api/workday-adjustments/{id}/` | 刪除補班日 |

### 自訂查詢端點
| 端點 | 說明 | 範例 |
|------|------|------|
| `/api/workday-adjustments/year/{year}/` | 查詢指定年份補班日 | `/api/workday-adjustments/year/2026/` |

---

## 🛠️ 實用工具 API

### 日期範圍查詢
```
GET /api/calendar/range/?start_date=2026-01-01&end_date=2026-01-31
```
查詢指定日期範圍內的所有日期資訊

### 今天的資訊
```
GET /api/calendar/today/
```
快速查詢今天的日期資訊（是否假日、補班日等）

### 檢查是否為假日
```
GET /api/calendar/is-holiday/?date=2026-01-01
```
檢查指定日期是否為假日、補班日或週末

**回應範例：**
```json
{
    "date": "2026-01-01",
    "is_holiday": true,
    "is_workday": false,
    "is_weekend": false,
    "holiday_name": "元旦"
}
```

### 月份統計摘要
```
GET /api/calendar/month-summary/?year=2026&month=1
```
取得指定月份的統計資訊

**回應範例：**
```json
{
    "year": 2026,
    "month": 1,
    "total_days": 31,
    "weekends": 8,
    "holidays": 3,
    "workday_adjustments": 0,
    "actual_workdays": 20
}
```

---

## 📚 API 文件

### Swagger UI (互動式文件)
```
http://localhost:8000/api/docs/
```

### ReDoc (美觀的文件)
```
http://localhost:8000/api/redoc/
```

### OpenAPI Schema
```
http://localhost:8000/api/schema/
```

---

## 🔍 通用查詢功能

所有列表端點都支援：

### 搜尋
使用 `search` 參數進行全文搜尋
```
/api/holidays/?search=春節
```

### 排序
使用 `ordering` 參數排序結果
```
/api/calendar-days/?ordering=-date  # 日期降序
/api/holidays/?ordering=date        # 日期升序
```

### 分頁
預設每頁 100 筆，可使用 `page` 參數
```
/api/calendar-days/?page=2
```