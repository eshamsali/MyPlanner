import datetime

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_POST

from habits.models import HabitLog
from tasks.models import Task

from .forms import JournalEntryForm
from .models import JournalEntry

MOOD_SCORES = {"great": 5, "good": 4, "okay": 3, "low": 2, "rough": 1}

# Rule-based "recommendation engine" — no external AI call, just simple
# statistics over the user's own mood/task/habit history. Kept bilingual so
# the report respects the profile language like everything else in the app.
RECOMMENDATIONS = {
    "declining": {
        "en": "Your mood has been trending down recently. Consider lightening your task load for a few days, and make time for something that usually lifts your mood.",
        "ar": "مزاجك في تراجع خلال الفترة الأخيرة. جرّبي تخفّفي حِمل المهام لبضعة أيام، وخصّصي وقت لحاجة بتحسّسك بتحسّن.",
    },
    "improving": {
        "en": "Your mood has been trending up recently — whatever you've been doing seems to be working. Keep an eye on what changed.",
        "ar": "مزاجك بيتحسّن في الفترة الأخيرة — اللي بتعمليه شكله شغّال. حاولي تلاحظي إيه اللي اتغيّر عشان تكمّلي عليه.",
    },
    "task_overload": {
        "en": "On days you finish an unusually high number of tasks, your mood tends to be lower. You might be overloading your schedule — try spacing tasks out a bit more.",
        "ar": "في الأيام اللي بتخلّصي فيها عدد مهام كبير جدًا، مزاجك بيميل يكون أقل. ممكن تكوني محمّلة جدولك أكتر من اللازم — جرّبي توزّعي المهام أكتر.",
    },
    "task_positive": {
        "en": "Completing your tasks tends to go hand-in-hand with a better mood for you — a good reason to keep your daily task list realistic and achievable.",
        "ar": "إنجاز مهامك بيترافق غالبًا مع مزاج أحسن — سبب كويس إنك تخلّي قائمة مهامك اليومية واقعية وقابلة للتحقيق.",
    },
    "habit_positive": {
        "en": "Days you complete more of your habits tend to have a better mood — a nice reminder that small consistent habits pay off emotionally too.",
        "ar": "الأيام اللي بتخلّصي فيها عادات أكتر بيبقى مزاجك فيها أحسن — تذكير إن الاستمرارية في العادات بتفرق نفسيًا كمان.",
    },
    "low_avg": {
        "en": "Your average mood over this period has been on the lower side. If this continues, it might help to talk to someone you trust or a professional.",
        "ar": "متوسط مزاجك خلال الفترة دي كان مايل للانخفاض. لو الموضوع مستمر، ممكن يفيدك تتكلمي مع حد تثقي فيه أو مختص.",
    },
    "default": {
        "en": "Not enough entries yet to spot a clear pattern — keep journaling daily and check back after a couple of weeks.",
        "ar": "لسّه مفيش تدوينات كفاية عشان نلاحظ نمط واضح — استمري في الكتابة يوميًا وارجعي شوفي التقرير بعد أسبوعين.",
    },
}


def _rec(key, lang):
    bucket = RECOMMENDATIONS.get(key, RECOMMENDATIONS["default"])
    return bucket.get(lang, bucket["en"])


def compute_insights(user, days=30, lang="en"):
    """Rule-based mood analysis: trend over time, plus simple correlations
    against that day's task/habit completion rate. This runs entirely on the
    user's own data already in the database — no external API call."""
    since = timezone.localdate() - datetime.timedelta(days=days)
    entries = list(JournalEntry.objects.filter(user=user, date__gte=since).order_by("date"))

    mood_series = [
        {"date": e.date, "score": MOOD_SCORES.get(e.mood, 3), "mood": e.mood}
        for e in entries if e.mood
    ]
    count = len(mood_series)
    avg_mood = round(sum(m["score"] for m in mood_series) / count, 2) if count else None

    trend = "stable"
    if count >= 4:
        half = count // 2
        first_avg = sum(m["score"] for m in mood_series[:half]) / half
        second_avg = sum(m["score"] for m in mood_series[half:]) / (count - half)
        diff = second_avg - first_avg
        if diff >= 0.4:
            trend = "improving"
        elif diff <= -0.4:
            trend = "declining"

    # Mood vs. that day's task-completion rate
    task_pairs = []
    for m in mood_series:
        day_tasks = Task.objects.filter(user=user, due_date=m["date"])
        total = day_tasks.count()
        if total:
            task_pairs.append((m["score"], day_tasks.filter(is_completed=True).count() / total))

    task_insight = None
    high = [s for s, r in task_pairs if r >= 0.7]
    low = [s for s, r in task_pairs if r < 0.3]
    if high and low:
        high_avg, low_avg = sum(high) / len(high), sum(low) / len(low)
        if high_avg - low_avg >= 0.5:
            task_insight = "task_positive"
        elif low_avg - high_avg >= 0.5:
            task_insight = "task_overload"

    # Mood vs. that day's habit-completion rate
    habit_pairs = []
    for m in mood_series:
        day_logs = HabitLog.objects.filter(habit__user=user, date=m["date"])
        total = day_logs.count()
        if total:
            habit_pairs.append((m["score"], day_logs.filter(completed=True).count() / total))

    habit_insight = None
    high_h = [s for s, r in habit_pairs if r >= 0.7]
    low_h = [s for s, r in habit_pairs if r < 0.3]
    if high_h and low_h and (sum(high_h) / len(high_h)) - (sum(low_h) / len(low_h)) >= 0.5:
        habit_insight = "habit_positive"

    recommendations = []
    if trend == "declining":
        recommendations.append(_rec("declining", lang))
    elif trend == "improving":
        recommendations.append(_rec("improving", lang))
    if task_insight:
        recommendations.append(_rec(task_insight, lang))
    if habit_insight:
        recommendations.append(_rec(habit_insight, lang))
    if avg_mood is not None and avg_mood <= 2.5:
        recommendations.append(_rec("low_avg", lang))
    if not recommendations:
        recommendations.append(_rec("default", lang))

    return {
        "avg_mood": avg_mood,
        "mood_count": count,
        "trend": trend,
        "mood_series": mood_series,
        "recommendations": recommendations,
        "days": days,
    }


@login_required
def journal_view(request):
    date_str = request.GET.get("date")
    date = datetime.date.fromisoformat(date_str) if date_str else timezone.localdate()

    entry, _ = JournalEntry.objects.get_or_create(user=request.user, date=date)

    if request.method == "POST":
        form = JournalEntryForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"ok": True, "saved_at": timezone.localtime().strftime("%I:%M %p")})
    else:
        form = JournalEntryForm(instance=entry)

    return render(request, "journal/entry.html", {
        "form": form, "date": date, "entry": entry,
        "mood_choices": JournalEntry.MOOD_CHOICES,
    })


@login_required
@require_POST
def autosave_field(request):
    """Autosave a single journal field via fetch() as the user types."""
    date_str = request.POST.get("date")
    field = request.POST.get("field")
    value = request.POST.get("value", "")
    allowed_fields = {"highlights", "gratitude", "reflection", "tomorrow", "mood"}
    if field not in allowed_fields:
        return JsonResponse({"ok": False, "error": "Invalid field."}, status=400)

    date = datetime.date.fromisoformat(date_str) if date_str else timezone.localdate()
    entry, _ = JournalEntry.objects.get_or_create(user=request.user, date=date)
    setattr(entry, field, value)
    entry.save(update_fields=[field, "updated_at"])
    return JsonResponse({"ok": True, "saved_at": timezone.localtime().strftime("%I:%M %p")})


@login_required
def journal_insights(request):
    """The mood-impact report: trend + rule-based recommendations."""
    days = 90 if request.GET.get("days") == "90" else 30
    lang = getattr(getattr(request.user, "profile", None), "language", "en")
    insights = compute_insights(request.user, days=days, lang=lang)
    return render(request, "journal/insights.html", {"insights": insights, "days": days})
