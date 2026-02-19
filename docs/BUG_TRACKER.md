# TuitionTrack — Bug & Task Tracker
**Last Updated:** 2026-02-19

---

## ✅ RESOLVED

| # | Issue | Status | Date Fixed |
|---|-------|--------|------------|
| 1 | FCM push notifications failing ("entity not found") | ✅ Fixed | 2026-02-19 |
| 2 | Service Worker caching user-specific HTML (wrong user after login switch) | ✅ Fixed | 2026-02-19 |
| 3 | Session fixation — old session persists after re-login | ✅ Fixed | 2026-02-19 |
| 4 | Stale FCM tokens returned by browser | ✅ Fixed | 2026-02-19 |
| 5 | Missing VAPID key (placeholder in .env) | ✅ Fixed | 2026-02-19 |
| 6 | Firebase project ID mismatch (client vs server) | ✅ Fixed | 2026-02-19 |

---

## 🔴 OPEN BUGS

| # | Bug | Severity | File(s) | Notes |
|---|-----|----------|---------|-------|
| B1 | Welcome page floods server with requests on logout (10+ GET /welcome in 1 second) | Low | `templates/`, service worker | Possibly multiple service worker + PWA tabs re-requesting. Monitor. |
| B2 | `DEBUG: Auth Action` print statements still in `auth.py` | Low | `blueprints/auth.py` | Remove before production deploy |
| B3 | `push_subscriptions` foreign key schema may not reference `users.id` properly | Low | `database.py` / migrations | Verify FK constraint exists |

---

## 📋 TASKS (TO-DO)

### Important (Not Priority)

| # | Task | Importance | Effort | Details |
|---|------|-----------|--------|---------|
| T1 | **Plaintext passwords in `students` table** | 🟡 Important | Medium | `students.py` stores plaintext password in `password` column alongside `password_hash`. Lines 125-127: `SET password = ?, password_hash = ?`. The `password` column should be dropped entirely — only `password_hash` should be stored. Requires: DB migration to drop `password` column, update all INSERT/UPDATE queries, update student credential sharing flow. |
| T2 | **Weak auto-generated student passwords** | 🟡 Important | Low | `students.py` line 224: passwords are 6-digit numeric only (`string.digits, k=6`). Should be alphanumeric or longer. |
| T3 | **Student password min length is only 4** | 🟡 Important | Low | `students.py` line 109: `len(new_password) < 4`. Should be at least 6 to match tutor requirements. |

### Nice-to-Have

| # | Task | Importance | Effort | Details |
|---|------|-----------|--------|---------|
| T4 | Add CSRF protection to forms | 🟢 Low | Medium | Use Flask-WTF or manual CSRF tokens |
| T5 | Rate limiting on login/signup endpoints | 🟢 Low | Medium | Prevent brute-force attacks |
| T6 | File upload validation & sanitization | 🟢 Low | Medium | Validate uploaded file types server-side |
| T7 | APScheduler running in multiple Gunicorn workers | 🟢 Low | Medium | Jobs may execute multiple times in production |
| T8 | Generate proper `SECRET_KEY` in `.env` | 🟢 Low | Low | Current key is a readable string, should be `secrets.token_hex(32)` |
| T9 | Remove `/debug/push` route before production | 🟢 Low | Low | Debug endpoint should not be public |
| T10 | Add proper `name` field to user signup | 🟢 Low | Low | All users show "No Name" in test script |

---

## 📝 Notes

- **Password Task (T1)** is the most important pending task. The `students` table has BOTH a `password` (plaintext) and `password_hash` column. When a student is created or password is updated, the plaintext is stored alongside the hash. This is a security vulnerability. Fix: drop the `password` column, only use `password_hash`, and update the credential sharing flow to show the password only at creation time (not retrieve it from DB).
- **Service Worker** was upgraded to v2 with smart caching. Static assets use Cache First, dynamic pages use Network First.
- **Firebase** is fully configured for project `tuitiontrack21ns15`.
