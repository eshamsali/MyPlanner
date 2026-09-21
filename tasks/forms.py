from django import forms
from .models import Task


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            "title", "description", "category", "priority", "due_date",
            "start_time", "end_time", "repeat", "reminder_minutes_before", "goal",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "e.g. Finish database assignment", "class": "field"}),
            "description": forms.Textarea(attrs={"rows": 3, "placeholder": "Add details...", "class": "field"}),
            "due_date": forms.DateInput(attrs={"type": "date", "class": "field"}),
            "start_time": forms.TimeInput(attrs={"type": "time", "class": "field"}),
            "end_time": forms.TimeInput(attrs={"type": "time", "class": "field"}),
            "category": forms.Select(attrs={"class": "field"}),
            "priority": forms.Select(attrs={"class": "field"}),
            "repeat": forms.Select(attrs={"class": "field"}),
            "reminder_minutes_before": forms.NumberInput(attrs={"class": "field", "placeholder": "e.g. 30"}),
            "goal": forms.Select(attrs={"class": "field"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.fields["goal"].required = False
        if user is not None:
            self.fields["goal"].queryset = self.fields["goal"].queryset.filter(user=user)
