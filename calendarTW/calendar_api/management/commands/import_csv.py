"""
從 CSV 檔案匯入台灣日曆資料的 Django 管理指令
支援匯入政府公開資料平台下載的日曆資料
"""
import csv
from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_date
from calendar_api.models import CalendarDay, Holiday, WorkdayAdjustment
from datetime import datetime


class Command(BaseCommand):
    help = '從 CSV 檔案匯入台灣日曆資料'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help='CSV 檔案路徑'
        )
        parser.add_argument(
            '--type',
            type=str,
            choices=['calendar', 'holiday', 'workday'],
            default='calendar',
            help='資料類型：calendar (日曆), holiday (假日), workday (補班日)'
        )
        parser.add_argument(
            '--encoding',
            type=str,
            default='utf-8-sig',
            help='CSV 檔案編碼 (預設: utf-8-sig，支援 Big5, UTF-8 等)'
        )
        parser.add_argument(
            '--skip-header',
            action='store_true',
            help='是否跳過第一行標題列'
        )

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        data_type = options['type']
        encoding = options['encoding']
        skip_header = options['skip_header']

        self.stdout.write(self.style.SUCCESS(f'\n開始匯入 CSV 檔案: {csv_file}'))
        self.stdout.write(f'資料類型: {data_type}')
        self.stdout.write(f'檔案編碼: {encoding}\n')

        try:
            # 嘗試不同的編碼
            encodings_to_try = [encoding, 'utf-8-sig', 'utf-8', 'big5', 'cp950']
            
            csv_data = None
            used_encoding = None
            
            for enc in encodings_to_try:
                try:
                    with open(csv_file, 'r', encoding=enc, newline='') as f:
                        csv_data = list(csv.reader(f))
                        used_encoding = enc
                        break
                except (UnicodeDecodeError, FileNotFoundError):
                    continue
            
            if csv_data is None:
                self.stdout.write(self.style.ERROR('無法讀取 CSV 檔案，請檢查檔案路徑和編碼'))
                return
            
            self.stdout.write(self.style.SUCCESS(f'✓ 成功讀取檔案 (使用編碼: {used_encoding})'))
            self.stdout.write(f'總共 {len(csv_data)} 行資料\n')

            # 如果要跳過標題列
            if skip_header and len(csv_data) > 0:
                header = csv_data[0]
                self.stdout.write(f'標題列: {header}')
                csv_data = csv_data[1:]

            # 根據類型匯入
            if data_type == 'calendar':
                self.import_calendar_days(csv_data)
            elif data_type == 'holiday':
                self.import_holidays(csv_data)
            elif data_type == 'workday':
                self.import_workdays(csv_data)

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'找不到檔案: {csv_file}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'匯入過程發生錯誤: {str(e)}'))
            import traceback
            traceback.print_exc()

    def import_calendar_days(self, csv_data):
        """
        匯入日曆資料
        預期 CSV 格式：日期,年,月,日,星期,是否週末,是否假日,是否補班,假日名稱,說明
        或簡化格式：日期,是否假日,假日名稱
        """
        created_count = 0
        updated_count = 0
        error_count = 0

        self.stdout.write('開始匯入日曆資料...')
        
        for i, row in enumerate(csv_data, start=1):
            try:
                if len(row) < 1:
                    continue

                # 解析日期（支援多種格式）
                date_str = row[0].strip()
                date = self.parse_date_flexible(date_str)
                
                if not date:
                    self.stdout.write(self.style.WARNING(f'第 {i} 行: 無法解析日期 "{date_str}"'))
                    error_count += 1
                    continue

                # 準備資料
                defaults = {
                    'year': date.year,
                    'month': date.month,
                    'day': date.day,
                    'weekday': date.weekday(),
                    'is_weekend': date.weekday() in [5, 6],
                }

                # 如果有更多欄位
                if len(row) >= 2:
                    # 是否為假日
                    is_holiday_str = row[1].strip() if len(row) > 1 else ''
                    defaults['is_holiday'] = is_holiday_str.lower() in ['true', '1', 'yes', 'y', '是']
                
                if len(row) >= 3:
                    # 假日名稱
                    defaults['holiday_name'] = row[2].strip() if row[2].strip() else None
                
                if len(row) >= 4:
                    # 是否為補班日
                    is_workday_str = row[3].strip() if len(row) > 3 else ''
                    defaults['is_workday'] = is_workday_str.lower() in ['true', '1', 'yes', 'y', '是']
                
                if len(row) >= 5:
                    # 說明
                    defaults['description'] = row[4].strip() if row[4].strip() else None

                # 建立或更新
                calendar_day, created = CalendarDay.objects.update_or_create(
                    date=date,
                    defaults=defaults
                )

                if created:
                    created_count += 1
                else:
                    updated_count += 1

                if (created_count + updated_count) % 100 == 0:
                    self.stdout.write(f'  處理進度: {created_count + updated_count} 筆...')

            except Exception as e:
                error_count += 1
                self.stdout.write(self.style.WARNING(f'第 {i} 行處理失敗: {str(e)}'))

        self.stdout.write(self.style.SUCCESS(f'\n✅ 日曆資料匯入完成！'))
        self.stdout.write(f'  新增: {created_count} 筆')
        self.stdout.write(f'  更新: {updated_count} 筆')
        if error_count > 0:
            self.stdout.write(self.style.WARNING(f'  錯誤: {error_count} 筆'))

    def import_holidays(self, csv_data):
        """
        匯入假日資料
        預期 CSV 格式：日期,假日名稱,假日類型,是否農曆,說明
        或簡化格式：日期,假日名稱
        """
        created_count = 0
        updated_count = 0
        error_count = 0

        self.stdout.write('開始匯入假日資料...')

        for i, row in enumerate(csv_data, start=1):
            try:
                if len(row) < 2:
                    continue

                # 解析日期
                date_str = row[0].strip()
                date = self.parse_date_flexible(date_str)
                
                if not date:
                    self.stdout.write(self.style.WARNING(f'第 {i} 行: 無法解析日期 "{date_str}"'))
                    error_count += 1
                    continue

                # 假日名稱
                holiday_name = row[1].strip()

                # 準備資料
                defaults = {
                    'name': holiday_name,
                    'year': date.year,
                }

                # 假日類型
                if len(row) >= 3:
                    holiday_type = row[2].strip()
                    if holiday_type in ['national', 'flexible', 'adjusted']:
                        defaults['holiday_type'] = holiday_type
                    else:
                        defaults['holiday_type'] = 'national'
                else:
                    defaults['holiday_type'] = 'national'

                # 是否農曆
                if len(row) >= 4:
                    is_lunar_str = row[3].strip()
                    defaults['is_lunar'] = is_lunar_str.lower() in ['true', '1', 'yes', 'y', '是']

                # 說明
                if len(row) >= 5:
                    defaults['description'] = row[4].strip()

                # 建立或更新假日
                holiday, created = Holiday.objects.update_or_create(
                    date=date,
                    defaults=defaults
                )

                # 同時更新 CalendarDay
                try:
                    calendar_day = CalendarDay.objects.get(date=date)
                    calendar_day.is_holiday = True
                    calendar_day.holiday_name = holiday_name
                    calendar_day.save()
                except CalendarDay.DoesNotExist:
                    # 如果沒有對應的日曆日期，建立一個
                    CalendarDay.objects.create(
                        date=date,
                        is_holiday=True,
                        holiday_name=holiday_name
                    )

                if created:
                    created_count += 1
                else:
                    updated_count += 1

            except Exception as e:
                error_count += 1
                self.stdout.write(self.style.WARNING(f'第 {i} 行處理失敗: {str(e)}'))

        self.stdout.write(self.style.SUCCESS(f'\n✅ 假日資料匯入完成！'))
        self.stdout.write(f'  新增: {created_count} 筆')
        self.stdout.write(f'  更新: {updated_count} 筆')
        if error_count > 0:
            self.stdout.write(self.style.WARNING(f'  錯誤: {error_count} 筆'))

    def import_workdays(self, csv_data):
        """
        匯入補班日資料
        預期 CSV 格式：日期,說明,補哪一天
        """
        created_count = 0
        updated_count = 0
        error_count = 0

        self.stdout.write('開始匯入補班日資料...')

        for i, row in enumerate(csv_data, start=1):
            try:
                if len(row) < 1:
                    continue

                # 解析日期
                date_str = row[0].strip()
                date = self.parse_date_flexible(date_str)
                
                if not date:
                    error_count += 1
                    continue

                # 準備資料
                defaults = {
                    'year': date.year,
                }

                if len(row) >= 2:
                    defaults['description'] = row[1].strip()

                if len(row) >= 3:
                    compensate_date_str = row[2].strip()
                    compensate_date = self.parse_date_flexible(compensate_date_str)
                    if compensate_date:
                        defaults['compensate_date'] = compensate_date

                # 建立或更新補班日
                workday, created = WorkdayAdjustment.objects.update_or_create(
                    date=date,
                    defaults=defaults
                )

                # 同時更新 CalendarDay
                try:
                    calendar_day = CalendarDay.objects.get(date=date)
                    calendar_day.is_workday = True
                    calendar_day.save()
                except CalendarDay.DoesNotExist:
                    CalendarDay.objects.create(
                        date=date,
                        is_workday=True
                    )

                if created:
                    created_count += 1
                else:
                    updated_count += 1

            except Exception as e:
                error_count += 1
                self.stdout.write(self.style.WARNING(f'第 {i} 行處理失敗: {str(e)}'))

        self.stdout.write(self.style.SUCCESS(f'\n✅ 補班日資料匯入完成！'))
        self.stdout.write(f'  新增: {created_count} 筆')
        self.stdout.write(f'  更新: {updated_count} 筆')
        if error_count > 0:
            self.stdout.write(self.style.WARNING(f'  錯誤: {error_count} 筆'))

    def parse_date_flexible(self, date_str):
        """彈性解析多種日期格式"""
        if not date_str:
            return None
        
        # 移除常見的分隔符並嘗試多種格式
        formats = [
            '%Y-%m-%d',
            '%Y/%m/%d',
            '%Y%m%d',
            '%Y.%m.%d',
            '%d/%m/%Y',
            '%d-%m-%Y',
            '%m/%d/%Y',
            '%m-%d-%Y',
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt).date()
            except ValueError:
                continue
        
        # 嘗試使用 Django 的解析器
        try:
            return parse_date(date_str.strip())
        except:
            return None
