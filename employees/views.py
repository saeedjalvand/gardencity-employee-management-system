from django.shortcuts import render, redirect
from django.db.models import Sum
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required

from .models import (
    Employee,
    Event,
    Task,
    MaintenanceAsset,
    MaintenanceRequest,
)
from .forms import (
    EmployeeForm,
    EventForm,
    TaskForm,
    MaintenanceAssetForm,
    MaintenanceRequestForm,
)


def landing_page(request):
    error_message = ''

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            error_message = 'ناوی بەکارهێنەر یان وشەی نهێنی هەڵەیە.'

    return render(request, 'employees/landing.html', {'error_message': error_message})


def logout_view(request):
    logout(request)
    return redirect('landing')


@login_required
def dashboard(request):
    total_employees = Employee.objects.count()
    total_tasks = Task.objects.count()
    open_tasks = Task.objects.filter(status__in=['todo', 'in_progress']).count()
    done_tasks = Task.objects.filter(status='done').count()

    total_assets = MaintenanceAsset.objects.count()
    open_maintenance = MaintenanceRequest.objects.filter(status__in=['open', 'in_progress']).count()

    score_rows = []
    for emp in Employee.objects.filter(active=True):
        positive = Event.objects.filter(
            employee=emp,
            event_type='positive'
        ).aggregate(Sum('score'))['score__sum'] or 0

        negative = Event.objects.filter(
            employee=emp,
            event_type='negative'
        ).aggregate(Sum('score'))['score__sum'] or 0

        total = positive - negative
        score_rows.append({
            'employee': emp,
            'score': total,
        })

    score_rows = sorted(score_rows, key=lambda x: x['score'], reverse=True)[:5]
    recent_tasks = Task.objects.order_by('-created_at')[:6]
    recent_maintenance = MaintenanceRequest.objects.order_by('-created_at')[:6]

    context = {
        'total_employees': total_employees,
        'total_tasks': total_tasks,
        'open_tasks': open_tasks,
        'done_tasks': done_tasks,
        'total_assets': total_assets,
        'open_maintenance': open_maintenance,
        'score_rows': score_rows,
        'recent_tasks': recent_tasks,
        'recent_maintenance': recent_maintenance,
    }
    return render(request, 'employees/dashboard.html', context)


@login_required
def employee_list(request):
    employees = Employee.objects.select_related('department').all().order_by('name')
    return render(request, 'employees/employee_list.html', {'employees': employees})


@login_required
def employee_scores(request):
    employees = Employee.objects.select_related('department').all()
    data = []

    for emp in employees:
        positive = Event.objects.filter(
            employee=emp,
            event_type='positive'
        ).aggregate(Sum('score'))['score__sum'] or 0

        negative = Event.objects.filter(
            employee=emp,
            event_type='negative'
        ).aggregate(Sum('score'))['score__sum'] or 0

        duration = Event.objects.filter(
            employee=emp
        ).aggregate(Sum('duration_hours'))['duration_hours__sum'] or 0

        total = positive - negative

        data.append({
            'name': emp.name,
            'position': emp.position,
            'department': emp.department.name,
            'positive': positive,
            'negative': negative,
            'score': total,
            'duration': duration,
        })

    data = sorted(data, key=lambda x: x['score'], reverse=True)
    return render(request, 'employees/employee_scores.html', {'data': data})


@login_required
@permission_required('employees.add_employee', raise_exception=True)
def add_employee(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'کارمەند بە سەرکەوتوویی زیادکرا.')
            return redirect('employee_list')
    else:
        form = EmployeeForm()

    return render(
        request,
        'employees/form_page.html',
        {
            'title': 'زیادکردنی کارمەند',
            'form': form,
            'back_url': '/employees/',
        }
    )


@login_required
@permission_required('employees.add_event', raise_exception=True)
def add_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.created_by = request.user
            obj.save()
            messages.success(request, 'تۆمارکردنی کار/ڕووداو بە سەرکەوتوویی ئەنجامدرا.')
            return redirect('employee_scores')
    else:
        form = EventForm()

    return render(
        request,
        'employees/form_page.html',
        {
            'title': 'تۆمارکردنی ڕووداو / هەڵسەنگاندن',
            'form': form,
            'back_url': '/scores/',
        }
    )


@login_required
def task_list(request):
    tasks = Task.objects.select_related('assigned_to').all().order_by('-created_at')
    return render(request, 'employees/task_list.html', {'tasks': tasks})


@login_required
@permission_required('employees.add_task', raise_exception=True)
def add_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.created_by = request.user
            obj.save()
            messages.success(request, 'پلانی نوێ بە سەرکەوتوویی زیادکرا.')
            return redirect('task_list')
    else:
        form = TaskForm()

    return render(
        request,
        'employees/form_page.html',
        {
            'title': 'زیادکردنی پلان / To-Do',
            'form': form,
            'back_url': '/tasks/',
        }
    )


@login_required
def maintenance_asset_list(request):
    assets = MaintenanceAsset.objects.all().order_by('name')
    return render(request, 'employees/asset_list.html', {'assets': assets})


@login_required
@permission_required('employees.add_maintenanceasset', raise_exception=True)
def add_maintenance_asset(request):
    if request.method == 'POST':
        form = MaintenanceAssetForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'کەرەستە یان ئامێری نوێ بە سەرکەوتوویی زیادکرا.')
            return redirect('asset_list')
    else:
        form = MaintenanceAssetForm()

    return render(
        request,
        'employees/form_page.html',
        {
            'title': 'زیادکردنی کەرەستەی چاکسازی',
            'form': form,
            'back_url': '/assets/',
        }
    )


@login_required
def maintenance_request_list(request):
    requests = MaintenanceRequest.objects.select_related('asset', 'assigned_to').all().order_by('-created_at')
    return render(request, 'employees/maintenance_list.html', {'requests': requests})


@login_required
@permission_required('employees.add_maintenancerequest', raise_exception=True)
def add_maintenance_request(request):
    if request.method == 'POST':
        form = MaintenanceRequestForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.reported_by = request.user
            obj.save()
            messages.success(request, 'داواکاریی چاکسازی بە سەرکەوتوویی تۆمارکرا.')
            return redirect('maintenance_request_list')
    else:
        form = MaintenanceRequestForm()

    return render(
        request,
        'employees/form_page.html',
        {
            'title': 'تۆمارکردنی داواکاریی چاکسازی',
            'form': form,
            'back_url': '/maintenance/',
        }
    )