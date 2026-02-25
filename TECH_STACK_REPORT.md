# TuitionTrack — Technology Stack Report

**Branch:** `feature`  
**Date:** 24 February 2026

---

## Backend

| Technology | Version | Purpose |
|-----------|---------|---------|
| **Python** | 3.12.2 | Runtime (via pyenv) |
| **Flask** | 3.0.0 | Web framework — routing, templating, sessions |
| **Werkzeug** | 3.0.1 | WSGI toolkit — password hashing (`generate_password_hash`, `check_password_hash`), request handling |
| **Gunicorn** | 21.2.0 | Production WSGI server |
| **python-dotenv** | 1.0.0 | Load `.env` files for config |
| **firebase-admin** | ≥6.2.0 | Firebase Admin SDK — sending FCM push notifications server-side |

---

## Frontend

| Technology | Version | Purpose |
|-----------|---------|---------|
| **HTML5 + Jinja2** | — | Server-rendered templates (37 template files) |
| **Vanilla CSS** | — | All styling is inline `<style>` blocks in `base.html` and individual templates. **No CSS framework** (no Tailwind, Bootstrap, etc.) |
| **Vanilla JavaScript** | — | All interactivity — fetch API calls, DOM manipulation, event handlers. **No JS framework** (no React, Vue, etc.) |
| **SweetAlert2** | 11.x (CDN) | Beautiful alert/confirm dialogs (delete confirmations, success messages) |
| **Intro.js** | 7.2.0 (CDN) | Onboarding tour / guided walkthrough for new users |
| **Firebase JS SDK** | 8.10.1 (CDN) | Browser-side Firebase Cloud Messaging for push notifications |

---

## Database

| Technology | Details |
|-----------|---------|
| **SQLite** | Single-file database (`tutor_app.db`) |
| **WAL mode** | Enabled for better read/write concurrency |
| **Tables** | `users`, `batches`, `students`, `attendance`, `homework`, `push_subscriptions` (6 tables) |
| **Migrations** | Custom Python migrations in `database.py` — `init_db()`, `migrate_db()`, `add_indexes()` |
| **No ORM** | All queries are raw SQL via `sqlite3` module |

---

## Push Notifications

| Component | Technology |
|-----------|------------|
| **Server → Device** | Firebase Cloud Messaging (FCM) via `firebase-admin` Python SDK |
| **Browser Registration** | Firebase JS SDK 8.x — gets FCM token, stores in `push_subscriptions` table |
| **Service Worker** | `firebase-messaging-sw.js` — served at root, config injected from env vars |
| **Trigger** | External cron service (cron-job.org) hits `/api/webhooks/cron` every 5 minutes |
| **Notification Types** | Batch start reminder, attendance reminder (15 min delay), homework shared, attendance marked |

---

## Authentication

| Aspect | Implementation |
|--------|----------------|
| **Method** | Mobile number + password (no OTP, no OAuth) |
| **Password Storage** | `werkzeug.security.generate_password_hash` (pbkdf2:sha256) |
| **Sessions** | Flask server-side sessions (signed cookies) |
| **Session Duration** | 24 hours (`PERMANENT_SESSION_LIFETIME`) |
| **Roles** | `tutor` (default), `student` — stored in `users.role` |
| **Student Auth** | Separate login at `/student/login` — phone + password |
| **Auth Decorators** | `@require_login` (checks `session['user_id']`), `@require_role('tutor')` |
| **CSRF Protection** | ❌ None (Flask-WTF not used) |

---

## PWA (Progressive Web App)

| Feature | Status |
|---------|--------|
| **manifest.json** | ✅ App name, icons (48–512px), theme color `#4F46E5`, `standalone` display |
| **Service Worker** | ✅ Firebase messaging SW + offline fallback (`offline.html`) |
| **Installable** | ✅ Meets PWA criteria — installable on Android/iOS |
| **TWA (Trusted Web Activity)** | Config present (assetlinks setup) for wrapping as Android app |
| **Offline Support** | Minimal — only `offline.html` fallback page |

---

## Static Assets

| Category | Files |
|----------|-------|
| **App Icons** | 6 PNG sizes (48, 72, 96, 144, 192, 512) |
| **Logos** | `TutionTrack_headerLogo.png`, `TutionTrack_logo.png`, `TutionTrack_logoNoBG.png` |
| **Avatar Images** | `niya_avatar_*.png` (5 sizes: 50–200px) |
| **JavaScript** | `form-validation.js`, `push-notifications.js`, `service-worker.js`, `skeleton-loader.js`, `swipe-gestures.js`, `tours.js` |
| **CSS Files** | None — all CSS is embedded in templates |

---

## Project Structure

```
tutor-help/
├── app.py                    # Flask app init, blueprint registration
├── config.py                 # Config class (env-based)
├── database.py               # SQLite schema, migration, indexes
├── jobs.py                   # Background notification jobs
├── requirements.txt          # 5 Python dependencies
│
├── blueprints/               # 12 Flask blueprints
│   ├── auth.py               # Login/signup/profile/push subscribe
│   ├── dashboard.py          # Tutor dashboard + onboarding API
│   ├── students.py           # Student CRUD + credentials
│   ├── batches.py            # Batch CRUD
│   ├── attendance.py         # Mark attendance + save API
│   ├── homework.py           # Homework CRUD + file uploads
│   ├── reports.py            # Attendance reports
│   ├── export.py             # CSV exports
│   ├── student.py            # Student portal
│   ├── payments.py           # Payment stubs
│   └── webhooks.py           # External cron webhook
│
├── utils/
│   ├── __init__.py           # Auth decorators, IST helpers
│   └── push_notifications.py # FCM send utilities
│
├── templates/                # 37 Jinja2 HTML templates
├── static/                   # JS, images, manifest
├── scripts/                  # Data population + push tester
├── uploads/                  # User-uploaded homework files
├── docs/                     # Internal documentation (11 md files)
│
├── .env / .env.example       # Environment variables
├── firebase-service-account.json  # Firebase Admin SDK credentials
├── gunicorn_config.py        # Production WSGI config
├── start.sh                  # Production start script
└── tutor-help.service        # Systemd service (Linux deploy)
```

---

## Deployment

| Aspect | Technology |
|--------|------------|
| **Hosting** | Render (cloud platform) |
| **WSGI Server** | Gunicorn with config file |
| **Process Manager** | Systemd (for VM/VPS deploy) |
| **Database** | SQLite file on disk (no external DB) |
| **File Storage** | Local `uploads/` directory (not cloud storage) |
| **SSL** | Managed by Render / reverse proxy |
| **Monitoring** | `/health` endpoint returns JSON status |

---

## External Services

| Service | Usage |
|---------|-------|
| **Firebase (Google)** | Push notifications via FCM, service worker |
| **cron-job.org** | External cron — triggers `/api/webhooks/cron` every 5 min for automated reminders |
| **CDN (jsDelivr)** | SweetAlert2, Intro.js, Firebase JS SDK |

---

## What's NOT Used

| Category | Details |
|----------|---------|
| CSS Framework | No Tailwind, Bootstrap, or Material — all custom CSS |
| JS Framework | No React, Vue, Angular — all vanilla JS |
| ORM | No SQLAlchemy — raw SQL only |
| Task Queue | No Celery, RQ — cron via external webhook |
| Caching | No Redis, Memcached — no caching layer |
| Email/SMS | No Twilio, SendGrid — push only |
| Payment Gateway | No Razorpay, Stripe — payments not implemented |
| Testing | No pytest, unittest — no test suite |
| CI/CD | No GitHub Actions, no automated pipeline |
| Containerization | No Docker — direct deployment |
| Logging Service | No Sentry, Datadog — only Python `logging` to stdout |

---

*End of report*
