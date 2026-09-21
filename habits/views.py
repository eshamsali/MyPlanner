import datetime

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import HabitForm
from .models import Habit, HabitLog


def _start_of_week(date):
    return date - datetime.timedelta(days=date.weekday())  # Monday start


@login_required
def habit_list(request):
    habits = Habit.objects.filter(user=request.user, is_active=True)
    today = timezone.localdate()
    start = _start_of_week(today)

    habit_rows = []
    for habit in habits:
        bools = habit.logs_for_week(start)
        # Real dates for each column so every dot can be clicked/toggled
        # individually (not just "today"), and so we know which days are
        # actually due for "Specific days" habits.
        day_cells = [
            {
                "date": start + datetime.timedelta(days=i),
                "done": bools[i],
                "is_today": (start + datetime.timedelta(days=i)) == today,
                "is_due": habit.is_due_on(start + datetime.timedelta(days=i)),
            }
            for i in range(7)
        ]
        habit_rows.append({
            "habit": habit,
            "days": bools,
            "day_cells": day_cells,
            "streak": habit.current_streak,
        })

    if request.method == "POST":
        form = HabitForm(request.POST)
        if form.is_valid():
            habit = form.save(commit=False)
            habit.user = request.user
            habit.save()
            messages.success(request, "Habit created.")
            return redirect("habits:list")
    else:
        form = HabitForm()

    total_habits = habits.count() or 1
    week_total = sum(sum(row["days"]) for row in habit_rows)
    week_pct = round((week_total / (total_habits * 7)) * 100) if total_habits else 0

    return render(request, "habits/list.html", {
        "habit_rows": habit_rows,
        "form": form,
        "today_index": today.weekday(),
        "week_pct": week_pct,
        "longest_streak": max([row["streak"] for row in habit_rows], default=0),
    })


@login_required
def habit_detail(request, pk):
    habit = get_object_or_404(Habit, pk=pk, user=request.user)
    today = timezone.localdate()
    month_start = today.replace(day=1)
    logs = habit.logs.filter(date__gte=month_start).order_by("date")
    return render(request, "habits/detail.html", {
        "habit": habit,
        "logs": logs,
        "completion_rate": habit.completion_rate(),
    })


@login_required
@require_POST
def toggle_habit_today(request, pk):
    habit = get_object_or_404(Habit, pk=pk, user=request.user)
    today = timezone.localdate()
    log, _ = HabitLog.objects.get_or_create(habit=habit, date=today)
    log.completed = not log.completed
    log.save()
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "completed": log.completed})
    return redirect(request.META.get("HTTP_REFERER", "habits:list"))


@login_required
@require_POST
def toggle_habit_day(request, pk):
    """Like toggle_habit_today, but for an arbitrary date — this is what
    lets you mark any day of the week grid as done, not just today."""
    habit = get_object_or_404(Habit, pk=pk, user=request.user)
    date_str = request.POST.get("date")
    try:
        date = datetime.date.fromisoformat(date_str)
    except (TypeError, ValueError):
        return JsonResponse({"ok": False, "error": "Invalid date."}, status=400)

    log, _ = HabitLog.objects.get_or_create(habit=habit, date=date)
    log.completed = not log.completed
    log.save()
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "completed": log.completed, "date": date_str})
    return redirect(request.META.get("HTTP_REFERER", "habits:list"))


@login_required
@require_POST
def toggle_habit_active(request, pk):
    """Mark a habit as complete by archiving it (is_active=False). Un-archiving
    brings it back into the active weekly grid."""
    habit = get_object_or_404(Habit, pk=pk, user=request.user)
    habit.is_active = not habit.is_active
    habit.save(update_fields=["is_active"])
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "is_active": habit.is_active})
    return redirect("habits:list")
