# TuitionTrack - Complete Project Overview

## 1. What is the Project?
**TuitionTrack** is a hyper-simple, mobile-first Progressive Web App (PWA) designed specifically for individual home tutors in India. It serves as a comprehensive MVP (Minimum Viable Product) that provides essential tools for tutors to digitize their daily operations, including student management, batch organization, daily attendance tracking, and homework sharing.

The project features a freemium model:
- **Free Tier:** Fully functional set of core features for managing students, batches, attendance, and homework.
- **Pro Tier (Locked):** Designed for future monentization, this tier includes advanced features like automated UPI fee collection, digital receipts, and automated reminder systems.

---

## 2. Technology Stack Used
The application is built using a lightweight and efficient tech stack prioritizing fast deployment and minimal configuration:

### Backend
- **Framework:** Python 3 + Flask (Micro-framework)
- **Database:** SQLite3 (Embedded, Zero-configuration) optimized with WAL (Write-Ahead Logging) mode and memory-mapped I/O for concurrent data access.
- **Background Jobs:** Flask-APScheduler for executing cron jobs (e.g., sending reminders).
- **Other Python Libraries:** Werkzeug, firebase-admin, gunicorn, python-dotenv.

### Frontend
- **Structure & Rendering:** HTML5, dynamically rendered using Jinja2 templates (Server-side rendering).
- **Styling:** Vanilla CSS3 emphasizing a modern, mobile-first design system with responsive layouts (flexbox/grid) and visually appealing components (gradients, glassmorphism, 44px minimum touch targets).
- **Interactivity:** Vanilla JavaScript for local interactive dynamics, DOM manipulation, and asynchronous requests via Fetch API.

### Infrastructure & PWA
- **Progressive Web App (PWA):** Features a full PWA layout using `manifest.json` and offline caching with Service Workers.
- **Push Notifications:** Firebase Cloud Messaging (FCM) through the Firebase Admin SDK, enabling web push notifications via `firebase-messaging-sw.js`.
- **Hosting / Deployment Capability:** Ready for WSGI deployment using Gunicorn. Has specific headers configuration for TWA (Trusted Web Activity) compatibility on Android (`assetlinks.json`).

---

## 3. All Functionalities & Capabilities

### Authentication & User Management
- **OTP-based Login Simulation:** Hassle-free login system utilizing a mobile number without requiring conventional emails or passwords.
- **Auto User Creation:** Users logging in with a new 10-digit number automatically get a new account created and are guided through onboarding.

### Student Management
- Complete CRUD (Create, Read, Update, Delete) capability for comprehensive student handling.
- Ability to save detailed student records including names, parent contact numbers, and specific enrolled batches.

### Batch Organization
- Seamless creation and grouping of students into identifiable batches (e.g., "Class 10 PCM", "Evening Math").
- Time scheduling for each batch with defined start/end timings and selected days of the week.

### Attendance Tracker
- Intuitive, single-tap interface for marking and reviewing daily student attendance.
- Data is logged historically, enabling future integration of attendance metrics and reporting.

### Homework & Content Sharing
- **Rich Homework Assignment:** Tutors can draft homework details comprising text, titles, YouTube URLs, and image URLs.
- **Assignment Distribution:** Homework can be shared entirely with an entire batch or precisely with individual students.
- **Direct WhatsApp Integration:** Automated formatted text links to share assigned homework directly to parent WhatsApp numbers with one click.

### Automated Notifications & Reminders
- **FCM Web Push:** Native web push notifications sent using Firebase to subscribed tutors/users on their devices (mobile/desktop).
- **Scheduled Background Reminders:** Five-minute interval background cron jobs exist to intelligently ascertain and dispatch pending push alerts (e.g., "Class reminder", "Attendance not marked" reminders).

### Premium (Pro Tier) Features (Currently Locked in MVP)
- Specialized locked pages intended for advanced Payment Management System.
- Pre-planned functionalities including automated UPI fee collection tracking and digital payment receipts.

---

## 4. Database Schema Overview
The SQLite database stores information using deeply correlated tables:
1. **`users`**: Details about the tutor (mobile, name, address, role, onboarding status).
2. **`batches`**: Batch groupings mapped to `user_id` alongside scheduling criteria.
3. **`students`**: Linkages distinguishing parent details mapped to distinct `batch_id` and `user_id`.
4. **`attendance`**: Daily log correlating `student_id`, boolean `present` flags, specific date, and linked to the active `user_id`.
5. **`homework`**: Assignments mapping payload content, URLs, and assignment scope (whether specific to `student_id` or `batch_id`).
6. **`push_subscriptions`**: Contains JSON configurations mapping the tutor's browser notification permission endpoints to allow FCM functionality.

---

## 5. Directory Structure Synopsis
- **`/app.py`**: Principal Flask file defining app context, scheduled contexts, and routing blueprint aggregations.
- **`/blueprints/`**: Logical modules segmenting the routes logically (`auth.py`, `students.py`, `batches.py`, `attendance.py`, `homework.py`, `payments.py`, `reports.py`).
- **`/templates/`**: Holds HTML Jinja macros shaping the UI (`base.html` defines the overarching CSS and JS logic injections).
- **`/static/`**: Hosts persistent statics - vanilla JS scripts (like `push-notifications.js`), generic global CSS paradigms, image assets, and PWA manifest configurations.
- **`/docs/`**: Extensive internal technical project documentation markdown libraries.
- **`/jobs.py` & `/utils/`**: Helper components isolating background processes (like push notifications delivery limits) and general logic checks.
