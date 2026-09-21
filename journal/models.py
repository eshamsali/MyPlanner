from django.conf import settings
from django.db import models
from django.utils import timezone


class JournalEntry(models.Model):
    MOOD_CHOICES = [
        ("great", "😍"),
        ("good", "😊"),
        ("okay", "😐"),
        ("low", "😔"),
        ("rough", "😭"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="journal_entries")
    date = models.DateField(default=timezone.localdate)
    mood = models.CharField(max_length=10, choices=MOOD_CHOICES, blank=True)
    highlights = models.TextField(blank=True)
    gratitude = models.TextField(blank=True)
    reflection = models.TextField(blank=True)
    tomorrow = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "date")
        ordering = ["-date"]

    def __str__(self):
        return f"{self.user} — {self.date}"
