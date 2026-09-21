import json

from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from goals.models import Goal
from habits.models import HabitLog
from journal.models import JournalEntry
from tasks.models import Task

from .forms import (
    AppearanceForm, NotificationSettingsForm, PlannerSettingsForm,
    ProfileEditForm, SignUpForm,
)
from .models import PushSubscription


class PlannerLoginView(LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True


def signup_view(request):
    if request.user.is_authenticated:
        return redirect("core:dashboard")
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Welcome to My Planner.")
            return redirect("core:dashboard")
    else:
        form = SignUpForm()
    return render(request, "accounts/signup.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("accounts:login")


@login_required
def profile_view(request):
    profile = request.user.profile
    stats = {
        "tasks_completed": Task.objects.filter(user=request.user, is_completed=True).count(),
        "habits_completed": HabitLog.objects.filter(habit__user=request.user, completed=True).count(),
        "goals_achieved": Goal.objects.filter(user=request.user, is_achieved=True).count(),
        "journal_entries": JournalEntry.objects.filter(user=request.user).count(),
    }
    if request.method == "POST":
        form = ProfileEditForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect("accounts:profile")
    else:
        form = ProfileEditForm(instance=profile, user=request.user)
    return render(request, "accounts/profile.html", {"form": form, "stats": stats})


@require_POST
def set_preference(request):
    """Instant theme/language toggle from the topbar/sidebar — persists immediately,
    without requiring a visit to the full Settings page."""
    theme = request.POST.get("theme")
    language = request.POST.get("language")

    if request.user.is_authenticated:
        profile = request.user.profile
        changed = []
        if theme in ("light", "dark"):
            profile.theme = theme
            changed.append("theme")
        if language in ("en", "ar"):
            profile.language = language
            changed.append("language")
        if changed:
            profile.save(update_fields=changed)
    else:
        if theme in ("light", "dark"):
            request.session["theme"] = theme
        if language in ("en", "ar"):
            request.session["lang"] = language

    return JsonResponse({"ok": True, "theme": theme, "language": language})


@login_required
def settings_view(request):
    profile = request.user.profile
    appearance_form = AppearanceForm(instance=profile)
    planner_form = PlannerSettingsForm(instance=profile)
    notif_form = NotificationSettingsForm(instance=profile)

    if request.method == "POST":
        section = request.POST.get("section")
        if section == "appearance":
            appearance_form = AppearanceForm(request.POST, instance=profile)
            if appearance_form.is_valid():
                appearance_form.save()
                messages.success(request, "Appearance saved.")
                return redirect("accounts:settings")
        elif section == "planner":
            planner_form = PlannerSettingsForm(request.POST, instance=profile)
            if planner_form.is_valid():
                planner_form.save()
                messages.success(request, "Planner settings saved.")
                return redirect("accounts:settings")
        elif section == "notifications":
            notif_form = NotificationSettingsForm(request.POST, instance=profile)
            if notif_form.is_valid():
                notif_form.save()
                messages.success(request, "Notification settings saved.")
                return redirect("accounts:settings")

    return render(request, "accounts/settings.html", {
        "appearance_form": appearance_form,
        "planner_form": planner_form,
        "notif_form": notif_form,
    })


@login_required
@require_POST
def push_subscribe(request):
    """Called by the browser's PushManager.subscribe() result — saves the
    endpoint + keys so send_due_reminders can push to this device later."""
    try:
        data = json.loads(request.body.decode("utf-8"))
        endpoint = data["endpoint"]
        keys = data["keys"]
        p256dh = keys["p256dh"]
        auth = keys["auth"]
    except (ValueError, KeyError, TypeError):
        return JsonResponse({"ok": False, "error": "Invalid subscription payload."}, status=400)

    PushSubscription.objects.update_or_create(
        endpoint=endpoint,
        defaults={"user": request.user, "p256dh": p256dh, "auth": auth},
    )
    return JsonResponse({"ok": True})


@login_required
@require_POST
def push_unsubscribe(request):
    endpoint = request.POST.get("endpoint")
    if endpoint:
        PushSubscription.objects.filter(user=request.user, endpoint=endpoint).delete()
    return JsonResponse({"ok": True})
