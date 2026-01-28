"""
匯入政府行政機關辦公日曆表 CSV 檔案
專門處理政府公開資料平台的標準格式
"""
import csv
from django.core.management.base import BaseCommand
from calendar_api.models import CalendarDay, Holiday, WorkdayAdjustment
from datetime import datetime


class Command(BaseCommand):
    help = '匯入政府行政機關辦公日曆表 CSV 檔案'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help='政府行政機關辦公日曆表 CSV 檔案路徑'
        )
        parser.add_argument(
            '--encoding',
            type=str,
            default='utf-8',
            help='CSV 檔案編碼 (預設: utf-8)'
        )
        parser.add_argument(
            '--year',
            type=int,
            help='只匯入指定年份的資料'
        )

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        encoding = options['encoding']
        filter_year = options.get('year')

        self.stdout.write(self.style.SUCCESS(f'\n📅 開始匯入政府行政機關辦公日曆表'))
        self.stdout.write(f'檔案: {csv_file}')
        self.stdout.write(f'編碼: {encoding}\n')

        try:
            # 嘗試不同的編碼
            encodings_to_try = [encoding, 'utf-8', 'utf-8-sig', 'big5', 'cp950']
            
            csv_data = None
            used_encoding = None
            
            for enc in encodings_to_try:
                try:
                    with open(csv_file, 'r', encoding=enc, newline='') as f:
                        reader = csv.DictReader(f)
                        csv_data = list(reader)
                        
                        # 移除 BOM (Byte Order Mark)
                        if csv_data and csv_data[0]:
                            first_key = list(csv_data[0].keys())[0]
                            if first_key.startswith('\ufeff'):
                                # 重新讀取，修正欄位名稱
                                csv_data = []
                                with open(csv_file, 'r', encoding='utf-8-sig', newline='') as f2:
                                    reader2 = csv.DictReader(f2)
                                    csv_data = list(reader2)
                                    enc = 'utf-8-sig'
                        
                        used_encoding = enc
                        break
                except (UnicodeDecodeError, FileNotFoundError):
                    continue
            
            if csv_data is None:
                self.stdout.write(self.style.ERROR('❌ 無法讀取 CSV 檔案'))
                return
            
            self.stdout.write(self.style.SUCCESS(f'✓ 成功讀取檔案 (編碼: {used_encoding})'))
            self.stdout.write(f'總筆數: {len(csv_data)}\n')

            # 檢查欄位
            if csv_data:
                expected_fields = ['date', 'year', 'name', 'isholiday', 'holidaycategory', 'description']
                actual_fields = list(csv_data[0].keys())
                self.stdout.write(f'欄位: {actual_fields}\n')

            # 如果指定年份，過濾資料
            if filter_year:
                csv_data = [row for row in csv_data if row.get('year') == str(filter_year)]
                self.stdout.write(f'過濾年份 {filter_year}: {len(csv_data)} 筆\n')

            # 統計資料
            stats = self.import_data(csv_data)
            
            # 顯示統計結果
            self.stdout.write(self.style.SUCCESS('\n' + '='*60))
            self.stdout.write(self.style.SUCCESS('✅ 匯入完成！'))
            self.stdout.write(self.style.SUCCESS('='*60))
            self.stdout.write(f'\n📊 統計資訊:')
            self.stdout.write(f'  日曆資料: 新增 {stats["calendar_created"]} 筆, 更新 {stats["calendar_updated"]} 筆')
            self.stdout.write(f'  假日資料: 新增 {stats["holiday_created"]} 筆, 更新 {stats["holiday_updated"]} 筆')
            self.stdout.write(f'  補班日資料: 新增 {stats["workday_created"]} 筆, 更新 {stats["workday_updated"]} 筆')
            if stats["errors"] > 0:
                self.stdout.write(self.style.WARNING(f'  ⚠️  錯誤: {stats["errors"]} 筆'))
            self.stdout.write('')

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'❌ 找不到檔案: {csv_file}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ 匯入過程發生錯誤: {str(e)}'))
            import traceback
            traceback.print_exc()

    def import_data(self, csv_data):
        """匯入資料"""
        stats = {
            'calendar_created': 0,
            'calendar_updated': 0,
            'holiday_created': 0,
            'holiday_updated': 0,
            'workday_created': 0,
            'workday_updated': 0,
            'errors': 0,
        }

        self.stdout.write('開始處理資料...\n')
        
        for i, row in enumerate(csv_data, start=1):
            try:
                # 解析欄位
                date_str = row.get('date', '').strip()
                year_str = row.get('year', '').strip()
                name = row.get('name', '').strip()
                isholiday = row.get('isholiday', '').strip()
                holidaycategory = row.get('holidaycategory', '').strip()
                description = row.get('description', '').strip()

                # 解析日期
                if len(date_str) != 8:
                    self.stdout.write(self.style.WARNING(f'第 {i} 行: 日期格式錯誤 "{date_str}"'))
                    stats['errors'] += 1
                    continue

                date = datetime.strptime(date_str, '%Y%m%d').date()

                # 判斷是否為假日
                is_holiday = isholiday == '是'
                
                # 判斷是否為補班日
                is_workday = holidaycategory == '補行上班日'
                
                # 判斷是否為週末
                is_weekend = date.weekday() in [5, 6]

                # 建立或更新 CalendarDay
                calendar_defaults = {
                    'year': date.year,
                    'month': date.month,
                    'day': date.day,
                    'weekday': date.weekday(),
                    'is_weekend': is_weekend,
                    'is_holiday': is_holiday and not is_workday,  # 補班日不算假日
                    'is_workday': is_workday,
                    'holiday_name': name if name else None,
                    'description': description if description else None,
                }

                calendar_day, created = CalendarDay.objects.update_or_create(
                    date=date,
                    defaults=calendar_defaults
                )

                if created:
                    stats['calendar_created'] += 1
                else:
                    stats['calendar_updated'] += 1

                # 如果有假日名稱，建立 Holiday 記錄
                if name and is_holiday and not is_workday:
                    # 判斷假日類型
                    if holidaycategory == '放假之紀念日及節日':
                        holiday_type = 'national'
                    elif holidaycategory == '調整放假日':
                        holiday_type = 'adjusted'
                    elif holidaycategory == '補假':
                        holiday_type = 'flexible'
                    else:
                        holiday_type = 'national'

                    # 判斷是否為農曆假日
                    is_lunar = any(keyword in name for keyword in ['春節', '端午', '中秋', '農曆'])

                    holiday_defaults = {
                        'name': name,
                        'year': date.year,
                        'holiday_type': holiday_type,
                        'is_lunar': is_lunar,
                        'description': description if description else '',
                    }

                    holiday, h_created = Holiday.objects.update_or_create(
                        date=date,
                        defaults=holiday_defaults
                    )

                    if h_created:
                        stats['holiday_created'] += 1
                    else:
                        stats['holiday_updated'] += 1

                # 如果是補班日，建立 WorkdayAdjustment 記錄
                if is_workday:
                    workday_defaults = {
                        'year': date.year,
                        'description': description if description else holidaycategory,
                    }

                    workday, w_created = WorkdayAdjustment.objects.update_or_create(
                        date=date,
                        defaults=workday_defaults
                    )

                    if w_created:
                        stats['workday_created'] += 1
                    else:
                        stats['workday_updated'] += 1

                # 進度顯示
                if i % 100 == 0:
                    self.stdout.write(f'  處理進度: {i}/{len(csv_data)} 筆...')

            except Exception as e:
                stats['errors'] += 1
                self.stdout.write(self.style.WARNING(f'第 {i} 行處理失敗: {str(e)}'))

        return stats
