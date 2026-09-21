import calendar as cal_module
import datetime

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils import timezone

from goals.models import Goal
from habits.models import Habit, HabitLog
from journal.models import JournalEntry
from schedule.models import Appointment
from tasks.models import Task


@login_required
def dashboard(request):
    today = timezone.localdate()
    user = request.user

    today_tasks = Task.objects.filter(user=user, due_date=today)
    completed_count = today_tasks.filter(is_completed=True).count()
    total_count = today_tasks.count()
    progress_pct = round((completed_count / total_count) * 100) if total_count else 0

    priority_tasks = today_tasks.filter(is_completed=False).order_by("-priority", "start_time")[:3]

    schedule = today_tasks.exclude(start_time__isnull=True).order_by("start_time")[:6]

    habits = Habit.objects.filter(user=user, is_active=True)[:4]
    habit_rows = []
    for habit in habits:
        log = HabitLog.objects.filter(habit=habit, date=today).first()
        completed = log.completed if log else False
        habit_rows.append({
            "habit": habit,
            "completed": completed,
            "pct": 100 if completed else 0,
        })

    # Previously this only looked at is_achieved=False, so the moment you
    # marked a goal as achieved it just vanished from the dashboard with no
    # confirmation. Now: prefer the nearest active goal, but if every goal
    # is achieved (or there simply isn't an active one), fall back to the
    # most recently achieved goal and show it with an "Achieved" badge.
    top_goal = Goal.objects.filter(user=user).order_by("is_achieved", "deadline", "-created_at").first()

    entry, _ = JournalEntry.objects.get_or_create(user=user, date=today)

    return render(request, "core/dashboard.html", {
        "today_tasks": today_tasks,
        "completed_count": completed_count,
        "total_count": total_count,
        "progress_pct": progress_pct,
        "priority_tasks": priority_tasks,
        "schedule": schedule,
        "habit_rows": habit_rows,
        "top_goal": top_goal,
        "entry": entry,
        "mood_choices": JournalEntry.MOOD_CHOICES,
    })


@login_required
def notifications_data(request):
    """Lightweight in-app notification feed — no browser permission needed,
    just derived from the user's own tasks/habits due today."""
    today = timezone.localdate()
    user = request.user
    items = []

    due_tasks = Task.objects.filter(user=user, due_date=today, is_completed=False).order_by("start_time")[:5]
    for t in due_tasks:
        when = t.start_time.strftime("%I:%M %p").lstrip("0") if t.start_time else None
        items.append({
            "icon": "check-square",
            "text": f"{t.title}" + (f" — {when}" if when else ""),
            "kind": "task",
        })

    active_habits = Habit.objects.filter(user=user, is_active=True)
    for h in active_habits:
        done_today = HabitLog.objects.filter(habit=h, date=today, completed=True).exists()
        if not done_today:
            items.append({"icon": "repeat", "text": h.name, "kind": "habit"})

    return JsonResponse({"ok": True, "items": items[:8]})


@login_required
def calendar_view(request):
    today = timezone.localdate()
    try:
        year = int(request.GET.get("year", today.year))
        month = int(request.GET.get("month", today.month))
        datetime.date(year, month, 1)  # validate
    except (ValueError, TypeError):
        year, month = today.year, today.month

    first_of_month = datetime.date(year, month, 1)
    prev_month = (first_of_month - datetime.timedelta(days=1)).replace(day=1)
    next_month = (first_of_month + datetime.timedelta(days=32)).replace(day=1)

    cal = cal_module.Calendar(firstweekday=0)  # Monday start
    month_days = [d for d in cal.itermonthdates(year, month)]  # includes leading/trailing days
    weeks = [month_days[i:i + 7] for i in range(0, len(month_days), 7)]

    month_tasks = Task.objects.filter(
        user=request.user, due_date__year=year, due_date__month=month,
    )
    tasks_by_day = {}
    for task in month_tasks:
        tasks_by_day.setdefault(task.due_date, []).append(task)

    # Fixed weekly appointments don't live on a specific date — they recur
    # on a weekday. Project the active ones onto every date shown in this
    # month's grid so they show up on the calendar automatically.
    active_appointments = Appointment.objects.filter(user=request.user, is_active=True)
    appointments_by_weekday = {}
    for appt in active_appointments:
        appointments_by_weekday.setdefault(appt.weekday, []).append(appt)

    appointments_by_day = {}
    for day in month_days:
        wd = day.weekday()
        if wd in appointments_by_weekday:
            appointments_by_day[day] = appointments_by_weekday[wd]

    selected_str = request.GET.get("selected")
    if selected_str:
        try:
            selected_date = datetime.date.fromisoformat(selected_str)
        except ValueError:
            selected_date = today
    else:
        selected_date = today

    selected_tasks = Task.objects.filter(user=request.user, due_date=selected_date).order_by(
        "start_time", "-priority"
    )
    selected_appointments = sorted(
        appointments_by_weekday.get(selected_date.weekday(), []),
        key=lambda a: a.start_time,
    )

    return render(request, "core/calendar.html", {
        "weeks": weeks,
        "month_label": first_of_month.strftime("%B %Y"),
        "current_month": month,
        "prev_year": prev_month.year, "prev_month": prev_month.month,
        "next_year": next_month.year, "next_month": next_month.month,
        "tasks_by_day": tasks_by_day,
        "appointments_by_day": appointments_by_day,
        "selected_date": selected_date,
        "selected_tasks": selected_tasks,
        "selected_appointments": selected_appointments,
        "today": today,
        "year": year,
        "month": month,
    })


# ---------------------------------------------------------------------------
# Real push notifications: a tiny service worker served at the SITE ROOT
# (config/urls.py maps "sw.js" -> this view) so its default scope is "/" and
# it can receive pushes for the whole app, not just /core/. Registered by
# initPushNotifications() in app.js.
# ---------------------------------------------------------------------------
SERVICE_WORKER_JS = r"""
self.addEventListener('push', function (event) {
  let data = {};
  try { data = event.data ? event.data.json() : {}; } catch (e) {}
  const title = data.title || 'My Planner';
  const options = {
    body: data.body || '',
    data: { url: data.url || '/' },
  };
  event.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener('notificationclick', function (event) {
  event.notification.close();
  const url = (event.notification.data && event.notification.data.url) || '/';
  event.waitUntil(clients.openWindow(url));
});
"""


def service_worker(request):
    return HttpResponse(SERVICE_WORKER_JS, content_type="application/javascript")
