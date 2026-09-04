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
- Settings: appearance (theme/accent/font size), planner prefs (week start,
  time format), notification toggles — all persisted to `Profile`
- Dashboard: today's progress ring, priority tasks, schedule, habit
  mini-bars, top goal, quick journal preview
- Tasks: tabs (Today/Upcoming/All/Completed), create modal, AJAX
  complete-toggle, delete
- Habits: weekly completion grid, streak + completion-rate calculations,
  detail page with a month view, create modal
- Goals: card grid with progress bars, detail page with milestones
  (AJAX toggle updates the progress bar live) and related tasks
- Journal: one entry per day, mood picker, four reflection fields that
  autosave via `fetch()` as you type (700ms debounce)
- Notes: folders, list/search, simple editor, delete confirmation

## Not yet implemented (natural next steps)

- Calendar month/week/day views (the dashboard/task model already has the
  date & time fields needed — this would be a new `core` view + template)
  along with drag/resize interactions
- Global command-palette search across tasks/notes/goals/journal
- Notification dropdown backed by real notification records (currently a
  static bell icon)
- Recurring task/habit generation from the `repeat` field (the field exists
  on `Task`; a periodic job or cron command would create future instances)
- Dark mode / accent color are wired to `Profile` and applied on page load,
  but the sidebar's quick theme toggle is client-side only — hook it up to
  POST to `accounts:settings` if you want it to persist automatically
- Tests (none included yet)

## Design notes

The visual system follows the original brief: warm off-white background,
white cards, a lavender accent (swappable to pink/blue/green/orange via
Settings → Appearance), soft green/orange/red for success/warning/error,
Plus Jakarta Sans for UI text and Fraunces (serif) for greetings and
journal prompts to give it a "personal notebook" feel rather than a
generic SaaS dashboard look. All of this lives in CSS custom properties
in `core/static/core/css/style.css`, switched via `data-theme` and
`data-accent` attributes on `<html>`.
