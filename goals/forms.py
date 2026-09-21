from django import forms
from django.forms import inlineformset_factory

from .models import Goal, Milestone


class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = ["name", "icon", "category", "description", "deadline"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "e.g. Finish university project", "class": "field"}),
            "icon": forms.TextInput(attrs={"placeholder": "🎯", "class": "field", "maxlength": 4}),
            "category": forms.Select(attrs={"class": "field"}),
            "description": forms.Textarea(attrs={"rows": 3, "class": "field"}),
            "deadline": forms.DateInput(attrs={"type": "date", "class": "field"}),
        }


MilestoneFormSet = inlineformset_factory(
    Goal, Milestone, fields=["title"], extra=3, can_delete=True,
    widgets={"title": forms.TextInput(attrs={"placeholder": "Milestone", "class": "field"})},
)
