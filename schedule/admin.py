from django.contrib import admin
from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "weekday", "start_time", "end_time", "is_active")
    list_filter = ("weekday", "category", "is_active")
    search_fields = ("title", "location")
