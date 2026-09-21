from django.contrib import admin
from .models import Goal, Milestone


class MilestoneInline(admin.TabularInline):
    model = Milestone
    extra = 1


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "category", "deadline", "is_achieved")
    list_filter = ("category", "is_achieved")
    inlines = [MilestoneInline]
