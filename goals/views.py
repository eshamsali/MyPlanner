from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from tasks.models import Task

from .forms import GoalForm, MilestoneFormSet
from .models import Goal, Milestone


@login_required
def goal_list(request):
    goals = Goal.objects.filter(user=request.user)

    if request.method == "POST":
        form = GoalForm(request.POST)
        formset = MilestoneFormSet(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            formset = MilestoneFormSet(request.POST, instance=goal)
            if formset.is_valid():
                formset.save()
            messages.success(request, "Goal created.")
            return redirect("goals:list")
    else:
        form = GoalForm()
        formset = MilestoneFormSet()

    return render(request, "goals/list.html", {"goals": goals, "form": form, "formset": formset})


@login_required
def goal_detail(request, pk):
    goal = get_object_or_404(Goal, pk=pk, user=request.user)
    related_tasks = Task.objects.filter(goal=goal)
    return render(request, "goals/detail.html", {"goal": goal, "related_tasks": related_tasks})


@login_required
@require_POST
def toggle_milestone(request, pk):
    milestone = get_object_or_404(Milestone, pk=pk, goal__user=request.user)
    milestone.is_completed = not milestone.is_completed
    milestone.save()
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({
            "ok": True,
            "is_completed": milestone.is_completed,
            "goal_progress": milestone.goal.progress_pct,
        })
    return redirect("goals:detail", pk=milestone.goal.pk)


@login_required
@require_POST
def toggle_achieved(request, pk):
    goal = get_object_or_404(Goal, pk=pk, user=request.user)
    goal.is_achieved = not goal.is_achieved
    goal.save(update_fields=["is_achieved"])
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "is_achieved": goal.is_achieved})
    return redirect("goals:detail", pk=goal.pk)
