from django.conf import settings
from django.utils import timezone

from core.translations import get_translations


def planner_context(request):
    """Data every template needs: today's date, translations, and (if logged in) the profile."""
    if request.user.is_authenticated and hasattr(request.user, "profile"):
        lang = request.user.profile.language
    else:
        lang = request.session.get("lang", "en")

    ctx = {
        "today": timezone.localdate(),
        "lang": lang,
        "is_rtl": lang == "ar",
        "T": get_translations(lang),
        # Needed by app.js's initPushNotifications() to call
        # pushManager.subscribe({ applicationServerKey: ... }).
        "VAPID_PUBLIC_KEY": getattr(settings, "VAPID_PUBLIC_KEY", ""),
    }
    if request.user.is_authenticated:
        ctx["profile"] = getattr(request.user, "profile", None)
    return ctx
