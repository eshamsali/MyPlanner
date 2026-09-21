// ---------------------------------------------------------------------------
// My Planner — shared front-end behaviour (vanilla JS, no build step)
// ---------------------------------------------------------------------------

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(";").shift();
  return null;
}
const CSRF_TOKEN = getCookie("csrftoken");

function toast(message) {
  let el = document.getElementById("planner-toast");
  if (!el) {
    el = document.createElement("div");
    el.id = "planner-toast";
    el.className = "toast";
    document.body.appendChild(el);
  }
  el.textContent = message;
  el.classList.add("show");
  clearTimeout(el._hideTimer);
  el._hideTimer = setTimeout(() => el.classList.remove("show"), 2200);
}

async function postForm(url, data) {
  const body = new URLSearchParams(data);
  const res = await fetch(url, {
    method: "POST",
    headers: {
      "X-CSRFToken": CSRF_TOKEN,
      "X-Requested-With": "XMLHttpRequest",
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body,
  });
  return res.json();
}

// ---------------------------------------------------------------------------
// Theme toggle — instantly flips the whole site (CSS vars on <html>) and
// persists to the user's Profile (or session for guests) so it's remembered
// on every future page load without a Settings visit.
// ---------------------------------------------------------------------------
function initTheme() {
  const root = document.documentElement;
  const toggle = document.getElementById("theme-toggle");
  const prefUrl = document.body.getAttribute("data-preference-url");
  if (!toggle) return;
  toggle.addEventListener("click", async () => {
    const next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
    root.setAttribute("data-theme", next);
    const icon = toggle.querySelector("[data-theme-icon]");
    if (icon) icon.textContent = next === "dark" ? "☀" : "☾";
    toggle.setAttribute("data-current-theme", next);
    if (prefUrl) {
      try { await postForm(prefUrl, { theme: next }); } catch (e) { /* best effort */ }
    }
  });
}

// ---------------------------------------------------------------------------
// Language toggle — persists to Profile then reloads so server-rendered
// strings (T.xxx) and RTL layout switch correctly.
// ---------------------------------------------------------------------------
function initLanguage() {
  const toggle = document.getElementById("lang-toggle");
  const prefUrl = document.body.getAttribute("data-preference-url");
  if (!toggle || !prefUrl) return;
  toggle.addEventListener("click", async () => {
    const current = toggle.getAttribute("data-current-lang") || "en";
    const next = current === "ar" ? "en" : "ar";
    await postForm(prefUrl, { language: next });
    window.location.reload();
  });
}

function initSidebarCollapse() {
  const sidebar = document.getElementById("sidebar");
  const btn = document.getElementById("collapse-toggle");
  if (sidebar && btn) {
    btn.addEventListener("click", () => sidebar.classList.toggle("collapsed"));
  }
}

// ---------------------------------------------------------------------------
// Mobile drawer — hamburger icon + bottom-nav "More" open the sidebar as an
// off-canvas panel with a dimmed overlay; tapping the overlay closes it.
// ---------------------------------------------------------------------------
function initMobileDrawer() {
  const sidebar = document.getElementById("sidebar");
  const overlay = document.getElementById("sidebar-overlay");
  const menuBtn = document.getElementById("mobile-menu-btn");
  const moreBtn = document.getElementById("bottom-nav-more");
  if (!sidebar || !overlay) return;

  function open() {
    sidebar.classList.add("mobile-open");
    overlay.classList.add("show");
  }
  function close() {
    sidebar.classList.remove("mobile-open");
    overlay.classList.remove("show");
  }

  if (menuBtn) menuBtn.addEventListener("click", open);
  if (moreBtn) moreBtn.addEventListener("click", open);
  overlay.addEventListener("click", close);
}

// ---------------------------------------------------------------------------
// FAB (mobile quick-add) — reuses the same dropdown menu as the desktop
// Quick Add button, just triggered from the floating button instead.
// ---------------------------------------------------------------------------
function initFab() {
  const fab = document.getElementById("fab-add-btn");
  const menu = document.getElementById("quick-add-menu");
  if (!fab || !menu) return;
  fab.addEventListener("click", (e) => {
    e.stopPropagation();
    const opening = menu.style.display !== "block";
    closeAllMenus();
    menu.style.display = opening ? "block" : "none";
  });
}

// ---------------------------------------------------------------------------
// Quick add dropdown + notifications dropdown (mutually exclusive)
// ---------------------------------------------------------------------------
function closeAllMenus(except) {
  document.querySelectorAll(".quick-add-menu").forEach((m) => {
    if (m !== except) m.style.display = "none";
  });
}

function initQuickAdd() {
  const btn = document.getElementById("quick-add-btn");
  const menu = document.getElementById("quick-add-menu");
  if (!btn || !menu) return;
  btn.addEventListener("click", (e) => {
    e.stopPropagation();
    const opening = menu.style.display !== "block";
    closeAllMenus();
    menu.style.display = opening ? "block" : "none";
  });
  document.addEventListener("click", () => (menu.style.display = "none"));
}

// ---------------------------------------------------------------------------
// Notifications — real in-app dropdown backed by /notifications/data/,
// no browser Notification permission requested anywhere.
// ---------------------------------------------------------------------------
function initNotifications() {
  const btn = document.getElementById("notif-btn");
  const menu = document.getElementById("notif-menu");
  const list = document.getElementById("notif-list");
  const dot = document.getElementById("notif-dot");
  const markRead = document.getElementById("notif-mark-read");
  const url = document.body.getAttribute("data-notifications-url");
  const emptyText = document.body.getAttribute("data-no-notifications-text") || "You're all caught up.";
  if (!btn || !menu || !url) return;

  const iconMap = { "check-square": "☑", repeat: "🔁" };

  async function loadNotifications() {
    list.innerHTML = '<div class="muted" style="font-size:12.5px; padding:10px 8px;">…</div>';
    try {
      const res = await fetch(url, { headers: { "X-Requested-With": "XMLHttpRequest" } });
      const data = await res.json();
      list.innerHTML = "";
      if (!data.items || !data.items.length) {
        list.innerHTML = `<div class="muted" style="font-size:12.5px; padding:10px 8px;">${emptyText}</div>`;
        if (dot) dot.style.display = "none";
        return;
      }
      if (dot) dot.style.display = "block";
      data.items.forEach((item) => {
        const row = document.createElement("div");
        row.style.cssText = "display:flex; gap:8px; align-items:flex-start; padding:8px; border-radius:9px; font-size:12.5px;";
        row.innerHTML = `<span>${iconMap[item.icon] || "•"}</span><span>${item.text}</span>`;
        list.appendChild(row);
      });
    } catch (e) {
      list.innerHTML = '<div class="muted" style="font-size:12.5px; padding:10px 8px;">Couldn\'t load notifications.</div>';
    }
  }

  btn.addEventListener("click", (e) => {
    e.stopPropagation();
    const opening = menu.style.display !== "block";
    closeAllMenus();
    menu.style.display = opening ? "block" : "none";
    if (opening) loadNotifications();
  });
  document.addEventListener("click", () => (menu.style.display = "none"));
  menu.addEventListener("click", (e) => e.stopPropagation());

  if (markRead) {
    markRead.addEventListener("click", () => {
      list.innerHTML = `<div class="muted" style="font-size:12.5px; padding:10px 8px;">${emptyText}</div>`;
      if (dot) dot.style.display = "none";
    });
  }
}

// ---------------------------------------------------------------------------
// AJAX checkboxes — used for task completion + habit today-toggle
// data-toggle-url on the button gives the POST target.
// ---------------------------------------------------------------------------
function initToggleButtons() {
  document.querySelectorAll("[data-toggle-url]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const url = btn.getAttribute("data-toggle-url");
      btn.disabled = true;
      try {
        const data = await postForm(url, {});
        if (data.ok) {
          const done = data.is_completed ?? data.completed ?? data.is_achieved ?? data.is_active;
          btn.classList.toggle("checked", !!done);
          const row = btn.closest("[data-row]");
          if (row) {
            const label = row.querySelector("[data-title]");
            if (label) label.classList.toggle("text-strike", !!done);
          }
        }
      } finally {
        btn.disabled = false;
      }
    });
  });
}

// ---------------------------------------------------------------------------
// Real push notifications (Web Push API) — separate from the in-app
// notifications dropdown. Registers a service worker at /sw.js (served by
// Django at the site root so its scope covers the whole app), asks for
// browser permission, subscribes via PushManager, and sends the
// subscription to the server so send_due_reminders can push to it later.
// ---------------------------------------------------------------------------
function urlBase64ToUint8Array(base64String) {
  const padding = "=".repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding).replace(/-/g, "+").replace(/_/g, "/");
  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);
  for (let i = 0; i < rawData.length; ++i) outputArray[i] = rawData.charCodeAt(i);
  return outputArray;
}

function initPushNotifications() {
  const btn = document.getElementById("enable-push-btn");
  if (!btn) return;

  if (!("serviceWorker" in navigator) || !("PushManager" in window)) {
    btn.disabled = true;
    btn.textContent = "Not supported on this browser";
    return;
  }

  const vapidKey = document.body.getAttribute("data-vapid-public-key");

  async function refreshButtonState() {
    try {
      const reg = await navigator.serviceWorker.getRegistration();
      const sub = reg ? await reg.pushManager.getSubscription() : null;
      btn.textContent = sub ? btn.getAttribute("data-label-on") : btn.getAttribute("data-label-off");
      btn.classList.toggle("achieved-active", !!sub);
    } catch (e) { /* ignore */ }
  }

  btn.addEventListener("click", async () => {
    if (!vapidKey) {
      toast("Push isn't configured on the server yet (missing VAPID key).");
      return;
    }
    btn.disabled = true;
    try {
      const reg = await navigator.serviceWorker.register("/sw.js");
      const existing = await reg.pushManager.getSubscription();

      if (existing) {
        const endpoint = existing.endpoint;
        await existing.unsubscribe();
        await postForm("/accounts/push/unsubscribe/", { endpoint });
        toast("Push notifications turned off.");
      } else {
        const permission = await Notification.requestPermission();
        if (permission !== "granted") {
          toast("Notification permission wasn't granted.");
          return;
        }
        const sub = await reg.pushManager.subscribe({
          userVisibleOnly: true,
          applicationServerKey: urlBase64ToUint8Array(vapidKey),
        });
        await fetch("/accounts/push/subscribe/", {
          method: "POST",
          headers: { "Content-Type": "application/json", "X-CSRFToken": CSRF_TOKEN },
          body: JSON.stringify(sub.toJSON()),
        });
        toast("Push notifications turned on.");
      }
    } catch (e) {
      toast("Couldn't set up push notifications.");
    } finally {
      btn.disabled = false;
      refreshButtonState();
    }
  });

  refreshButtonState();
}

// ---------------------------------------------------------------------------
// Habit weekly-grid day toggles — lets you mark/unmark ANY day of the
// current week for a habit, not just "today". Buttons carry the target
// date in data-date; the URL itself just needs the habit pk.
// ---------------------------------------------------------------------------
function initHabitDayToggle() {
  document.querySelectorAll("[data-habit-day-url]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const url = btn.getAttribute("data-habit-day-url");
      const date = btn.getAttribute("data-date");
      if (!date) return;
      btn.disabled = true;
      try {
        const data = await postForm(url, { date });
        if (data.ok) {
          btn.classList.toggle("done", !!data.completed);
        } else if (data.error) {
          toast(data.error);
        }
      } finally {
        btn.disabled = false;
      }
    });
  });
}

// ---------------------------------------------------------------------------
// Milestone toggles on the goal detail page also update the progress bar
// ---------------------------------------------------------------------------
function initMilestoneToggles() {
  document.querySelectorAll("[data-milestone-url]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const url = btn.getAttribute("data-milestone-url");
      const data = await postForm(url, {});
      if (data.ok) {
        btn.classList.toggle("checked", data.is_completed);
        const bar = document.getElementById("goal-progress-fill");
        const pctLabel = document.getElementById("goal-progress-pct");
        if (bar) bar.style.width = data.goal_progress + "%";
        if (pctLabel) pctLabel.textContent = data.goal_progress + "%";
      }
    });
  });
}

// ---------------------------------------------------------------------------
// Goal "mark achieved" and habit "mark complete / archive" toggles
// ---------------------------------------------------------------------------
function initAchievedToggle() {
  document.querySelectorAll("[data-achieve-url]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const url = btn.getAttribute("data-achieve-url");
      const data = await postForm(url, {});
      if (data.ok) {
        btn.classList.toggle("achieved-active", data.is_achieved);
        const labelOn = btn.getAttribute("data-label-on");
        const labelOff = btn.getAttribute("data-label-off");
        if (labelOn && labelOff) btn.textContent = data.is_achieved ? labelOn : labelOff;
      }
    });
  });
}

function initHabitArchiveToggle() {
  document.querySelectorAll("[data-archive-url]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      if (!confirm(btn.getAttribute("data-confirm") || "Mark this habit as complete?")) return;
      const url = btn.getAttribute("data-archive-url");
      const data = await postForm(url, {});
      if (data.ok) {
        toast("Done!");
        window.location.href = btn.getAttribute("data-redirect") || "/habits/";
      }
    });
  });
}

// ---------------------------------------------------------------------------
// Journal autosave — debounced fetch on input for each field
// ---------------------------------------------------------------------------
function initJournalAutosave() {
  const fields = document.querySelectorAll("[data-journal-field]");
  if (!fields.length) return;
  const dateInput = document.getElementById("journal-date");
  const status = document.getElementById("autosave-status");
  const url = document.body.getAttribute("data-autosave-url");

  fields.forEach((field) => {
    let timer;
    field.addEventListener("input", () => {
      clearTimeout(timer);
      if (status) status.textContent = "Saving…";
      timer = setTimeout(async () => {
        const data = await postForm(url, {
          date: dateInput ? dateInput.value : "",
          field: field.getAttribute("data-journal-field"),
          value: field.value,
        });
        if (status && data.ok) status.textContent = `Saved at ${data.saved_at}`;
      }, 700);
    });
  });

  document.querySelectorAll("[data-mood-option]").forEach((moodBtn) => {
    moodBtn.addEventListener("click", async () => {
      document.querySelectorAll("[data-mood-option]").forEach((b) => b.classList.remove("selected"));
      moodBtn.classList.add("selected");
      const data = await postForm(url, {
        date: dateInput ? dateInput.value : "",
        field: "mood",
        value: moodBtn.getAttribute("data-mood-option"),
      });
      if (status && data.ok) status.textContent = `Saved at ${data.saved_at}`;
    });
  });
}

// ---------------------------------------------------------------------------
// Simple modal open/close (used by "New task", "New habit", "New goal", etc.)
// Also auto-opens the page's "new" modal when arriving via ?new=1 — this is
// what makes Quick Add jump straight into the create form.
// ---------------------------------------------------------------------------
function initModals() {
  document.querySelectorAll("[data-open-modal]").forEach((opener) => {
    opener.addEventListener("click", () => {
      const modal = document.getElementById(opener.getAttribute("data-open-modal"));
      if (modal) modal.style.display = "flex";
    });
  });
  document.querySelectorAll("[data-close-modal]").forEach((closer) => {
    closer.addEventListener("click", () => {
      const modal = closer.closest(".modal-backdrop");
      if (modal) modal.style.display = "none";
    });
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      document.querySelectorAll(".modal-backdrop").forEach((m) => (m.style.display = "none"));
    }
  });

  const params = new URLSearchParams(window.location.search);
  if (params.get("new") === "1") {
    const autoModal = document.querySelector('.modal-backdrop[id^="new-"]');
    if (autoModal) autoModal.style.display = "flex";
  }
}

document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  initLanguage();
  initSidebarCollapse();
  initMobileDrawer();
  initFab();
  initQuickAdd();
  initNotifications();
  initToggleButtons();
  initHabitDayToggle();
  initPushNotifications();
  initMilestoneToggles();
  initAchievedToggle();
  initHabitArchiveToggle();
  initJournalAutosave();
  initModals();
});
