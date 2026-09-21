from django import forms
from .models import Appointment


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ["title", "category", "weekday", "start_time", "end_time", "location", "notes"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "e.g. Database Systems lecture", "class": "field"}),
            "category": forms.Select(attrs={"class": "field"}),
            "weekday": forms.Select(attrs={"class": "field"}),
            "start_time": forms.TimeInput(attrs={"type": "time", "class": "field"}),
            "end_time": forms.TimeInput(attrs={"type": "time", "class": "field"}),
            "location": forms.TextInput(attrs={"placeholder": "e.g. Building 3, Room 210", "class": "field"}),
            "notes": forms.Textarea(attrs={"rows": 2, "class": "field"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["end_time"].required = False
        self.fields["location"].required = False
        self.fields["notes"].required = False
