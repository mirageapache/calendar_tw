from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from datetime import datetime, timedelta
from django.db.models import Q

from .models import CalendarDay, Holiday, WorkdayAdjustment
from .serializers import (
    CalendarDaySerializer,
    CalendarDayListSerializer,
    HolidaySerializer,
    HolidayListSerializer,
    WorkdayAdjustmentSerializer,
)


class CalendarDayViewSet(viewsets.ModelViewSet):
    """
    日曆日期 ViewSet
    提供完整的 CRUD 操作
    """
    queryset = CalendarDay.objects.all()
    serializer_class = CalendarDaySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['year', 'month', 'is_weekend', 'is_holiday', 'is_workday']
    search_fields = ['holiday_name', 'description']
    ordering_fields = ['date', 'year', 'month']
    ordering = ['date']
    
    def get_serializer_class(self):
        """根據 action 返回不同的 serializer"""
        if self.action == 'list':
            return CalendarDayListSerializer
        return CalendarDaySerializer
    
    @action(detail=False, methods=['get'], url_path='by-date/(?P<date>[0-9-]+)')
    def by_date(self, request, date=None):
        """
        根據日期查詢單一日期資訊
        URL: /api/calendar-days/by-date/2026-01-01/
        """
        try:
            calendar_day = CalendarDay.objects.get(date=date)
            serializer = self.get_serializer(calendar_day)
            return Response(serializer.data)
        except CalendarDay.DoesNotExist:
            return Response(
                {'error': '找不到該日期的資料'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'], url_path='month/(?P<year>[0-9]+)/(?P<month>[0-9]+)')
    def by_month(self, request, year=None, month=None):
        """
        查詢指定年月的所有日期
        URL: /api/calendar-days/month/2026/1/
        """
        calendar_days = CalendarDay.objects.filter(year=year, month=month)
        serializer = self.get_serializer(calendar_days, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def holidays(self, request):
        """
        查詢所有假日
        URL: /api/calendar-days/holidays/
        """
        year = request.query_params.get('year', None)
        queryset = CalendarDay.objects.filter(is_holiday=True)
        
        if year:
            queryset = queryset.filter(year=year)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def workdays(self, request):
        """
        查詢所有補班日
        URL: /api/calendar-days/workdays/
        """
        year = request.query_params.get('year', None)
        queryset = CalendarDay.objects.filter(is_workday=True)
        
        if year:
            queryset = queryset.filter(year=year)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class HolidayViewSet(viewsets.ModelViewSet):
    """
    假日 ViewSet
    提供完整的 CRUD 操作
    """
    queryset = Holiday.objects.all()
    serializer_class = HolidaySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['year', 'holiday_type', 'is_lunar']
    search_fields = ['name', 'description']
    ordering_fields = ['date', 'year']
    ordering = ['date']
    
    def get_serializer_class(self):
        """根據 action 返回不同的 serializer"""
        if self.action == 'list':
            return HolidayListSerializer
        return HolidaySerializer
    
    @action(detail=False, methods=['get'], url_path='year/(?P<year>[0-9]+)')
    def by_year(self, request, year=None):
        """
        查詢指定年份的所有假日
        URL: /api/holidays/year/2026/
        """
        holidays = Holiday.objects.filter(year=year)
        serializer = self.get_serializer(holidays, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def lunar(self, request):
        """
        查詢所有農曆假日
        URL: /api/holidays/lunar/
        """
        year = request.query_params.get('year', None)
        queryset = Holiday.objects.filter(is_lunar=True)
        
        if year:
            queryset = queryset.filter(year=year)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def national(self, request):
        """
        查詢所有國定假日
        URL: /api/holidays/national/
        """
        year = request.query_params.get('year', None)
        queryset = Holiday.objects.filter(holiday_type='national')
        
        if year:
            queryset = queryset.filter(year=year)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class WorkdayAdjustmentViewSet(viewsets.ModelViewSet):
    """
    補班日 ViewSet
    提供完整的 CRUD 操作
    """
    queryset = WorkdayAdjustment.objects.all()
    serializer_class = WorkdayAdjustmentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['date']
    ordering = ['date']
    
    @action(detail=False, methods=['get'], url_path='year/(?P<year>[0-9]+)')
    def by_year(self, request, year=None):
        """
        查詢指定年份的所有補班日
        URL: /api/workday-adjustments/year/2026/
        """
        # 使用 date__year 來過濾
        workdays = WorkdayAdjustment.objects.filter(date__year=year)
        serializer = self.get_serializer(workdays, many=True)
        return Response(serializer.data)


class CalendarRangeAPIView(APIView):
    """
    查詢日期範圍的 API View
    URL: /api/calendar/range/?start_date=2026-01-01&end_date=2026-01-31
    """
    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not start_date or not end_date:
            return Response(
                {'error': '請提供 start_date 和 end_date 參數'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            calendar_days = CalendarDay.objects.filter(
                date__gte=start_date,
                date__lte=end_date
            )
            serializer = CalendarDaySerializer(calendar_days, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class TodayAPIView(APIView):
    """
    查詢今天的日期資訊
    URL: /api/calendar/today/
    """
    def get(self, request):
        today = datetime.now().date()
        
        try:
            calendar_day = CalendarDay.objects.get(date=today)
            serializer = CalendarDaySerializer(calendar_day)
            return Response(serializer.data)
        except CalendarDay.DoesNotExist:
            return Response(
                {'error': '今天的日期資料尚未建立'},
                status=status.HTTP_404_NOT_FOUND
            )


class IsHolidayAPIView(APIView):
    """
    檢查指定日期是否為假日
    URL: /api/calendar/is-holiday/?date=2026-01-01
    """
    def get(self, request):
        date_str = request.query_params.get('date')
        
        if not date_str:
            return Response(
                {'error': '請提供 date 參數'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            calendar_day = CalendarDay.objects.get(date=date_str)
            return Response({
                'date': calendar_day.date,
                'is_holiday': calendar_day.is_holiday,
                'is_workday': calendar_day.is_workday,
                'is_weekend': calendar_day.is_weekend,
                'holiday_name': calendar_day.holiday_name,
            })
        except CalendarDay.DoesNotExist:
            return Response(
                {'error': '找不到該日期的資料'},
                status=status.HTTP_404_NOT_FOUND
            )


class MonthSummaryAPIView(APIView):
    """
    查詢指定月份的統計摘要
    URL: /api/calendar/month-summary/?year=2026&month=1
    """
    def get(self, request):
        year = request.query_params.get('year')
        month = request.query_params.get('month')
        
        if not year or not month:
            return Response(
                {'error': '請提供 year 和 month 參數'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            calendar_days = CalendarDay.objects.filter(year=year, month=month)
            
            total_days = calendar_days.count()
            weekends = calendar_days.filter(is_weekend=True).count()
            holidays = calendar_days.filter(is_holiday=True).count()
            workdays = calendar_days.filter(is_workday=True).count()
            
            # 實際工作日 = 總天數 - 週末 - 假日 + 補班日
            actual_workdays = total_days - weekends - holidays + workdays
            
            return Response({
                'year': int(year),
                'month': int(month),
                'total_days': total_days,
                'weekends': weekends,
                'holidays': holidays,
                'workday_adjustments': workdays,
                'actual_workdays': actual_workdays,
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
