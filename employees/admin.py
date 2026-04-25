from django.contrib import admin
from .models import (
    Department,
    Employee,
    Event,
    Task,
    MaintenanceAsset,
    MaintenanceRequest,
    Notification,
)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'position', 'department', 'can_enter_data', 'is_supervisor', 'active']
    list_filter = ['department', 'can_enter_data', 'is_supervisor', 'active']
    search_fields = ['name', 'code', 'position', 'phone']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['employee', 'date', 'event_type', 'score', 'duration_hours', 'created_by']
    list_filter = ['event_type', 'date']
    search_fields = ['employee__name', 'description']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'assigned_to', 'planned_date', 'estimated_hours', 'actual_hours', 'priority', 'status']
    list_filter = ['priority', 'status', 'planned_date']
    search_fields = ['title', 'description', 'location']


@admin.register(MaintenanceAsset)
class MaintenanceAssetAdmin(admin.ModelAdmin):
    list_display = ['name', 'asset_type', 'location', 'code', 'active']
    list_filter = ['asset_type', 'active']
    search_fields = ['name', 'code', 'location']


@admin.register(MaintenanceRequest)
class MaintenanceRequestAdmin(admin.ModelAdmin):
    list_display = ['title', 'asset', 'assigned_to', 'planned_date', 'estimated_hours', 'actual_hours', 'priority', 'status']
    list_filter = ['priority', 'status', 'planned_date']
    search_fields = ['title', 'asset__name', 'asset__code']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['title', 'message', 'user__username']
