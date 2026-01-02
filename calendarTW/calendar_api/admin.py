from django.contrib import admin
from .models import CalendarDay, Holiday, WorkdayAdjustment


@admin.register(CalendarDay)
class CalendarDayAdmin(admin.ModelAdmin):
    list_display = ['date', 'year', 'month', 'day', 'weekday', 'is_weekend', 'is_holiday', 'is_workday', 'holiday_name']
    list_filter = ['year', 'month', 'is_weekend', 'is_holiday', 'is_workday']
    search_fields = ['date', 'holiday_name', 'description']
    date_hierarchy = 'date'
    ordering = ['-date']
    readonly_fields = ['year', 'month', 'day', 'weekday', 'is_weekend']


@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ['name', 'date', 'year', 'holiday_type', 'is_lunar']
    list_filter = ['year', 'holiday_type', 'is_lunar']
    search_fields = ['name', 'description']
    date_hierarchy = 'date'
    ordering = ['-date']
    readonly_fields = ['year']


@admin.register(WorkdayAdjustment)
class WorkdayAdjustmentAdmin(admin.ModelAdmin):
    list_display = ['date', 'compensate_for', 'description']
    search_fields = ['description']
    date_hierarchy = 'date'
    ordering = ['-date']

