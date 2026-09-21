from django.conf import settings
from django.db import models


class Goal(models.Model):
    CATEGORY_CHOICES = [
        ("university", "University"),
        ("work", "Work"),
        ("personal", "Personal"),
        ("health", "Health"),
        ("finance", "Finance"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="goals")
    name = models.CharField(max_length=180)
    icon = models.CharField(max_length=10, default="🎯")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="personal")
    description = models.TextField(blank=True)
    deadline = models.DateField(null=True, blank=True)
    is_achieved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["deadline", "-created_at"]

    def __str__(self):
        return self.name

    @property
    def progress_pct(self):
        total = self.milestones.count()
        if not total:
            return 0
        done = self.milestones.filter(is_completed=True).count()
        return round((done / total) * 100)

    @property
    def milestones_remaining(self):
        return self.milestones.filter(is_completed=False).count()


class Milestone(models.Model):
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name="milestones")
    title = models.CharField(max_length=200)
    is_completed = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.title
