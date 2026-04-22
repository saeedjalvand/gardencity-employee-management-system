from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission


class Command(BaseCommand):
    help = "Create default role groups"

    def handle(self, *args, **kwargs):
        roles = {
            'Admin': [
                'add_employee', 'change_employee', 'view_employee',
                'add_event', 'change_event', 'view_event',
                'add_task', 'change_task', 'view_task',
                'add_maintenanceasset', 'change_maintenanceasset', 'view_maintenanceasset',
                'add_maintenancerequest', 'change_maintenancerequest', 'view_maintenancerequest',
            ],
            'Supervisor': [
                'view_employee',
                'add_event', 'view_event',
                'add_task', 'change_task', 'view_task',
                'view_maintenanceasset',
                'add_maintenancerequest', 'view_maintenancerequest',
            ],
            'Data Entry': [
                'view_employee',
                'add_event', 'view_event',
                'add_task', 'view_task',
            ],
            'Maintenance': [
                'view_employee',
                'view_task',
                'add_maintenanceasset', 'view_maintenanceasset',
                'add_maintenancerequest', 'change_maintenancerequest', 'view_maintenancerequest',
            ],
        }

        for role_name, perms in roles.items():
            group, created = Group.objects.get_or_create(name=role_name)
            group.permissions.clear()

            for codename in perms:
                try:
                    perm = Permission.objects.get(codename=codename)
                    group.permissions.add(perm)
                except Permission.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f'Permission not found: {codename}'))

            if created:
                self.stdout.write(self.style.SUCCESS(f'Created group: {role_name}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Updated group: {role_name}'))