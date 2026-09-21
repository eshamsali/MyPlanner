# My Planner — Django + PostgreSQL

A personal productivity planner: tasks, habits, goals, journal, and notes,
built with Django, server-rendered HTML/CSS, vanilla JavaScript (fetch-based
AJAX, no build step), and PostgreSQL.

## Stack

- **Backend:** Django 5 (function-based views, Django forms & formsets)
- **Database:** PostgreSQL
- **Frontend:** Django templates + a small hand-written CSS design system
  (`core/static/core/css/style.css`) + vanilla JS (`core/static/core/js/app.js`)
- **Icons:** [Lucide](https://lucide.dev) via CDN

## Project layout

```
config/           settings, root urls, wsgi/asgi
accounts/         auth (login/signup/logout), Profile model, settings & profile pages
core/             dashboard view, base template, shared CSS/JS, context processor
tasks/            Task model + views (list/create/toggle/delete)
habits/           Habit + HabitLog models, weekly grid, streak logic
goals/            Goal + Milestone models, progress tracking, related tasks
journal/          JournalEntry model, autosaving daily entry
notes/            Note + NoteFolder models
schedule/         Appointment model — fixed weekly timetable, feeds the calendar
templates/        base.html (app shell) and auth_base.html (login/signup layout)
```

## Local setup

1. **Create a virtual environment and install dependencies**

   ```bash
   python -m venv venv
   source venv/bin/activate        # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Set up PostgreSQL**

   Create a database and user (adjust names/passwords as you like):

   ```sql
   CREATE DATABASE planner_db;
   CREATE USER planner_user WITH PASSWORD 'planner_pass';
   GRANT ALL PRIVILEGES ON DATABASE planner_db TO planner_user;
   ```

3. **Configure environment variables**

   ```bash
   cp .env.example .env
   # edit .env if your DB credentials differ
   ```

4. **Run migrations and create a superuser**

   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

5. **Run the dev server**

   ```bash
   python manage.py runserver
   ```

   Visit `http://127.0.0.1:8000/accounts/signup/` to create an account, or
   `http://127.0.0.1:8000/admin/` to use the Django admin (useful for
   quickly adding sample tasks/habits/goals while the UI is still growing).

## What's implemented

- Auth: signup, login, logout, profile edit (name/email/avatar), stats
- Settings: appearance (theme/accent/font size/**language**), planner prefs
  (week start, time format), notification toggles — all persisted to `Profile`
- **Calendar**: real month view with prev/next navigation, per-day task
  indicators (colored by priority), click a day to see its task list, plus
  fixed weekly appointments projected onto every matching date
- **Fixed weekly appointments schedule** (`schedule` app): add a recurring
  weekly timetable entry once (class, shift, standing meeting) and it shows
  up on the calendar automatically every week; fully editable/deletable
- **Notifications**: in-app dropdown in the topbar (due-today tasks/habits),
  **plus real OS-level push notifications** (Web Push / VAPID) via the
  "Enable" button in Settings → Notifications, delivered by the
  `send_due_reminders` management command
- **Journal insights report**: rule-based mood-trend analysis (improving /
  declining / stable) correlated against task/habit completion rates, with
  bilingual recommendations — `/journal/insights/`
- **Arabic language support**: a language toggle in the sidebar and in
  Settings → Appearance switches the whole UI to Arabic and flips the layout
  to RTL. Translation strings live in `core/translations.py` as a simple
  `{"en": {...}, "ar": {...}}` dict (no `gettext`/`.mo` compilation needed) —
  extend it the same way for any text not yet covered
- **Theme toggle persists everywhere**: clicking the sidebar's dark/light
  toggle saves to your `Profile` immediately via AJAX
- Dashboard: today's progress ring, priority tasks, schedule, habit
  mini-bars, top goal (shown with an "Achieved ✓" badge instead of
  disappearing once achieved), quick journal preview
- Tasks: tabs (Today/Upcoming/All/Completed), create modal, AJAX
  complete-toggle, delete
- Habits: weekly completion grid where **any day can be marked/unmarked**
  (not just today), frequency support for "Specific days" (choose exactly
  which weekdays apply), streak + completion-rate calculations, detail page
  with a month view, "Mark habit complete" button (archives it)
- Goals: card grid with progress bars, detail page with milestones
  (AJAX toggle updates the progress bar live), related tasks, "Mark as
  achieved" button
- Journal: one entry per day, mood picker, four reflection fields that
  autosave via `fetch()` as you type (700ms debounce)
- Notes: folders, list/search, simple editor, delete confirmation
- **Fully responsive** across desktop / tablet / phone breakpoints

## Real push notifications — one-time setup

```bash
pip install -r requirements.txt          # includes pywebpush + py-vapid
python -m py_vapid --gen                 # generates private_key.pem + prints your public key
```

Put the printed public key in `.env` as `VAPID_PUBLIC_KEY=...`, keep
`private_key.pem` next to `manage.py` (out of git), then run:

```bash
python manage.py migrate
python manage.py send_due_reminders      # run this every minute via
                                          # Windows Task Scheduler / cron
```

## Upgrading from an earlier copy of this project

If you already ran `migrate` once before pulling this update:

```bash
python manage.py makemigrations
python manage.py migrate
```

(New fields: `Profile` gained nothing new here, but `Task.reminder_sent_at`,
`Habit.active_days` / `Habit.last_reminder_sent_date`, and the new
`PushSubscription` and `schedule.Appointment` models all need migrating.)

## Not yet implemented (natural next steps)

- Calendar week/day views (month view is done; week/day are natural
  extensions of the same `core:calendar` view + template)
- Global command-palette search across tasks/notes/goals/journal
- Recurring task generation from the `repeat` field on `Task`
- Full RTL coverage: the shell is mirrored for Arabic; a few deeper
  form-modal layouts may still want manual RTL polish
- Login/signup pages are still English-only
- Tests (none included yet)

## Design notes

The visual system follows the original brief: warm off-white background,
white cards, a lavender accent (swappable to pink/blue/green/orange via
Settings → Appearance), soft green/orange/red for success/warning/error,
Plus Jakarta Sans for UI text and Fraunces (serif) for greetings and
journal prompts. All of this lives in CSS custom properties in
`core/static/core/css/style.css`, switched via `data-theme` and
`data-accent` attributes on `<html>`. Arabic/RTL mode adds a `dir="rtl"`
attribute on `<html>` with matching `[dir="rtl"]` overrides in the same
stylesheet.
