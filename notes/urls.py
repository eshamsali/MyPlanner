from django.urls import path
from . import views

app_name = "notes"

urlpatterns = [
    path("", views.note_list, name="list"),
    path("new/", views.note_edit, name="new"),
    path("<int:pk>/", views.note_edit, name="edit"),
    path("<int:pk>/delete/", views.note_delete, name="delete"),
]
