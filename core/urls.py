from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("calendar/", views.calendar_view, name="calendar"),
    path("notifications/data/", views.notifications_data, name="notifications_data"),
]
