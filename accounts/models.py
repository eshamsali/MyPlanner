from django.conf import settings
from django.db import models


class Profile(models.Model):
    ACCENT_CHOICES = [
        ("purple", "Purple"),
        ("pink", "Pink"),
        ("blue", "Blue"),
        ("green", "Green"),
        ("orange", "Orange"),
    ]
    THEME_CHOICES = [
        ("light", "Light"),
        ("dark", "Dark"),
        ("system", "System"),
    ]
    WEEK_START_CHOICES = [
        ("mon", "Monday"),
        ("sat", "Saturday"),
        ("sun", "Sunday"),
    ]
    LANGUAGE_CHOICES = [
        ("en", "English"),
        ("ar", "العربية"),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    theme = models.CharField(max_length=10, choices=THEME_CHOICES, default="light")
    accent_color = models.CharField(max_length=10, choices=ACCENT_CHOICES, default="purple")
    language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default="en")
    font_size = models.CharField(
        max_length=10,
        choices=[("small", "Small"), ("medium", "Medium"), ("large", "Large")],
        default="medium",
    )
    week_start = models.CharField(max_length=3, choices=WEEK_START_CHOICES, default="mon")
    time_format_24h = models.BooleanField(default=False)
    task_reminders = models.BooleanField(default=True)
    habit_reminders = models.BooleanField(default=True)
    goal_reminders = models.BooleanField(default=True)
    daily_planning_reminder = models.BooleanField(default=True)

    def __str__(self):
        return f"Profile<{self.user.username}>"

    @property
    def initials(self):
        name = self.user.get_full_name() or self.user.username
        parts = name.split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[1][0]).upper()
        return name[:2].upper()


class PushSubscription(models.Model):
    """One row per browser/device the user has enabled real push
    notifications on (Web Push API). Populated by the JS in
    initPushNotifications() -> POST /accounts/push/subscribe/, and consumed
    by the `send_due_reminders` management command."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="push_subscriptions")
    endpoint = models.URLField(max_length=500, unique=True)
    p256dh = models.CharField(max_length=255)
    auth = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"PushSubscription<{self.user.username}>"
