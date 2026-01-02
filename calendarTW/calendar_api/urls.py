from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CalendarDayViewSet,
    HolidayViewSet,
    WorkdayAdjustmentViewSet,
    CalendarRangeAPIView,
    TodayAPIView,
    IsHolidayAPIView,
    MonthSummaryAPIView,
)

# 建立 Router 並註冊 ViewSets
router = DefaultRouter()
router.register(r'calendar-days', CalendarDayViewSet, basename='calendar-day')
router.register(r'holidays', HolidayViewSet, basename='holiday')
router.register(r'workday-adjustments', WorkdayAdjustmentViewSet, basename='workday-adjustment')

# URL patterns
urlpatterns = [
    # Router URLs (包含所有 ViewSet 的標準 CRUD 端點和自訂 action)
    path('', include(router.urls)),
    
    # 自訂 APIView 端點
    path('calendar/range/', CalendarRangeAPIView.as_view(), name='calendar-range'),
    path('calendar/today/', TodayAPIView.as_view(), name='calendar-today'),
    path('calendar/is-holiday/', IsHolidayAPIView.as_view(), name='is-holiday'),
    path('calendar/month-summary/', MonthSummaryAPIView.as_view(), name='month-summary'),
]
