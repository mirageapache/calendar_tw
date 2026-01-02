from django.db import models


class CalendarDay(models.Model):
    """
    日曆日期模型 - 儲存每一天的詳細資訊
    """
    date = models.DateField(unique=True, verbose_name="日期", db_index=True)
    year = models.IntegerField(verbose_name="年份", db_index=True)
    month = models.IntegerField(verbose_name="月份", db_index=True)
    day = models.IntegerField(verbose_name="日")
    weekday = models.IntegerField(
        verbose_name="星期",
        help_text="0=週一, 1=週二, 2=週三, 3=週四, 4=週五, 5=週六, 6=週日"
    )
    is_weekend = models.BooleanField(default=False, verbose_name="是否為週末")
    is_holiday = models.BooleanField(default=False, verbose_name="是否為假日", db_index=True)
    is_workday = models.BooleanField(default=False, verbose_name="是否為補班日", db_index=True)
    holiday_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="假日名稱"
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name="說明"
    )

    class Meta:
        verbose_name = "日曆日期"
        verbose_name_plural = "日曆日期"
        ordering = ['date']
        indexes = [
            models.Index(fields=['year', 'month']),
            models.Index(fields=['date']),
        ]

    def __str__(self):
        return f"{self.date} ({self.get_weekday_display()})"

    def get_weekday_display(self):
        """返回星期的中文顯示"""
        weekdays = ['週一', '週二', '週三', '週四', '週五', '週六', '週日']
        return weekdays[self.weekday]

    def save(self, *args, **kwargs):
        """
        覆寫 save 方法，自動計算年、月、日、星期等欄位
        """
        if self.date:
            self.year = self.date.year
            self.month = self.date.month
            self.day = self.date.day
            # weekday() 返回 0-6，其中 0 是週一
            self.weekday = self.date.weekday()
            # 判斷是否為週末（週六或週日）
            self.is_weekend = self.weekday in [5, 6]
        super().save(*args, **kwargs)


class Holiday(models.Model):
    """
    假日模型 - 儲存國定假日、彈性放假等資訊
    """
    HOLIDAY_TYPE_CHOICES = [
        ('national', '國定假日'),
        ('flexible', '彈性放假'),
        ('adjusted', '調整放假'),
    ]

    name = models.CharField(max_length=100, verbose_name="假日名稱")
    date = models.DateField(verbose_name="日期", db_index=True)
    year = models.IntegerField(verbose_name="年份", db_index=True)
    holiday_type = models.CharField(
        max_length=20,
        choices=HOLIDAY_TYPE_CHOICES,
        default='national',
        verbose_name="假日類型"
    )
    is_lunar = models.BooleanField(default=False, verbose_name="是否為農曆假日")
    description = models.TextField(blank=True, verbose_name="說明")

    class Meta:
        verbose_name = "假日"
        verbose_name_plural = "假日"
        ordering = ['date']
        indexes = [
            models.Index(fields=['year', 'date']),
            models.Index(fields=['holiday_type']),
        ]

    def __str__(self):
        return f"{self.name} ({self.date})"

    def save(self, *args, **kwargs):
        """
        覆寫 save 方法，自動從日期提取年份
        """
        if self.date:
            self.year = self.date.year
        super().save(*args, **kwargs)


class WorkdayAdjustment(models.Model):
    """
    補班日模型 - 儲存補班日資訊
    """
    date = models.DateField(unique=True, verbose_name="補班日期", db_index=True)
    compensate_for = models.DateField(verbose_name="補哪一天的假")
    description = models.TextField(blank=True, verbose_name="說明")

    class Meta:
        verbose_name = "補班日"
        verbose_name_plural = "補班日"
        ordering = ['date']

    def __str__(self):
        return f"{self.date} 補 {self.compensate_for} 的假"
