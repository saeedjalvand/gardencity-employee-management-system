from django.contrib.auth.models import Permission, User
from django.test import TestCase
from django.urls import reverse

from .models import Department, Employee, Event, Notification, Task


class EmployeeManagementViewsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='manager', password='secret123')
        self.department = Department.objects.create(name='Gardening')
        self.employee = Employee.objects.create(
            user=self.user,
            name='Sample Employee',
            code='EMP-001',
            position='Supervisor',
            department=self.department,
        )

    def test_landing_redirects_authenticated_users(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('landing'))
        self.assertRedirects(response, reverse('dashboard'))

    def test_add_task_creates_notification_for_linked_user(self):
        permission = Permission.objects.get(codename='add_task')
        self.user.user_permissions.add(permission)
        self.client.force_login(self.user)

        response = self.client.post(reverse('add_task'), {
            'title': 'Morning irrigation',
            'description': 'Check sector B',
            'assigned_to': self.employee.id,
            'planned_date': '2026-04-24',
            'estimated_hours': '2.00',
            'priority': 'high',
            'location': 'Sector B',
        })

        self.assertRedirects(response, reverse('task_list'))
        self.assertEqual(Notification.objects.count(), 1)
        notification = Notification.objects.first()
        self.assertEqual(notification.user, self.user)

    def test_complete_task_creates_single_positive_event(self):
        permission = Permission.objects.get(codename='change_task')
        self.user.user_permissions.add(permission)
        task = Task.objects.create(
            title='Trim hedges',
            assigned_to=self.employee,
            created_by=self.user,
        )

        self.client.force_login(self.user)
        response = self.client.post(reverse('complete_task', args=[task.id]), {
            'status': 'done',
            'completed_by': self.employee.id,
            'actual_hours': '3.00',
            'score_awarded': 5,
            'close_note': 'Completed successfully',
        })

        task.refresh_from_db()
        self.assertRedirects(response, reverse('task_list'))
        self.assertEqual(task.status, 'done')
        self.assertTrue(task.close_event_created)
        self.assertEqual(Event.objects.filter(employee=self.employee, event_type='positive').count(), 1)

    def test_delete_event_removes_employee_record(self):
        permission = Permission.objects.get(codename='delete_event')
        self.user.user_permissions.add(permission)
        event = Event.objects.create(
            employee=self.employee,
            event_type='negative',
            date='2026-04-24',
            description='Late arrival',
            score=1,
            created_by=self.user,
        )

        self.client.force_login(self.user)
        response = self.client.post(reverse('delete_event', args=[event.id]))

        self.assertRedirects(response, reverse('employee_detail', args=[self.employee.id]))
        self.assertFalse(Event.objects.filter(id=event.id).exists())
