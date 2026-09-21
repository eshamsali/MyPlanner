from django.contrib import admin
from .models import Note, NoteFolder


@admin.register(NoteFolder)
class NoteFolderAdmin(admin.ModelAdmin):
    list_display = ("name", "user")


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "folder", "updated_at")
    list_filter = ("folder",)
    search_fields = ("title", "content")
