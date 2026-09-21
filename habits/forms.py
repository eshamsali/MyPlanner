from django import forms
from .models import Habit

DAY_CHOICES = [
    ("0", "Mon"), ("1", "Tue"), ("2", "Wed"), ("3", "Thu"),
    ("4", "Fri"), ("5", "Sat"), ("6", "Sun"),
]


class HabitForm(forms.ModelForm):
    # Not a model field directly — mapped to/from Habit.active_days (a
    # comma-separated string) in __init__/save below. Only used when
    # frequency is set to "weekly" ("Specific days"); the template should
    # show/hide this block based on the frequency select.
    days = forms.MultipleChoiceField(
        choices=DAY_CHOICES, required=False, widget=forms.CheckboxSelectMultiple,
        label="Days",
    )

    class Meta:
        model = Habit
        fields = ["name", "icon", "color", "frequency", "goal_per_day", "reminder_time"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "e.g. Drink water", "class": "field"}),
            "icon": forms.Select(attrs={"class": "field"}, choices=[
                ("droplet", "Water"), ("book", "Read"), ("dumbbell", "Workout"),
                ("graduation-cap", "Study"), ("moon", "Sleep"), ("sparkles", "General"),
            ]),
            "color": forms.Select(attrs={"class": "field"}, choices=[
                ("accent", "Lavender"), ("success", "Green"), ("warning", "Orange"), ("error", "Red"),
            ]),
            "frequency": forms.Select(attrs={"class": "field", "id": "id_frequency"}),
            "goal_per_day": forms.NumberInput(attrs={"class": "field"}),
            "reminder_time": forms.TimeInput(attrs={"type": "time", "class": "field"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.active_days:
            self.fields["days"].initial = self.instance.active_days.split(",")

    def save(self, commit=True):
        habit = super().save(commit=False)
        selected_days = self.cleaned_data.get("days") or []
        habit.active_days = ",".join(selected_days)
        if commit:
            habit.save()
        return habit
