from django import forms
from .models import JournalEntry


class JournalEntryForm(forms.ModelForm):
    class Meta:
        model = JournalEntry
        fields = ["mood", "highlights", "gratitude", "reflection", "tomorrow"]
        widgets = {
            "mood": forms.RadioSelect(),
            "highlights": forms.Textarea(attrs={"rows": 3, "placeholder": "What made today worth remembering?", "class": "field journal-field"}),
            "gratitude": forms.Textarea(attrs={"rows": 3, "placeholder": "I'm grateful for...", "class": "field journal-field"}),
            "reflection": forms.Textarea(attrs={"rows": 3, "placeholder": "How was your day?", "class": "field journal-field"}),
            "tomorrow": forms.Textarea(attrs={"rows": 3, "placeholder": "What do I want to accomplish tomorrow?", "class": "field journal-field"}),
        }
