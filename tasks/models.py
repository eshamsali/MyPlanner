from django.conf import settings
from django.db import models
from django.utils import timezone


class Task(models.Model):
    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
    ]
    CATEGORY_CHOICES = [
        ("university", "University"),
        ("work", "Work"),
        ("personal", "Personal"),
        ("health", "Health"),
        ("other", "Other"),
    ]
    REPEAT_CHOICES = [
        ("none", "Does not repeat"),
        ("daily", "Daily"),
        ("weekly", "Weekly"),
        ("monthly", "Monthly"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tasks")
    goal = models.ForeignKey("goals.Goal", on_delete=models.SET_NULL, null=True, blank=True, related_name="related_tasks")

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="personal")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="medium")

    due_date = models.DateField(default=timezone.localdate)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)

    repeat = models.CharField(max_length=10, choices=REPEAT_CHOICES, default="none")
    reminder_minutes_before = models.PositiveIntegerField(null=True, blank=True, help_text="Minutes before start time")
    # Guards against sending the same real push notification twice for the
    # same task; set by the send_due_reminders management command.
    reminder_sent_at = models.DateTimeField(null=True, blank=True)

    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["due_date", "start_time", "-priority"]

    def __str__(self):
        return self.title

    def mark_completed(self, completed: bool):
        self.is_completed = completed
        self.completed_at = timezone.now() if completed else None
        self.save(update_fields=["is_completed", "completed_at"])
