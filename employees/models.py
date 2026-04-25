from django.db import models
from django.contrib.auth.models import User


class Department(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    position = models.CharField(max_length=200)
    phone = models.CharField(max_length=50, blank=True, null=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    can_enter_data = models.BooleanField(default=False)
    is_supervisor = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.code})"


class Event(models.Model):
    EVENT_TYPE_CHOICES = [
        ('positive', 'ئەرێنی'),
        ('negative', 'نەرێنی'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES)
    date = models.DateField()
    description = models.TextField()
    score = models.IntegerField(default=0)
    duration_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.name} - {self.event_type} - {self.date}"


class Task(models.Model):
    STATUS_CHOICES = [
        ('todo', 'لە چاوەڕوانیدا'),
        ('in_progress', 'لە جێبەجێکردندایە'),
        ('done', 'تەواو بووە'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'نزم'),
        ('medium', 'مامناوەند'),
        ('high', 'بەرز'),
        ('urgent', 'زۆر گرنگ'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    assigned_to = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks'
    )
    planned_date = models.DateField(null=True, blank=True)
    estimated_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    actual_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    location = models.CharField(max_length=255, blank=True, null=True)

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    completed_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='completed_tasks'
    )
    score_awarded = models.IntegerField(default=0)
    close_note = models.TextField(blank=True, null=True)
    close_event_created = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class MaintenanceAsset(models.Model):
    name = models.CharField(max_length=200)
    asset_type = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class MaintenanceRequest(models.Model):
    STATUS_CHOICES = [
        ('open', 'کراوە'),
        ('in_progress', 'لە جێبەجێکردندایە'),
        ('done', 'تەواو بووە'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'نزم'),
        ('medium', 'مامناوەند'),
        ('high', 'بەرز'),
        ('urgent', 'زۆر گرنگ'),
    ]

    title = models.CharField(max_length=200)
    asset = models.ForeignKey(MaintenanceAsset, on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    planned_date = models.DateField(null=True, blank=True)
    estimated_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    actual_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    reported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='maintenance_reported')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title