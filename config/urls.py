from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from core import views as core_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("", include("core.urls")),
    path("tasks/", include("tasks.urls")),
    path("habits/", include("habits.urls")),
    path("goals/", include("goals.urls")),
    path("journal/", include("journal.urls")),
    path("notes/", include("notes.urls")),
    path("schedule/", include("schedule.urls")),
    # Served at the exact site root (not under /static/) so its default
    # service-worker scope is "/" and it can catch pushes app-wide.
    path("sw.js", core_views.service_worker, name="service_worker"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
