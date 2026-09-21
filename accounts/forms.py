from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Profile


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True, label="Name")

    class Meta:
        model = User
        fields = ("first_name", "email", "username", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.update({"class": "field"})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        if commit:
            user.save()
        return user


class ProfileEditForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, required=True, label="Name")
    email = forms.EmailField(required=True)

    class Meta:
        model = Profile
        fields = ("avatar",)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        self.fields["first_name"].initial = self.user.first_name
        self.fields["email"].initial = self.user.email
        # NOTE: these three fields previously had no widget/class set at all,
        # so they rendered with plain unstyled browser inputs whose text
        # color didn't follow the app's theme (looked fine in light mode,
        # unreadable in dark mode). Give them the same "field" styling as
        # every other input, and a dedicated class for the file input.
        self.fields["first_name"].widget.attrs.update({"class": "field", "placeholder": "Your name"})
        self.fields["email"].widget.attrs.update({"class": "field", "placeholder": "you@example.com"})
        self.fields["avatar"].widget.attrs.update({"class": "field-file"})

    def save(self, commit=True):
        profile = super().save(commit=False)
        self.user.first_name = self.cleaned_data["first_name"]
        self.user.email = self.cleaned_data["email"]
        if commit:
            self.user.save()
            profile.save()
        return profile


class AppearanceForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("theme", "accent_color", "font_size", "language")


class PlannerSettingsForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("week_start", "time_format_24h")


class NotificationSettingsForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("task_reminders", "habit_reminders", "goal_reminders", "daily_planning_reminder")
