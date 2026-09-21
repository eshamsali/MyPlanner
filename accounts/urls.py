from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.PlannerLoginView.as_view(), name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile_view, name="profile"),
    path("settings/", views.settings_view, name="settings"),
    path("preference/", views.set_preference, name="set_preference"),
    path("push/subscribe/", views.push_subscribe, name="push_subscribe"),
    path("push/unsubscribe/", views.push_unsubscribe, name="push_unsubscribe"),
]
