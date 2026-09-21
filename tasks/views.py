from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import TaskForm
from .models import Task


@login_required
def task_list(request):
    tab = request.GET.get("tab", "today")
    qs = Task.objects.filter(user=request.user)
    today = timezone.localdate()

    if tab == "today":
        qs = qs.filter(due_date=today, is_completed=False)
    elif tab == "upcoming":
        qs = qs.filter(due_date__gt=today, is_completed=False)
    elif tab == "completed":
        qs = qs.filter(is_completed=True)
    # "all" -> no extra filter

    priority = request.GET.get("priority")
    category = request.GET.get("category")
    search = request.GET.get("q")
    if priority:
        qs = qs.filter(priority=priority)
    if category:
        qs = qs.filter(category=category)
    if search:
        qs = qs.filter(title__icontains=search)

    if request.method == "POST":
        form = TaskForm(request.POST, user=request.user)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            messages.success(request, "Task created.")
            return redirect("tasks:list")
    else:
        form = TaskForm(user=request.user)

    return render(request, "tasks/list.html", {
        "tasks": qs,
        "tab": tab,
        "form": form,
        "priority_choices": Task.PRIORITY_CHOICES,
        "category_choices": Task.CATEGORY_CHOICES,
    })


@login_required
@require_POST
def toggle_task(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    task.mark_completed(not task.is_completed)
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "is_completed": task.is_completed})
    return redirect(request.META.get("HTTP_REFERER", "tasks:list"))


@login_required
@require_POST
def delete_task(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    task.delete()
    messages.success(request, "Task deleted.")
    return redirect(request.META.get("HTTP_REFERER", "tasks:list"))
