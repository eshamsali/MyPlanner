from django.urls import path
from . import views

app_name = "schedule"

urlpatterns = [
    path("", views.schedule_list, name="list"),
    path("<int:pk>/edit/", views.appointment_edit, name="edit"),
    path("<int:pk>/delete/", views.appointment_delete, name="delete"),
    path("<int:pk>/toggle-active/", views.appointment_toggle_active, name="toggle_active"),
]
