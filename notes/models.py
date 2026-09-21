from django.conf import settings
from django.db import models


class NoteFolder(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="note_folders")
    name = models.CharField(max_length=80)

    class Meta:
        ordering = ["name"]
        unique_together = ("user", "name")

    def __str__(self):
        return self.name


class Note(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notes")
    folder = models.ForeignKey(NoteFolder, on_delete=models.SET_NULL, null=True, blank=True, related_name="notes")
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return self.title

    @property
    def preview(self):
        return (self.content[:120] + "…") if len(self.content) > 120 else self.content
