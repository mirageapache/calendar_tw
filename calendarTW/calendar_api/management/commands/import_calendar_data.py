"""
匯入台灣日曆資料的 Django 管理指令
用於初始化資料庫中的日期資料
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from calendar_api.models import CalendarDay, Holiday, WorkdayAdjustment


class Command(BaseCommand):
    help = '匯入台灣日曆資料（日期、假日、補班日）'

    def add_arguments(self, parser):
        parser.add_argument(
            '--year',
            type=int,
            default=datetime.now().year,
            help='指定要匯入的年份（預設為當前年份）'
        )
        parser.add_argument(
            '--start-year',
            type=int,
            help='起始年份（用於匯入多年資料）'
        )
        parser.add_argument(
            '--end-year',
            type=int,
            help='結束年份（用於匯入多年資料）'
        )

    def handle(self, *args, **options):
        # 判斷是匯入單年還是多年
        if options['start_year'] and options['end_year']:
            years = range(options['start_year'], options['end_year'] + 1)
        else:
            years = [options['year']]

        for year in years:
            self.stdout.write(self.style.SUCCESS(f'\n開始匯入 {year} 年資料...'))
            self.import_calendar_days(year)
            self.import_holidays(year)
            self.stdout.write(self.style.SUCCESS(f'✅ {year} 年資料匯入完成！\n'))

    def import_calendar_days(self, year):
        """匯入整年的日曆日期資料"""
        start_date = datetime(year, 1, 1).date()
        end_date = datetime(year, 12, 31).date()
        
        current_date = start_date
        created_count = 0
        updated_count = 0
        
        while current_date <= end_date:
            calendar_day, created = CalendarDay.objects.update_or_create(
                date=current_date,
                defaults={
                    'year': current_date.year,
                    'month': current_date.month,
                    'day': current_date.day,
                    'weekday': current_date.weekday(),
                    'is_weekend': current_date.weekday() in [5, 6],
                }
            )
            
            if created:
                created_count += 1
            else:
                updated_count += 1
            
            current_date += timedelta(days=1)
        
        self.stdout.write(
            f'  📅 日曆日期: 新增 {created_count} 筆, 更新 {updated_count} 筆'
        )

    def import_holidays(self, year):
        """匯入假日資料"""
        # 這裡是範例資料，實際使用時需要根據政府公告調整
        holidays_data = self.get_holidays_data(year)
        
        created_count = 0
        updated_count = 0
        
        for holiday_info in holidays_data:
            # 建立或更新假日記錄
            holiday, created = Holiday.objects.update_or_create(
                date=holiday_info['date'],
                defaults={
                    'name': holiday_info['name'],
                    'year': year,
                    'holiday_type': holiday_info.get('holiday_type', 'national'),
                    'is_lunar': holiday_info.get('is_lunar', False),
                    'description': holiday_info.get('description', ''),
                }
            )
            
            # 更新對應的 CalendarDay
            try:
                calendar_day = CalendarDay.objects.get(date=holiday_info['date'])
                calendar_day.is_holiday = True
                calendar_day.holiday_name = holiday_info['name']
                calendar_day.save()
            except CalendarDay.DoesNotExist:
                pass
            
            if created:
                created_count += 1
            else:
                updated_count += 1
        
        self.stdout.write(
            f'  🎉 假日資料: 新增 {created_count} 筆, 更新 {updated_count} 筆'
        )

    def get_holidays_data(self, year):
        """
        取得假日資料
        TODO: 這裡需要根據實際情況調整
        可以從政府開放資料平台或其他來源取得
        """
        # 2026 年範例資料
        if year == 2026:
            return [
                {'date': datetime(2026, 1, 1).date(), 'name': '中華民國開國紀念日', 'holiday_type': 'national'},
                {'date': datetime(2026, 1, 26).date(), 'name': '農曆除夕', 'holiday_type': 'national', 'is_lunar': True},
                {'date': datetime(2026, 1, 27).date(), 'name': '春節', 'holiday_type': 'national', 'is_lunar': True},
                {'date': datetime(2026, 1, 28).date(), 'name': '春節', 'holiday_type': 'national', 'is_lunar': True},
                {'date': datetime(2026, 1, 29).date(), 'name': '春節', 'holiday_type': 'national', 'is_lunar': True},
                {'date': datetime(2026, 2, 28).date(), 'name': '和平紀念日', 'holiday_type': 'national'},
                {'date': datetime(2026, 4, 3).date(), 'name': '兒童節', 'holiday_type': 'national'},
                {'date': datetime(2026, 4, 4).date(), 'name': '清明節', 'holiday_type': 'national'},
                {'date': datetime(2026, 6, 25).date(), 'name': '端午節', 'holiday_type': 'national', 'is_lunar': True},
                {'date': datetime(2026, 10, 1).date(), 'name': '中秋節', 'holiday_type': 'national', 'is_lunar': True},
                {'date': datetime(2026, 10, 10).date(), 'name': '國慶日', 'holiday_type': 'national'},
            ]
        
        # 其他年份回傳空列表，或實作自動抓取邏輯
        return []
