from django.contrib import admin
from django.urls import path
from employees.views import (
    landing_page,
    logout_view,
    dashboard,
    employee_list,
    employee_scores,
    add_employee,
    add_event,
    task_list,
    add_task,
    maintenance_asset_list,
    add_maintenance_asset,
    maintenance_request_list,
    add_maintenance_request,
)

urlpatterns = [
    path('', landing_page, name='landing'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard, name='dashboard'),
    path('admin/', admin.site.urls),

    path('employees/', employee_list, name='employee_list'),
    path('scores/', employee_scores, name='employee_scores'),
    path('add-employee/', add_employee, name='add_employee'),
    path('add-event/', add_event, name='add_event'),

    path('tasks/', task_list, name='task_list'),
    path('add-task/', add_task, name='add_task'),

    path('assets/', maintenance_asset_list, name='asset_list'),
    path('add-asset/', add_maintenance_asset, name='add_asset'),

    path('maintenance/', maintenance_request_list, name='maintenance_request_list'),
    path('add-maintenance/', add_maintenance_request, name='add_maintenance'),
]