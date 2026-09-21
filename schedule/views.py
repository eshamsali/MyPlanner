from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import AppointmentForm
from .models import Appointment


@login_required
def schedule_list(request):
    appointments = Appointment.objects.filter(user=request.user, is_active=True)

    by_day = {i: [] for i in range(7)}
    for appt in appointments:
        by_day[appt.weekday].append(appt)

    if request.method == "POST":
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appt = form.save(commit=False)
            appt.user = request.user
            appt.save()
            messages.success(request, "Appointment added — it will now show up on your calendar every week.")
            return redirect("schedule:list")
    else:
        form = AppointmentForm()

    return render(request, "schedule/list.html", {
        "by_day": by_day,
        "form": form,
        "weekday_choices": Appointment.WEEKDAY_CHOICES,
        "total_count": appointments.count(),
    })


@login_required
def appointment_edit(request, pk):
    appt = get_object_or_404(Appointment, pk=pk, user=request.user)
    if request.method == "POST":
        form = AppointmentForm(request.POST, instance=appt)
        if form.is_valid():
            form.save()
            messages.success(request, "Appointment updated.")
            return redirect("schedule:list")
    else:
        form = AppointmentForm(instance=appt)
    return render(request, "schedule/edit.html", {"form": form, "appointment": appt})


@login_required
@require_POST
def appointment_delete(request, pk):
    appt = get_object_or_404(Appointment, pk=pk, user=request.user)
    appt.delete()
    messages.success(request, "Appointment deleted.")
    return redirect(request.META.get("HTTP_REFERER", "schedule:list") or "schedule:list")


@login_required
@require_POST
def appointment_toggle_active(request, pk):
    """Pause/resume an appointment without deleting its history — a paused
    appointment stops showing up on the calendar."""
    appt = get_object_or_404(Appointment, pk=pk, user=request.user)
    appt.is_active = not appt.is_active
    appt.save(update_fields=["is_active"])
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "is_active": appt.is_active})
    return redirect("schedule:list")
