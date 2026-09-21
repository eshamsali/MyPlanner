import datetime
import json

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import PushSubscription
from habits.models import Habit, HabitLog
from tasks.models import Task

try:
    from pywebpush import webpush, WebPushException
except ImportError:
    webpush = None

    class WebPushException(Exception):
        pass


def send_push(user, title, body, url="/"):
    """Sends a real OS-level push notification (via the browser's push
    service) to every device this user has subscribed on. Requires
    `pip install pywebpush` and VAPID_PRIVATE_KEY_PATH / VAPID_ADMIN_EMAIL
    configured in settings.py (see README section added for this feature)."""
    if webpush is None:
        return
    payload = json.dumps({"title": title, "body": body, "url": url})
    for sub in PushSubscription.objects.filter(user=user):
        try:
            webpush(
                subscription_info={
                    "endpoint": sub.endpoint,
                    "keys": {"p256dh": sub.p256dh, "auth": sub.auth},
                },
                data=payload,
                vapid_private_key=settings.VAPID_PRIVATE_KEY_PATH,
                vapid_claims={"sub": settings.VAPID_ADMIN_EMAIL},
            )
        except WebPushException as e:
            status = getattr(getattr(e, "response", None), "status_code", None)
            if status in (404, 410):
                # Subscription is gone (browser data cleared, app uninstalled, etc.)
                sub.delete()


class Command(BaseCommand):
    help = (
        "Sends due task/habit reminders as real OS push notifications. "
        "Meant to run every minute — e.g. a Windows Task Scheduler entry running "
        "`python manage.py send_due_reminders`, or cron on other OSes."
    )

    def handle(self, *args, **options):
        now = timezone.localtime()
        today = now.date()

        # --- Task reminders: fire once, exactly when "start time minus
        # reminder minutes" has passed, for tasks that haven't fired yet. ---
        due_tasks = Task.objects.filter(
            due_date=today,
            is_completed=False,
            reminder_sent_at__isnull=True,
            reminder_minutes_before__isnull=False,
            start_time__isnull=False,
        ).select_related("user")

        for task in due_tasks:
            profile = getattr(task.user, "profile", None)
            if profile and not profile.task_reminders:
                continue
            naive_remind_at = datetime.datetime.combine(today, task.start_time) - datetime.timedelta(
                minutes=task.reminder_minutes_before
            )
            remind_at = timezone.make_aware(naive_remind_at, now.tzinfo) if timezone.is_naive(naive_remind_at) else naive_remind_at
            if remind_at <= now:
                send_push(
                    task.user,
                    f"⏰ {task.title}",
                    f"Starts at {task.start_time.strftime('%I:%M %p')}",
                    url="/tasks/",
                )
                task.reminder_sent_at = now
                task.save(update_fields=["reminder_sent_at"])
                self.stdout.write(f"Sent task reminder: {task.title} ({task.user})")

        # --- Habit reminders: fire once per day, in the minute matching
        # reminder_time, for habits due today that aren't completed yet. ---
        due_habits = Habit.objects.filter(
            is_active=True, reminder_time__isnull=False,
        ).exclude(last_reminder_sent_date=today).select_related("user")

        for habit in due_habits:
            if not habit.is_due_on(today):
                continue
            if habit.reminder_time > now.time():
                continue
            profile = getattr(habit.user, "profile", None)
            if profile and not profile.habit_reminders:
                continue

            already_done = HabitLog.objects.filter(habit=habit, date=today, completed=True).exists()
            habit.last_reminder_sent_date = today
            habit.save(update_fields=["last_reminder_sent_date"])
            if already_done:
                continue

            send_push(habit.user, f"🔁 {habit.name}", "Don't forget today's habit.", url="/habits/")
            self.stdout.write(f"Sent habit reminder: {habit.name} ({habit.user})")
