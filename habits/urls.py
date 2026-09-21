from django.urls import path
from . import views

app_name = "habits"

urlpatterns = [
    path("", views.habit_list, name="list"),
    path("<int:pk>/", views.habit_detail, name="detail"),
    path("<int:pk>/toggle-today/", views.toggle_habit_today, name="toggle_today"),
    path("<int:pk>/toggle-day/", views.toggle_habit_day, name="toggle_day"),
    path("<int:pk>/toggle-active/", views.toggle_habit_active, name="toggle_active"),
]
