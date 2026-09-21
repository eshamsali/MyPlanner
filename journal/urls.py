from django.urls import path
from . import views

app_name = "journal"

urlpatterns = [
    path("", views.journal_view, name="entry"),
    path("autosave/", views.autosave_field, name="autosave"),
    path("insights/", views.journal_insights, name="insights"),
]
