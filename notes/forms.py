from django import forms
from .models import Note


class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ["title", "content", "folder"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Untitled note", "class": "field"}),
            "content": forms.Textarea(attrs={"rows": 14, "placeholder": "Start writing...", "class": "field note-body"}),
            "folder": forms.Select(attrs={"class": "field"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.fields["folder"].required = False
        if user is not None:
            self.fields["folder"].queryset = self.fields["folder"].queryset.filter(user=user)
