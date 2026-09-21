from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "theme", "accent_color", "week_start")
    list_filter = ("theme", "accent_color")
