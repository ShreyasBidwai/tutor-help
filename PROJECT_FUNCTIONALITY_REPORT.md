# TuitionTrack — Complete Functionality Report

**Date:** 24 February 2026  
**Audit scope:** Every route, feature, and module in the `tutor-help/` codebase

---

## Summary

| Category | ✅ Working | ⚠️ Partial | ❌ Not Working / Stub |
|----------|-----------|-----------|---------------------|
| Auth & Onboarding | 5 | 1 | 1 |
| Dashboard | 3 | 0 | 0 |
| Batch Management | 5 | 0 | 0 |
| Student Management | 7 | 0 | 0 |
| Attendance | 2 | 0 | 0 |
| Homework | 5 | 0 | 0 |
| Reports | 3 | 0 | 0 |
| Exports (CSV) | 3 | 0 | 0 |
| Student Portal | 6 | 0 | 0 |
| Push Notifications | 3 | 1 | 0 |
| Payments | 0 | 0 | 2 |
| Admin Dashboard | 0 | 5 | 0 |
| Infrastructure | 5 | 0 | 0 |
| **Totals** | **47** | **7** | **3** |

---

## 1. Auth & Onboarding

| # | Feature | Route | Status | Notes |
|---|---------|-------|--------|-------|
| 1 | Welcome / landing page | `GET /welcome` | ✅ Working | Redirects logged-in users to dashboard |
| 2 | Tutor signup (mobile + password + tuition name) | `POST /login` → `GET /signup` | ✅ Working | Validates mobile, password length, tuition name |
| 3 | Tutor login (mobile + password) | `POST /login` | ✅ Working | Password hash checked, session created |
| 4 | Logout | `GET /logout` | ✅ Working | Clears session, redirects to welcome |
| 5 | Profile edit (tutor name, tuition name, address) | `GET/POST /profile` | ✅ Working | Name validation, session update |
| 6 | Enterprise login | `GET /enterprise/login` | ⚠️ Partial | Template exists but shows "Coming Soon" — stub |
| 7 | Onboarding flow (intro.js tour) | JS in dashboard | ✅ Working | Guided tour with `data-intro-step` attributes |

---

## 2. Dashboard (Tutor)

| # | Feature | Route | Status | Notes |
|---|---------|-------|--------|-------|
| 1 | Main dashboard with stats cards | `GET /dashboard` | ✅ Working | Shows student count, batch count, today's attendance, pending homework |
| 2 | Today's Batches (upcoming/past) | `GET /api/batches/upcoming` | ✅ Working | AJAX polling, filters by today's day code |
| 3 | Quick Actions (Add Student, Create Batch, Share HW) | In dashboard template | ✅ Working | Links to respective pages |

---

## 3. Batch Management

| # | Feature | Route | Status | Notes |
|---|---------|-------|--------|-------|
| 1 | List all batches | `GET /batches` | ✅ Working | Shows name, time, day badges |
| 2 | View batch students | `GET /batches/<id>/students` | ✅ Working | Lists students in batch with attendance quick-view |
| 3 | Add batch | `GET/POST /batches/add` | ✅ Working | Name, time, days, notifications toggle, duplicate name validation |
| 4 | Edit batch | `GET/POST /batches/<id>/edit` | ✅ Working | Pre-fills form, validates ownership |
| 5 | Delete batch | `DELETE /api/batches/<id>` | ✅ Working | Cascades to students/attendance via FK, ownership check |

---

## 4. Student Management

| # | Feature | Route | Status | Notes |
|---|---------|-------|--------|-------|
| 1 | List all students (with batch filter) | `GET /students` | ✅ Working | Paginated, batch filter dropdown |
| 2 | Add student | `GET/POST /students/add` | ✅ Working | Name validation (letters only), phone uniqueness per user, auto-password generation |
| 3 | Edit student | `GET/POST /students/<id>/edit` | ✅ Working | Change name, phone, batch, school, standard, address |
| 4 | View student detail | `GET /students/<id>` | ✅ Working | Shows info + recent attendance + homework |
| 5 | Delete student | `DELETE /api/students/<id>` | ✅ Working | Cascade deletes attendance records |
| 6 | Update student password | `POST /api/students/<id>/update-password` | ✅ Working | Re-generates random password, returns new credentials |
| 7 | Student credentials page | `GET /students/credentials` | ✅ Working | Bulk list phone + password for sharing |

---

## 5. Attendance

| # | Feature | Route | Status | Notes |
|---|---------|-------|--------|-------|
| 1 | Attendance page (select batch, date, mark present/absent/late) | `GET /attendance` | ✅ Working | Batch selector, date picker, "Mark All Present/Absent" buttons, preview |
| 2 | Save attendance (bulk) | `POST /api/attendance/save` | ✅ Working | Upserts per student+date, sends push notification to students on save |

---

## 6. Homework

| # | Feature | Route | Status | Notes |
|---|---------|-------|--------|-------|
| 1 | List homework | `GET /homework` | ✅ Working | Paginated, shows batch name, due date, file/YouTube link |
| 2 | Share homework (create) | `GET/POST /homework/share` | ✅ Working | Supports text, file upload (image/PDF/doc), YouTube URL, due date, batch selection. Sends push to students |
| 3 | Edit homework | `GET/POST /homework/<id>/edit` | ✅ Working | Update title, description, content, file, due date |
| 4 | Delete homework | `DELETE /api/homework/<id>` | ✅ Working | Deletes associated file from disk |
| 5 | Serve uploaded files | `GET /uploads/<filename>` | ✅ Working | Static file serving from uploads dir |
| 6 | Auto-cleanup expired homework | `cleanup_expired_homework()` | ✅ Working | Deletes HW + files 1 day after due date, runs on dashboard load |

---

## 7. Reports

| # | Feature | Route | Status | Notes |
|---|---------|-------|--------|-------|
| 1 | Reports overview (all batches) | `GET /reports` | ✅ Working | Shows per-batch attendance %, today's %, present/absent counts |
| 2 | Batch report detail | `GET /reports/batch/<id>` | ✅ Working | Per-student attendance table for selected month, filterable |
| 3 | Student report detail | `GET /reports/student/<id>` | ✅ Working | Calendar view, monthly stats, attendance history |

---

## 8. CSV Exports

| # | Feature | Route | Status | Notes |
|---|---------|-------|--------|-------|
| 1 | Export students | `GET /export/students` | ✅ Working | CSV with name, phone, batch, school, address |
| 2 | Export attendance | `GET /export/attendance` | ✅ Working | Date range + batch filter, CSV download |
| 3 | Export batch report | `GET /export/reports/batch/<id>` | ✅ Working | 30-day attendance summary per student |

---

## 9. Student Portal (student login)

| # | Feature | Route | Status | Notes |
|---|---------|-------|--------|-------|
| 1 | Student login | `GET/POST /student/login` | ✅ Working | Phone + password auth, loads tuition context |
| 2 | Student dashboard | `GET /student/dashboard` | ✅ Working | Shows attendance %, recent homework, batch info |
| 3 | Student attendance view | `GET /student/attendance` | ✅ Working | Calendar with present/absent dots, monthly summary |
| 4 | Student homework view | `GET /student/homework` | ✅ Working | Lists active homework with files/YouTube links |
| 5 | Student profile | `GET /student/profile` | ✅ Working | Shows name, phone, batch, school |
| 6 | Homework reminders API | `GET /api/student/homework/reminders` | ✅ Working | Returns upcoming homework badges for polling |
| 7 | Attendance notifications API | `GET /api/student/attendance/notifications` | ✅ Working | Returns unread attendance notifications |

---

## 10. Push Notifications

| # | Feature | Route/Function | Status | Notes |
|---|---------|----------------|--------|-------|
| 1 | Subscribe to push | `POST /api/push/subscribe` | ✅ Working | Stores FCM token in push_subscriptions table |
| 2 | Unsubscribe from push | `POST /api/push/unsubscribe` | ✅ Working | Removes token |
| 3 | Send notification (FCM) | `send_fcm_notification()` | ✅ Working | Uses Firebase Admin SDK, sends to all user devices |
| 4 | Cron webhook (batch start + attendance reminders) | `GET/POST /api/webhooks/cron` | ⚠️ Partial | Code is working, but requires external cron service (cron-job.org) to trigger. Secret key validation works. Won't run automatically without the external trigger. |

---

## 11. Payments

| # | Feature | Route | Status | Notes |
|---|---------|-------|--------|-------|
| 1 | Payments locked page | `GET /payments/locked` | ❌ Stub | Just renders a "locked" template — no actual payment logic |
| 2 | Pro details page | `GET /payments/pro-details` | ❌ Stub | Shows feature descriptions, no purchase flow |

**Note:** The entire payments module is a UI placeholder. No payment gateway integration, no billing logic, no pro/free plan enforcement exists.

---

## 12. Admin Dashboard (NEW — `/tut-admin/`)

| # | Feature | Route | Status | Notes |
|---|---------|-------|--------|-------|
| 1 | Admin login | `GET/POST /tut-admin/login` | ⚠️ Partial | Blueprint and templates created but `create_admin.py` seed script was accidentally deleted. Admin user needs to be re-seeded in DB. |
| 2 | Admin dashboard overview | `GET /tut-admin/` | ⚠️ Partial | Code is complete — shows total teachers, students, batches, attendance, signups. Needs admin login to work. |
| 3 | All teachers list | `GET /tut-admin/teachers` | ⚠️ Partial | Lists all tutors with student/batch counts, last active date. Needs admin login. |
| 4 | Teacher detail | `GET /tut-admin/teachers/<id>` | ⚠️ Partial | Shows batches, students, attendance stats for a tutor. Needs admin login. |
| 5 | All students (cross-tutor) | `GET /tut-admin/students` | ⚠️ Partial | Lists all students across all tutors. Needs admin login. |

**Note:** The admin panel code is fully implemented but needs the `create_admin.py` script to be recreated to seed the first admin user. Once seeded, all 5 pages will be fully functional.

---

## 13. Infrastructure & Utilities

| # | Feature | File/Route | Status | Notes |
|---|---------|------------|--------|-------|
| 1 | SQLite database with WAL mode | `database.py` | ✅ Working | Auto-migration, retry logic, indexes, FK constraints |
| 2 | Firebase service worker | `GET /firebase-messaging-sw.js` | ✅ Working | Injected config from env vars |
| 3 | PWA manifest | `GET /manifest.json` | ✅ Working | App icons, theme color, display mode |
| 4 | Health check | `GET /health` | ✅ Working | Returns JSON status for monitoring |
| 5 | Error pages (404, 500) | Templates | ✅ Working | Custom error templates |
| 6 | Gunicorn config | `gunicorn_config.py` | ✅ Working | Production WSGI config |
| 7 | Systemd service | `tutor-help.service` | ✅ Working | For Linux deployment |

---

## Features NOT Implemented (No Code Exists)

| Feature | Notes |
|---------|-------|
| Payment gateway integration | No Razorpay/Stripe/UPI integration. `payments.py` is a stub. |
| Pro vs Free plan enforcement | No feature gating — all features are open to everyone. |
| Fee tracking / payment history | No fee management module at all. |
| Multi-language support (i18n) | All UI is in English. |
| Dark mode | No theme toggle (light mode only). |
| Batch-level reports export (PDF) | Only CSV export is available. |
| Admin: Edit/delete teachers | Admin dashboard is read-only. |
| Admin: Edit/delete students | Admin dashboard is read-only. |
| Admin: Payment/billing overview | No payment data exists to show. |
| Email notifications | Only push (FCM) notifications, no email/SMS. |
| Automated testing | No unit tests or integration tests exist. |
| Rate limiting | No API rate limiting on any endpoint. |
| CSRF protection | No CSRF tokens on forms (Flask-WTF not used). |
| Session timeout warning | Sessions expire silently after 24 hours. |

---

## File Structure Overview

```
tutor-help/
├── app.py                  # Main Flask app, blueprint registration
├── config.py               # Environment-based configuration
├── database.py             # SQLite schema, migrations, indexes
├── jobs.py                 # FCM notification jobs (batch start, attendance)
├── gunicorn_config.py      # Production WSGI config
├── start.sh                # Production start script
├── tutor-help.service      # Systemd service file
├── requirements.txt        # Python dependencies
├── migrate.py              # Legacy data migration script
├── manifest.json           # PWA manifest
├── firebase-service-account.json # Firebase Admin SDK key
├── .env / .env.example     # Environment variables
│
├── blueprints/
│   ├── auth.py             # Tutor & student login/signup/profile
│   ├── dashboard.py        # Tutor dashboard + onboarding API
│   ├── students.py         # Student CRUD + credentials
│   ├── batches.py          # Batch CRUD + batch students view
│   ├── attendance.py       # Attendance page + save API
│   ├── homework.py         # Homework CRUD + file uploads
│   ├── reports.py          # Reports overview + batch/student detail
│   ├── export.py           # CSV export (students, attendance, reports)
│   ├── student.py          # Student portal (dashboard, attendance, HW)
│   ├── payments.py         # Payment stubs (locked/pro details)
│   └── webhooks.py         # External cron webhook for notifications
│
├── admin_panel/
│   ├── __init__.py         # Exports admin_bp
│   ├── routes.py           # Admin login, dashboard, teachers, students
│   └── templates/admin/    # Admin-only templates (6 files)
│
├── templates/              # Jinja2 templates (37 files)
├── static/                 # CSS, JS, images, manifest
├── utils/
│   ├── __init__.py         # require_login, require_role, IST helpers
│   └── push_notifications.py # FCM send helpers
├── scripts/
│   ├── populate_user_data.py # Sample data generator
│   └── test_push.py        # Push notification tester
└── uploads/                # User-uploaded homework files
```

---

## Database Tables

| Table | Purpose | Records Linked To |
|-------|---------|-------------------|
| `users` | Tutor accounts (mobile, password, tuition name) | batches, students, attendance, homework |
| `batches` | Batch definitions (name, time, days) | students, homework |
| `students` | Student records (name, phone, batch, school) | attendance, homework |
| `attendance` | Daily attendance (student + date + status) | students, users |
| `homework` | Homework entries (title, file, YouTube, due date) | batches, students, users |
| `push_subscriptions` | FCM tokens for push notifications | users |
| `admins` | Admin login credentials (separate from users) | — |

---

*End of report*
