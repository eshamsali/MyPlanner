from django.urls import path
from . import views

app_name = "goals"

urlpatterns = [
    path("", views.goal_list, name="list"),
    path("<int:pk>/", views.goal_detail, name="detail"),
    path("milestone/<int:pk>/toggle/", views.toggle_milestone, name="toggle_milestone"),
    path("<int:pk>/toggle-achieved/", views.toggle_achieved, name="toggle_achieved"),
]
