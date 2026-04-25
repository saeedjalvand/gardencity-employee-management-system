from django import forms
from .models import Employee, Event, Task, MaintenanceAsset, MaintenanceRequest


class StyledModelForm(forms.ModelForm):
    field_help_texts = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            widget = field.widget
            css_class = widget.attrs.get('class', '')
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs['class'] = 'form-check-input'
            else:
                widget.attrs['class'] = f'{css_class} form-control'.strip()
                widget.attrs.setdefault('placeholder', field.label)

            help_text = self.field_help_texts.get(name)
            if help_text:
                field.help_text = help_text


class EmployeeForm(StyledModelForm):
    field_help_texts = {
        'user': 'ئەگەر دەتەوێت ئەم کارمەندە ئاگادارکردنەوە و هەژمار هەبێت، بە یوزەرێک بیبەستەوە.',
        'code': 'کۆدی تایبەتی کارمەند کە دووبارە نابێت.',
    }

    class Meta:
        model = Employee
        fields = [
            'user',
            'name',
            'code',
            'position',
            'phone',
            'department',
            'active',
            'can_enter_data',
            'is_supervisor',
        ]
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_enter_data': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_supervisor': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class EventForm(StyledModelForm):
    field_help_texts = {
        'score': 'ئاستی کاریگەریی ڕووداوەکە بە خاڵ.',
        'duration_hours': 'ماوەکە بە ژمارەی کاتژمێر، وەک 1.5 یان 2.25.',
    }

    date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
        })
    )

    class Meta:
        model = Event
        fields = [
            'employee',
            'event_type',
            'date',
            'description',
            'score',
            'duration_hours',
        ]
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-control'}),
            'event_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'score': forms.NumberInput(attrs={'class': 'form-control'}),
            'duration_hours': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.25'}),
        }


class TaskForm(StyledModelForm):
    field_help_texts = {
        'assigned_to': 'ئەگەر کارمەندەکە یوزەری پەیوەست هەبێت، ئاگادارکردنەوە بۆی دەنێردرێت.',
        'estimated_hours': 'کاتی پێشبینی کراو بۆ تەواوکردنی ئەرک.',
    }

    planned_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
        })
    )

    class Meta:
        model = Task
        fields = [
            'title',
            'description',
            'assigned_to',
            'planned_date',
            'estimated_hours',
            'priority',
            'location',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'assigned_to': forms.Select(attrs={'class': 'form-control'}),
            'estimated_hours': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.25'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
        }


class TaskCloseForm(StyledModelForm):
    field_help_texts = {
        'completed_by': 'کێ ئەم ئەرکەی تەواو کردووە.',
        'score_awarded': 'ئەو خاڵەی دەبێت بۆ ئەم تەواوکارییە زیاد بکرێت.',
    }

    class Meta:
        model = Task
        fields = [
            'status',
            'completed_by',
            'actual_hours',
            'score_awarded',
            'close_note',
        ]
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'completed_by': forms.Select(attrs={'class': 'form-control'}),
            'actual_hours': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.25'}),
            'score_awarded': forms.NumberInput(attrs={'class': 'form-control'}),
            'close_note': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }


class MaintenanceAssetForm(StyledModelForm):
    class Meta:
        model = MaintenanceAsset
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'asset_type': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class MaintenanceRequestForm(StyledModelForm):
    field_help_texts = {
        'estimated_hours': 'کاتی پێشبینی کراو بۆ چارەسەری کێشەکە.',
        'actual_hours': 'ئەگەر ئیشی دەستی پێکردووە، کاتی واقعی لێرە تۆمار بکە.',
    }

    planned_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
        })
    )

    class Meta:
        model = MaintenanceRequest
        fields = [
            'title',
            'asset',
            'assigned_to',
            'planned_date',
            'estimated_hours',
            'actual_hours',
            'priority',
            'status',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'asset': forms.Select(attrs={'class': 'form-control'}),
            'assigned_to': forms.Select(attrs={'class': 'form-control'}),
            'estimated_hours': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.25'}),
            'actual_hours': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.25'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
