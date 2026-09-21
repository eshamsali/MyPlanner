import datetime

from django.conf import settings
from django.db import models
from django.utils import timezone


class Habit(models.Model):
    FREQUENCY_CHOICES = [
        ("daily", "Every day"),
        ("weekdays", "Weekdays"),
        ("weekly", "Specific days"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="habits")
    name = models.CharField(max_length=120)
    icon = models.CharField(max_length=40, default="droplet", help_text="Icon key used by the template")
    color = models.CharField(max_length=20, default="accent")
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES, default="daily")
    # Only meaningful when frequency == "weekly". Comma-separated weekday
    # numbers, Monday=0 .. Sunday=6, e.g. "0,2,4" for Mon/Wed/Fri.
    active_days = models.CharField(
        max_length=20, blank=True, default="",
        help_text="Comma-separated weekday numbers (0=Mon..6=Sun), used when frequency='weekly'",
    )
    goal_per_day = models.PositiveIntegerField(default=1, help_text="e.g. glasses of water")
    reminder_time = models.TimeField(null=True, blank=True)
    # Guards against sending the same real push reminder twice in one day;
    # set by the send_due_reminders management command.
    last_reminder_sent_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def active_days_list(self):
        """['0', '2', '4'] -> [0, 2, 4] as ints, empty list if unset."""
        if not self.active_days:
            return []
        return [int(d) for d in self.active_days.split(",") if d != ""]

    def is_due_on(self, date):
        """Whether this habit is expected to be done on the given date,
        based on its frequency setting."""
        weekday = date.weekday()  # Monday=0 .. Sunday=6
        if self.frequency == "daily":
            return True
        if self.frequency == "weekdays":
            return weekday < 5
        if self.frequency == "weekly":
            days = self.active_days_list
            return weekday in days if days else True
        return True

    def logs_for_week(self, start_of_week):
        end_of_week = start_of_week + datetime.timedelta(days=6)
        logs = self.logs.filter(date__range=[start_of_week, end_of_week])
        by_date = {log.date: log.completed for log in logs}
        return [by_date.get(start_of_week + datetime.timedelta(days=i), False) for i in range(7)]

    @property
    def current_streak(self):
        streak = 0
        day = timezone.localdate()
        completed_dates = set(self.logs.filter(completed=True).values_list("date", flat=True))
        while day in completed_dates:
            streak += 1
            day -= datetime.timedelta(days=1)
        return streak

    @property
    def longest_streak(self):
        dates = sorted(self.logs.filter(completed=True).values_list("date", flat=True))
        if not dates:
            return 0
        longest = current = 1
        for i in range(1, len(dates)):
            if (dates[i] - dates[i - 1]).days == 1:
                current += 1
            else:
                current = 1
            longest = max(longest, current)
        return longest

    def completion_rate(self, days=30):
        since = timezone.localdate() - datetime.timedelta(days=days)
        total_logs = self.logs.filter(date__gte=since)
        if not total_logs.exists():
            return 0
        completed = total_logs.filter(completed=True).count()
        return round((completed / days) * 100)


class HabitLog(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name="logs")
    date = models.DateField(default=timezone.localdate)
    completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ("habit", "date")
        ordering = ["-date"]

    def __str__(self):
        return f"{self.habit.name} — {self.date}"
