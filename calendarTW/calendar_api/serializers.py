from rest_framework import serializers
from .models import CalendarDay, Holiday, WorkdayAdjustment


class CalendarDaySerializer(serializers.ModelSerializer):
    """
    日曆日期序列化器
    """
    weekday_display = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = CalendarDay
        fields = [
            'id',
            'date',
            'year',
            'month',
            'day',
            'weekday',
            'weekday_display',
            'is_weekend',
            'is_holiday',
            'is_workday',
            'holiday_name',
            'description',
        ]
        read_only_fields = ['year', 'month', 'day', 'weekday', 'is_weekend']
    
    def get_weekday_display(self, obj):
        """返回星期的中文顯示"""
        return obj.get_weekday_display()
    
    def validate_date(self, value):
        """驗證日期欄位"""
        if value is None:
            raise serializers.ValidationError("日期不能為空")
        return value


class HolidaySerializer(serializers.ModelSerializer):
    """
    假日序列化器
    """
    holiday_type_display = serializers.CharField(
        source='get_holiday_type_display',
        read_only=True
    )
    
    class Meta:
        model = Holiday
        fields = [
            'id',
            'name',
            'date',
            'year',
            'holiday_type',
            'holiday_type_display',
            'is_lunar',
            'description',
        ]
        read_only_fields = ['year']
    
    def validate_name(self, value):
        """驗證假日名稱不能為空"""
        if not value or value.strip() == '':
            raise serializers.ValidationError("假日名稱不能為空")
        return value.strip()


class WorkdayAdjustmentSerializer(serializers.ModelSerializer):
    """
    補班日序列化器
    """
    class Meta:
        model = WorkdayAdjustment
        fields = [
            'id',
            'date',
            'compensate_for',
            'description',
        ]
    
    def validate(self, data):
        """
        驗證補班日期不能與補假日期相同
        """
        if data.get('date') and data.get('compensate_for'):
            if data['date'] == data['compensate_for']:
                raise serializers.ValidationError({
                    'compensate_for': '補班日期不能與補假日期相同'
                })
        return data


class CalendarDayListSerializer(serializers.ModelSerializer):
    """
    日曆日期列表序列化器（簡化版，用於列表顯示）
    """
    weekday_display = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = CalendarDay
        fields = [
            'id',
            'date',
            'weekday_display',
            'is_weekend',
            'is_holiday',
            'is_workday',
            'holiday_name',
        ]
    
    def get_weekday_display(self, obj):
        """返回星期的中文顯示"""
        return obj.get_weekday_display()


class HolidayListSerializer(serializers.ModelSerializer):
    """
    假日列表序列化器（簡化版，用於列表顯示）
    """
    holiday_type_display = serializers.CharField(
        source='get_holiday_type_display',
        read_only=True
    )
    
    class Meta:
        model = Holiday
        fields = [
            'id',
            'name',
            'date',
            'holiday_type_display',
            'is_lunar',
        ]
