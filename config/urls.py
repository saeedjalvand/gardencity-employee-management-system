from django.contrib import admin
from django.urls import path
from employees.views import (
    landing_page,
    logout_view,
    dashboard,
    employee_list,
    employee_detail,
    employee_scores,
    add_employee,
    add_event,
    edit_event,
    delete_event,
    task_list,
    task_history,
    add_task,
    edit_task,
    complete_task,
    delete_task,
    maintenance_asset_list,
    add_maintenance_asset,
    maintenance_request_list,
    add_maintenance_request,
    notification_list,
    mark_notification_read,
)

urlpatterns = [
    path('', landing_page, name='landing'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard, name='dashboard'),
    path('admin/', admin.site.urls),

    path('employees/', employee_list, name='employee_list'),
    path('employees/<int:employee_id>/', employee_detail, name='employee_detail'),
    path('scores/', employee_scores, name='employee_scores'),
    path('add-employee/', add_employee, name='add_employee'),

    path('add-event/', add_event, name='add_event'),
    path('events/<int:event_id>/edit/', edit_event, name='edit_event'),
    path('events/<int:event_id>/delete/', delete_event, name='delete_event'),

    path('tasks/', task_list, name='task_list'),
    path('tasks/history/', task_history, name='task_history'),
    path('add-task/', add_task, name='add_task'),
    path('tasks/<int:task_id>/edit/', edit_task, name='edit_task'),
    path('tasks/<int:task_id>/complete/', complete_task, name='complete_task'),
    path('tasks/<int:task_id>/delete/', delete_task, name='delete_task'),

    path('assets/', maintenance_asset_list, name='asset_list'),
    path('add-asset/', add_maintenance_asset, name='add_asset'),

    path('maintenance/', maintenance_request_list, name='maintenance_request_list'),
    path('add-maintenance/', add_maintenance_request, name='add_maintenance'),

    path('notifications/', notification_list, name='notification_list'),
    path('notifications/<int:notification_id>/read/', mark_notification_read, name='mark_notification_read'),
]
