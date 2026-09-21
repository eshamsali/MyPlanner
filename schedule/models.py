from django.conf import settings
from django.db import models


class Appointment(models.Model):
    """A FIXED, recurring weekly appointment (e.g. a class, a shift, a
    standing meeting) — not a one-off Task. It doesn't live on a specific
    calendar date; instead it recurs every week on `weekday`, and the
    calendar view projects it onto every matching date automatically.
    Editable/deletable at any time from the schedule page.
    """

    CATEGORY_CHOICES = [
        ("university", "University"),
        ("work", "Work"),
        ("personal", "Personal"),
        ("health", "Health"),
        ("other", "Other"),
    ]
    WEEKDAY_CHOICES = [
        (0, "Monday"),
        (1, "Tuesday"),
        (2, "Wednesday"),
        (3, "Thursday"),
        (4, "Friday"),
        (5, "Saturday"),
        (6, "Sunday"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="appointments")
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="personal")
    weekday = models.PositiveSmallIntegerField(choices=WEEKDAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField(null=True, blank=True)
    location = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["weekday", "start_time"]

    def __str__(self):
        return f"{self.title} — {self.get_weekday_display()} {self.start_time}"
