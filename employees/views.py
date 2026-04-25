from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Count, Q, Sum
from django.utils import timezone

from .models import (
    Employee,
    Event,
    Task,
    MaintenanceAsset,
    MaintenanceRequest,
    Notification,
)
from .forms import (
    EmployeeForm,
    EventForm,
    TaskForm,
    TaskCloseForm,
    MaintenanceAssetForm,
    MaintenanceRequestForm,
)


def landing_page(request):
    if request.user.is_authenticated:
        return redirect('/dashboard/')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('/dashboard/')
        else:
            messages.error(request, 'ناوی بەکارهێنەر یان پاسوورد هەڵەیە')

    return render(request, 'employees/landing.html')


def logout_view(request):
    logout(request)
    return redirect('/')


@login_required
def dashboard(request):
    employee_count = Employee.objects.count()
    event_count = Event.objects.count()
    open_task_count = Task.objects.exclude(status='done').count()
    active_employee_count = Employee.objects.filter(active=True).count()
    maintenance_open_count = MaintenanceRequest.objects.exclude(status='done').count()

    employees = Employee.objects.select_related('department').annotate(
        positive_score=Sum('events__score', filter=Q(events__event_type='positive')),
        negative_score=Sum('events__score', filter=Q(events__event_type='negative')),
        event_total=Count('events'),
    )

    top_employees = []
    for emp in employees:
        positive = emp.positive_score or 0
        negative = emp.negative_score or 0
        top_employees.append({
            'id': emp.id,
            'name': emp.name,
            'position': emp.position,
            'department': emp.department.name,
            'event_total': emp.event_total,
            'total_score': positive - negative,
        })

    top_employees = sorted(top_employees, key=lambda x: x['total_score'], reverse=True)[:5]
    latest_tasks = Task.objects.select_related('assigned_to').order_by('-created_at')[:4]
    latest_maintenance_requests = MaintenanceRequest.objects.select_related(
        'asset',
        'assigned_to',
    ).order_by('-created_at')[:4]

    context = {
        'employee_count': employee_count,
        'active_employee_count': active_employee_count,
        'event_count': event_count,
        'task_count': open_task_count,
        'maintenance_open_count': maintenance_open_count,
        'top_employees': top_employees,
        'latest_tasks': latest_tasks,
        'latest_maintenance_requests': latest_maintenance_requests,
    }
    return render(request, 'employees/dashboard.html', context)


@login_required
def employee_list(request):
    employees = Employee.objects.select_related('department').annotate(
        event_total=Count('events'),
        assigned_task_total=Count('assigned_tasks'),
    ).order_by('name')
    return render(request, 'employees/employee_list.html', {'employees': employees})


@login_required
def employee_detail(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    events = Event.objects.filter(employee=employee).order_by('-date', '-created_at')

    return render(request, 'employees/employee_detail.html', {
        'employee': employee,
        'events': events
    })


@login_required
@permission_required('employees.add_employee', raise_exception=True)
def add_employee(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'کارمەند بە سەرکەوتوویی زیادکرا')
            return redirect('/employees/')
    else:
        form = EmployeeForm()

    return render(request, 'employees/form_page.html', {
        'form': form,
        'title': 'زیادکردنی کارمەند',
        'back_url': '/employees/'
    })


@login_required
@permission_required('employees.add_event', raise_exception=True)
def add_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.created_by = request.user
            obj.save()
            messages.success(request, 'ڕووداو بە سەرکەوتوویی تۆمارکرا')
            return redirect(f'/employees/{obj.employee.id}/')
    else:
        form = EventForm()

    return render(request, 'employees/form_page.html', {
        'form': form,
        'title': 'زیادکردنی ڕووداو',
        'back_url': '/employees/'
    })


@login_required
@permission_required('employees.change_event', raise_exception=True)
def edit_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'زانیاری نوێکرایەوە')
            return redirect(f'/employees/{event.employee.id}/')
    else:
        form = EventForm(instance=event)

    return render(request, 'employees/form_page.html', {
        'form': form,
        'title': 'دەستکاری ڕووداو',
        'back_url': f'/employees/{event.employee.id}/'
    })


@login_required
@permission_required('employees.delete_event', raise_exception=True)
def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    back_url = f'/employees/{event.employee.id}/'

    if request.method == 'POST':
        event.delete()
        messages.success(request, 'ڕووداو بە سەرکەوتوویی سڕایەوە')
        return redirect(back_url)

    return render(request, 'employees/delete_confirm.html', {
        'object_name': f'{event.employee.name} - {event.date}',
        'back_url': back_url,
    })


@login_required
def employee_scores(request):
    employees = Employee.objects.select_related('department').annotate(
        positive_score=Sum('events__score', filter=Q(events__event_type='positive')),
        negative_score=Sum('events__score', filter=Q(events__event_type='negative')),
        total_duration=Sum('events__duration_hours'),
        event_total=Count('events'),
    )
    data = []

    for emp in employees:
        positive = emp.positive_score or 0
        negative = emp.negative_score or 0
        duration = emp.total_duration or 0
        total = positive - negative

        data.append({
            'employee_id': emp.id,
            'name': emp.name,
            'position': emp.position,
            'department': emp.department.name,
            'positive': positive,
            'negative': negative,
            'score': total,
            'duration': duration,
            'event_total': emp.event_total,
        })

    data = sorted(data, key=lambda x: x['score'], reverse=True)

    return render(request, 'employees/employee_scores.html', {'data': data})


@login_required
def task_list(request):
    tasks = Task.objects.select_related('assigned_to').exclude(status='done').order_by(
        'planned_date',
        '-created_at',
    )
    return render(request, 'employees/task_list.html', {'tasks': tasks})


@login_required
def task_history(request):
    tasks = Task.objects.select_related('completed_by').filter(status='done').order_by('-created_at')
    return render(request, 'employees/task_history.html', {'tasks': tasks})


@login_required
@permission_required('employees.add_task', raise_exception=True)
def add_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.save()

            assigned_employee = task.assigned_to
            linked_user = getattr(assigned_employee, 'user', None) if assigned_employee else None

            if linked_user:
                Notification.objects.create(
                    user=linked_user,
                    title='ئەرکی نوێ بۆ تۆ زیادکرا',
                    message=f'ئەرکی "{task.title}" بۆ تۆ دیاریکراوە.'
                )
                messages.success(request, 'ئەرک زیادکرا و ئاگادارکردنەوە نێردرا.')
            else:
                messages.warning(
                    request,
                    'ئەرک زیادکرا، بەڵام بۆ ئەم کارمەندە user پەیوەست نەکراوە، بۆیە ئاگادارکردنەوە نەنێردرا.'
                )

            return redirect('/tasks/')
    else:
        form = TaskForm()

    return render(request, 'employees/form_page.html', {
        'form': form,
        'title': 'زیادکردنی ئەرک',
        'back_url': '/tasks/'
    })


@login_required
@permission_required('employees.change_task', raise_exception=True)
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, 'ئەرک نوێکرایەوە')
            return redirect('/tasks/')
    else:
        form = TaskForm(instance=task)

    return render(request, 'employees/form_page.html', {
        'form': form,
        'title': 'دەستکاری ئەرک',
        'back_url': '/tasks/'
    })


@login_required
@permission_required('employees.change_task', raise_exception=True)
def complete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if request.method == 'POST':
        form = TaskCloseForm(request.POST, instance=task)
        if form.is_valid():
            with transaction.atomic():
                task = form.save(commit=False)
                task.status = 'done'
                task.save()

                if task.completed_by and not task.close_event_created:
                    Event.objects.create(
                        employee=task.completed_by,
                        event_type='positive',
                        date=timezone.localdate(),
                        description=f'ئەنجامدانی ئەرک: {task.title}\n{task.close_note or ""}',
                        score=task.score_awarded,
                        duration_hours=task.actual_hours,
                        created_by=request.user
                    )
                    task.close_event_created = True
                    task.save(update_fields=['close_event_created'])

            messages.success(request, 'ئەرک وەک تەواوبوو تۆمارکرا و چووە بۆ سوابقی کارمەند')
            return redirect('/tasks/')
    else:
        form = TaskCloseForm(instance=task)

    return render(request, 'employees/task_complete.html', {
        'form': form,
        'task': task,
        'title': 'تەواوکردنی ئەرک',
        'back_url': '/tasks/'
    })


@login_required
@permission_required('employees.delete_task', raise_exception=True)
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if request.method == 'POST':
        task.delete()
        messages.success(request, 'ئەرک بە سەرکەوتوویی سڕایەوە')
        return redirect('/tasks/history/')

    return render(request, 'employees/delete_confirm.html', {
        'object_name': task.title,
        'back_url': '/tasks/history/',
    })


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
            return redirect('/assets/')
    else:
        form = MaintenanceAssetForm()

    return render(request, 'employees/form_page.html', {
        'form': form,
        'title': 'زیادکردنی ئامێر',
        'back_url': '/assets/'
    })


@login_required
def maintenance_request_list(request):
    requests = MaintenanceRequest.objects.select_related('asset', 'assigned_to').order_by(
        '-created_at'
    )
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
            return redirect('/maintenance/')
    else:
        form = MaintenanceRequestForm()

    return render(request, 'employees/form_page.html', {
        'form': form,
        'title': 'داواکاری چاکسازی',
        'back_url': '/maintenance/'
    })


@login_required
def notification_list(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'employees/notification_list.html', {'notifications': notifications})


@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect('/notifications/')


def unread_notifications_count(request):
    if request.user.is_authenticated:
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return {'unread_notifications_count': count}
    return {'unread_notifications_count': 0}
