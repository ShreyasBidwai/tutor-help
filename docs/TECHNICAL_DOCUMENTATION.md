# TuitionTrack - Complete Technical Documentation

**Version:** 1.0.0  
**Last Updated:** December 2025  
**Status:** Production Ready

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Architecture](#system-architecture)
3. [Technology Stack](#technology-stack)
4. [Database Schema](#database-schema)
5. [API Endpoints](#api-endpoints)
6. [Features & Functionality](#features--functionality)
7. [Security Implementation](#security-implementation)
8. [Performance Optimizations](#performance-optimizations)
9. [Deployment Architecture](#deployment-architecture)
10. [Development Setup](#development-setup)
11. [Testing & Quality Assurance](#testing--quality-assurance)
12. [Monitoring & Logging](#monitoring--logging)
13. [Future Enhancements](#future-enhancements)

---

## Executive Summary

TuitionTrack is a comprehensive Progressive Web Application (PWA) designed for home tutors in India to manage their tutoring business efficiently. Built with Flask (Python) and SQLite, it provides a complete solution for student management, attendance tracking, homework distribution, and reporting.

### Key Technical Highlights

- **Architecture**: Monolithic Flask application with modular blueprint structure
- **Database**: SQLite with WAL mode for concurrent access
- **Frontend**: Server-side rendered templates with vanilla JavaScript
- **PWA**: Full Progressive Web App with offline capabilities
- **AI Integration**: RAG-powered help bot using TF-IDF, FAISS, and Google Gemini
- **Real-time**: Push notifications via Web Push API
- **Mobile-First**: Responsive design optimized for mobile devices
- **APK Ready**: Trusted Web Activity (TWA) compatible for Android APK generation

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Client (Browser/Mobile)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Web App    │  │  PWA/APK     │  │ Service Worker│      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTPS
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Flask Application (Gunicorn)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Blueprints │  │   Utils      │  │   Config     │      │
│  │   (Routes)   │  │   (Helpers)  │  │   (Settings) │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   SQLite     │  │  File System │  │  External    │
│   Database   │  │  (Uploads)   │  │  APIs        │
│              │  │              │  │  (Gemini)    │
└──────────────┘  └──────────────┘  └──────────────┘
```

### Application Structure

```
tutor-help/
├── app.py                    # Main Flask application
├── config.py                 # Configuration settings
├── database.py               # Database connection & utilities
├── gunicorn_config.py        # Production server config
├── requirements.txt          # Python dependencies
├── start.sh                  # Production startup script
│
├── blueprints/               # Modular route handlers
│   ├── auth.py              # Authentication & user management
│   ├── dashboard.py         # Dashboard & statistics
│   ├── students.py          # Student CRUD operations
│   ├── batches.py           # Batch management
│   ├── attendance.py        # Attendance tracking
│   ├── homework.py          # Homework management
│   ├── reports.py           # Attendance reports & analytics
│   ├── student.py           # Student portal
│   ├── payments.py           # Payment management (locked)
│   ├── export.py            # CSV export functionality
│   └── help_bot.py          # AI help bot API
│
├── utils/                    # Utility modules
│   ├── __init__.py          # Utility functions
│   ├── push_notifications.py # Push notification service
│   └── rag_system.py        # RAG AI system
│
├── templates/                # Jinja2 templates
│   ├── base.html            # Base template
│   ├── auth/                # Authentication pages
│   ├── dashboard/           # Dashboard pages
│   ├── students/            # Student management
│   ├── batches/             # Batch management
│   ├── attendance/          # Attendance pages
│   ├── homework/            # Homework pages
│   ├── reports/             # Report pages
│   ├── student/             # Student portal
│   ├── payments/            # Payment pages
│   └── errors/              # Error pages
│
├── static/                   # Static assets
│   ├── css/                 # Stylesheets
│   ├── js/                  # JavaScript files
│   │   ├── service-worker.js # PWA service worker
│   │   ├── push-notifications.js # Push notification client
│   │   ├── help-bot.js      # AI help bot UI
│   │   ├── form-validation.js # Form validation
│   │   └── ...
│   ├── manifest.json        # PWA manifest
│   └── *.png                # App icons & images
│
├── data/                     # Data files
│   ├── niya_qa_pairs.json   # RAG Q&A pairs
│   ├── niya_faiss.index     # FAISS vector index
│   ├── niya_embeddings.pkl  # TF-IDF embeddings
│   └── niya_vectorizer.pkl  # TF-IDF vectorizer
│
├── uploads/                  # User uploads
│   └── homework/             # Homework files
│
└── docs/                     # Documentation
    ├── PRODUCTION_SETUP.md
    ├── SETUP_INSTRUCTIONS.md
    ├── AI_FALLBACK_SYSTEM.md
    └── SQLITE_OPTIMIZATIONS.md
```

### Request Flow

1. **Client Request** → Browser/PWA sends HTTP request
2. **Gunicorn** → WSGI server receives request
3. **Flask App** → Routes request to appropriate blueprint
4. **Blueprint** → Processes request, queries database
5. **Database** → SQLite returns data
6. **Template Rendering** → Jinja2 renders HTML
7. **Response** → Returns HTML/JSON to client

---

## Technology Stack

### Backend

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Framework** | Flask | 3.0.0 | Web framework |
| **WSGI Server** | Gunicorn | 21.2.0 | Production server |
| **Database** | SQLite | 3.x | Embedded database |
| **Language** | Python | 3.10+ | Programming language |

### Frontend

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Templating** | Jinja2 | Server-side rendering |
| **Styling** | CSS3 | Responsive design |
| **Scripting** | Vanilla JavaScript | Client-side interactivity |
| **PWA** | Service Workers | Offline capabilities |
| **Icons** | PNG (Multiple sizes) | App icons |

### AI & Machine Learning

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Vector Search** | FAISS | 1.13.1 | Similarity search |
| **Text Processing** | scikit-learn | ≥1.5.1 | TF-IDF vectorization |
| **AI Models** | Google Gemini | 0.3.1 | Natural language generation |
| **Numeric Computing** | NumPy | ≥1.26.0 | Array operations |

### Push Notifications

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Protocol** | Web Push API | Browser push notifications |
| **Library** | pywebpush | 1.14.0 | Server-side push |
| **Encryption** | VAPID | Authentication |

### Development Tools

| Tool | Purpose |
|------|---------|
| **python-dotenv** | Environment variable management |
| **Git** | Version control |
| **Render/Railway** | Cloud hosting |

---

## Database Schema

### Tables Overview

#### 1. `users` Table
Stores tutor/user account information.

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mobile TEXT UNIQUE NOT NULL,
    tutor_name TEXT,
    tuition_name TEXT,
    address TEXT,
    role TEXT DEFAULT 'tutor',
    onboarding_completed INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Fields:**
- `id`: Primary key
- `mobile`: Unique 10-digit mobile number (authentication)
- `tutor_name`: Tutor's personal name
- `tuition_name`: Tuition center name
- `address`: Physical address
- `role`: User role ('tutor', 'student', 'enterprise')
- `onboarding_completed`: Boolean flag for onboarding status
- `created_at`: Account creation timestamp

**Indexes:**
- Unique index on `mobile`

#### 2. `batches` Table
Stores batch/class information.

```sql
CREATE TABLE batches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    start_time TEXT,
    end_time TEXT,
    days TEXT,
    notifications_enabled INTEGER DEFAULT 1,
    user_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

**Fields:**
- `id`: Primary key
- `name`: Batch name (e.g., "Class 10 PCM")
- `description`: Optional batch description
- `start_time`: Class start time (HH:MM format)
- `end_time`: Class end time (HH:MM format)
- `days`: Comma-separated days (e.g., "mo,tu,we,th,fr")
- `notifications_enabled`: Boolean for push notifications
- `user_id`: Foreign key to `users` table
- `created_at`: Creation timestamp

**Indexes:**
- Index on `user_id`

#### 3. `students` Table
Stores student information.

```sql
CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    batch_id INTEGER NOT NULL,
    address TEXT,
    school_name TEXT,
    standard TEXT,
    user_id INTEGER NOT NULL,
    last_attendance_notification TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (batch_id) REFERENCES batches (id),
    FOREIGN KEY (user_id) REFERENCES users (id),
    UNIQUE(user_id, phone)
);
```

**Fields:**
- `id`: Primary key
- `name`: Student name
- `phone`: Parent's 10-digit phone number
- `batch_id`: Foreign key to `batches`
- `address`: Student address
- `school_name`: School name
- `standard`: Class/standard (e.g., "10th", "12th")
- `user_id`: Foreign key to `users` (tutor)
- `last_attendance_notification`: Last notification timestamp
- `created_at`: Creation timestamp

**Indexes:**
- Unique index on `(user_id, phone)`
- Index on `batch_id`
- Index on `user_id`

#### 4. `attendance` Table
Tracks daily attendance records.

```sql
CREATE TABLE attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    date DATE NOT NULL,
    present INTEGER DEFAULT 1,
    status INTEGER DEFAULT 1,
    user_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students (id),
    FOREIGN KEY (user_id) REFERENCES users (id),
    UNIQUE(student_id, date)
);
```

**Fields:**
- `id`: Primary key
- `student_id`: Foreign key to `students`
- `date`: Attendance date (YYYY-MM-DD)
- `present`: Legacy field (0=absent, 1=present)
- `status`: New status field (0=absent, 1=present, 2=late)
- `user_id`: Foreign key to `users` (tutor)
- `created_at`: Record creation timestamp

**Indexes:**
- Unique index on `(student_id, date)`
- Index on `user_id`
- Index on `date`

#### 5. `homework` Table
Stores homework assignments.

```sql
CREATE TABLE homework (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    content TEXT,
    batch_id INTEGER,
    student_id INTEGER,
    file_path TEXT,
    youtube_url TEXT,
    submission_date DATE,
    user_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (batch_id) REFERENCES batches (id),
    FOREIGN KEY (student_id) REFERENCES students (id),
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

**Fields:**
- `id`: Primary key
- `title`: Homework title
- `description`: Optional description
- `content`: Homework content/text
- `batch_id`: Foreign key to `batches` (if batch-wide)
- `student_id`: Foreign key to `students` (if individual)
- `file_path`: Path to uploaded file
- `youtube_url`: Optional YouTube video URL
- `submission_date`: Due date for submission
- `user_id`: Foreign key to `users` (tutor)
- `created_at`: Creation timestamp

**Indexes:**
- Index on `batch_id`
- Index on `student_id`
- Index on `user_id`
- Index on `submission_date`

#### 6. `push_subscriptions` Table
Stores Web Push API subscriptions.

```sql
CREATE TABLE push_subscriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    endpoint TEXT NOT NULL UNIQUE,
    p256dh TEXT NOT NULL,
    auth TEXT NOT NULL,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

**Fields:**
- `id`: Primary key
- `user_id`: Foreign key to `users`
- `endpoint`: Web Push endpoint URL
- `p256dh`: Public key for encryption
- `auth`: Authentication secret
- `user_agent`: Browser user agent
- `created_at`: Subscription timestamp

**Indexes:**
- Unique index on `endpoint`
- Index on `user_id`

### Database Optimizations

#### WAL Mode (Write-Ahead Logging)
```python
PRAGMA journal_mode=WAL
```
- Enables concurrent reads and writes
- Better performance for multi-user scenarios
- Creates `.db-wal` and `.db-shm` files

#### Performance PRAGMAs
```python
PRAGMA synchronous=NORMAL      # Faster than FULL, still safe
PRAGMA cache_size=-64000      # 64MB cache (adjustable)
PRAGMA temp_store=MEMORY      # Store temp tables in RAM
PRAGMA mmap_size=268435456    # 256MB memory-mapped I/O
PRAGMA foreign_keys=ON        # Referential integrity
```

#### Indexes
- All foreign keys indexed
- Unique constraints on critical fields
- Composite indexes for common queries

---

## API Endpoints

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/` | Welcome page | No |
| GET | `/welcome` | Welcome page | No |
| GET | `/login` | Login page | No |
| POST | `/login` | Process login (mobile) | No |
| GET | `/signup` | Signup page | No |
| POST | `/signup` | Create account | No |
| GET | `/student/login` | Student login page | No |
| POST | `/student/login` | Student login | No |
| GET | `/logout` | Logout user | Yes |
| GET | `/profile` | View/edit profile | Yes |
| POST | `/profile` | Update profile | Yes |

### Dashboard Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/dashboard` | Main dashboard | Yes |
| POST | `/api/onboarding/complete` | Complete onboarding | Yes |
| GET | `/api/batches/upcoming` | Get upcoming batches | Yes |

### Student Management Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/students` | List students | Yes |
| GET | `/students/add` | Add student form | Yes |
| POST | `/students/add` | Create student | Yes |
| GET | `/students/<id>/edit` | Edit student form | Yes |
| POST | `/students/<id>/edit` | Update student | Yes |
| GET | `/students/<id>` | View student details | Yes |
| DELETE | `/api/students/<id>` | Delete student | Yes |

### Batch Management Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/batches` | List batches | Yes |
| GET | `/batches/add` | Add batch form | Yes |
| POST | `/batches/add` | Create batch | Yes |
| GET | `/batches/<id>/edit` | Edit batch form | Yes |
| POST | `/batches/<id>/edit` | Update batch | Yes |
| GET | `/batches/<id>/students` | View batch students | Yes |
| DELETE | `/api/batches/<id>` | Delete batch | Yes |

### Attendance Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/attendance` | Attendance page | Yes |
| POST | `/api/attendance/mark` | Mark attendance | Yes |

### Homework Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/homework` | List homework | Yes |
| GET | `/homework/share` | Share homework form | Yes |
| POST | `/homework/share` | Create homework | Yes |
| GET | `/homework/<id>/edit` | Edit homework form | Yes |
| POST | `/homework/<id>/edit` | Update homework | Yes |
| DELETE | `/api/homework/<id>` | Delete homework | Yes |
| GET | `/uploads/homework/<filename>` | Download file | Yes |

### Reports Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/reports` | Reports page | Yes |
| GET | `/reports/batch/<id>` | Batch report detail | Yes |
| GET | `/reports/student/<id>` | Student report detail | Yes |

### Export Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/export/students` | Export students CSV | Yes |
| GET | `/export/attendance` | Export attendance CSV | Yes |
| GET | `/export/reports/batch/<id>` | Export batch report CSV | Yes |

### Student Portal Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/student/dashboard` | Student dashboard | Yes (Student) |
| GET | `/student/attendance` | Student attendance view | Yes (Student) |
| GET | `/student/homework` | Student homework view | Yes (Student) |
| GET | `/student/profile` | Student profile | Yes (Student) |
| GET | `/api/student/homework/reminders` | Get homework reminders | Yes (Student) |
| GET | `/api/student/attendance/notifications` | Get attendance notifications | Yes (Student) |

### Push Notification Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/push/subscribe` | Subscribe to push | Yes |
| POST | `/api/push/unsubscribe` | Unsubscribe from push | Yes |

### Help Bot (AI) Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/help-bot/query` | Query AI help bot | Yes |

### System Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/health` | Health check | No |
| GET | `/manifest.json` | PWA manifest | No |
| GET | `/.well-known/assetlinks.json` | TWA asset links | No |

---

## Features & Functionality

### 1. Authentication System

#### Tutor Authentication
- **Mobile-based login**: 10-digit mobile number authentication
- **Auto-signup**: New users automatically created on first login
- **Session management**: Flask sessions with secure cookies
- **OTP simulation**: Auto-login for development (production-ready for SMS integration)

#### Student Authentication
- **Separate login portal**: `/student/login`
- **Mobile + password**: Student-specific credentials
- **Role-based access**: Separate student dashboard and features

#### Security Features
- **Session cookies**: HTTPOnly, Secure (HTTPS), SameSite=Lax
- **24-hour sessions**: Automatic expiration
- **Role-based routing**: Automatic redirects based on user role
- **Input validation**: Server-side validation on all forms

### 2. Dashboard

#### Tutor Dashboard
- **Statistics Overview**:
  - Total students count
  - Total batches count
  - Today's attendance count
  - Attendance percentage
  - Recent homework count
- **Quick Actions**:
  - Add new student
  - Create new batch
  - Mark attendance
  - Share homework
- **Upcoming Batches**: List of batches scheduled for today
- **Recent Activity**: Latest homework and attendance updates

#### Student Dashboard
- **Personal Statistics**:
  - Attendance calendar view
  - Homework assignments
  - Batch information
- **Quick Access**: Links to attendance, homework, profile

### 3. Student Management

#### Features
- **CRUD Operations**: Create, Read, Update, Delete students
- **Batch Assignment**: Assign students to batches
- **Search & Filter**: Search by name/phone, filter by batch
- **Pagination**: 20 students per page
- **Validation**:
  - Name: Letters and spaces only
  - Phone: 10-digit validation
  - Unique phone per tutor

#### Student Fields
- Name (required)
- Parent phone (required, unique)
- Batch (required)
- Address (optional)
- School name (optional)
- Standard/Class (optional)

### 4. Batch Management

#### Features
- **CRUD Operations**: Create, Read, Update, Delete batches
- **Schedule Configuration**:
  - Start time (HH:MM)
  - End time (HH:MM)
  - Class days (Monday-Sunday)
  - Daily option (select all days)
- **Notifications**: Enable/disable push notifications per batch
- **Batch Students View**: View all students in a batch
- **Validation**:
  - Name: 2-100 characters, allows numbers and special characters
  - Time validation: End time must be after start time

### 5. Attendance Tracking

#### Features
- **Date Selection**: Select any date (today, yesterday, or future)
- **Batch Filtering**: Filter students by batch (required)
- **Status Types**:
  - Present (status=1)
  - Absent (status=0)
  - Late (status=2)
- **Batch Timing Validation**: Cannot mark attendance before batch start time
- **Per-Batch Tracking**: Attendance status tracked per batch
- **Visual Indicators**: Color-coded status (green=present, red=absent, orange=late)
- **Auto-save**: Attendance saved automatically on toggle

#### Business Logic
- **Time-based restrictions**: Attendance can only be marked if batch has started (IST)
- **Date restrictions**: Can mark for today and yesterday only
- **Duplicate prevention**: One attendance record per student per date
- **Batch-specific**: Each batch's attendance tracked independently

### 6. Homework Management

#### Features
- **CRUD Operations**: Create, Read, Update, Delete homework
- **Distribution Options**:
  - Batch-wide: Share with entire batch
  - Individual: Share with specific student
- **Content Types**:
  - Text content
  - File uploads (PDF, images, documents)
  - YouTube video links
- **Submission Date**: Set due date for homework
- **Auto-expiry**: Homework expires after submission date
- **WhatsApp Integration**: Share homework via WhatsApp link
- **Pagination**: 20 homework items per page

#### File Upload
- **Supported formats**: PDF, PNG, JPG, JPEG, GIF, DOC, DOCX
- **Max size**: 10MB per file
- **Storage**: `uploads/homework/` directory
- **Security**: Filename sanitization, type validation

### 7. Attendance Reports

#### Batch Reports
- **Current Month Summary**: Statistics for current month
- **Daily Statistics**: Present/Absent/Late counts per day
- **Date Selection**: Select any date in current month
- **Student Filtering**: Filter by status (All, Present, Absent, Late)
- **Visual Cards**: Small cube-style cards with transparent backgrounds
- **Export**: CSV export functionality

#### Student Reports
- **Individual Statistics**: Per-student attendance tracking
- **Monthly Summary**: Current month attendance percentage
- **Present Days**: Count of days marked present
- **Total Class Days**: Based on batch schedule
- **Visual Indicators**: Avatar with initial, status dots

#### Report Features
- **Real-time Calculation**: Based on batch schedule and attendance records
- **Schedule-aware**: Only counts days when batch has classes
- **Date Range**: Current month (up to today)
- **Export Options**: CSV export for all reports

### 8. Export Functionality

#### CSV Exports
- **Students Export**: All student data with batch information
- **Attendance Export**: Attendance records with date range filtering
- **Batch Report Export**: Detailed batch attendance report
- **Mobile-friendly**: Optimized for mobile downloads

#### Export Fields
- **Students**: Name, Phone, Batch, Standard, School, Address, Added Date
- **Attendance**: Date, Student Name, Batch, Status
- **Batch Report**: Student Name, Phone, Total Days, Present, Late, Absent, Attendance %

### 9. Student Portal

#### Features
- **Separate Interface**: Student-specific UI
- **Attendance Calendar**: Visual calendar view of attendance
- **Homework List**: View assigned homework
- **Profile View**: View personal information
- **Notifications**: Push notifications for homework and attendance

#### Access Control
- **Role-based**: Only students can access student portal
- **Auto-redirect**: Tutors redirected to tutor dashboard
- **Session-based**: Uses same authentication system

### 10. Push Notifications

#### Features
- **Web Push API**: Browser-native push notifications
- **VAPID Protocol**: Secure push notification authentication
- **Auto-subscribe**: Automatic permission request on login
- **Notification Types**:
  - Attendance reminders (15 minutes before batch)
  - Homework assignments
  - Attendance marked notifications
- **Smart Display**:
  - SweetAlert when app is open
  - Native push when app is closed
- **Multi-device**: Supports multiple devices per user

#### Technical Implementation
- **Service Worker**: Handles push events
- **Subscription Management**: Store subscriptions in database
- **Retry Logic**: Automatic retry on failure
- **Error Handling**: Graceful degradation if push unavailable

### 11. AI Help Bot (Niya)

#### Features
- **RAG System**: Retrieval-Augmented Generation
- **TF-IDF Vectorization**: Lightweight text processing
- **FAISS Index**: Fast similarity search
- **Google Gemini Integration**: Natural language generation
- **Multi-model Fallback**: Automatic model switching on rate limits
- **Role-aware**: Different responses for tutors vs students
- **Floating Icon**: Always-accessible help button
- **Fullscreen Chat**: Immersive chat interface

#### AI Models (Priority Order)
1. **gemini-2.5-flash** (Primary): 5 RPM, 250K TPM, 20 RPD
2. **gemini-2.5-flash-lite** (Fallback 1): 10 RPM, 250K TPM, 20 RPD
3. **gemma-3-1b** (Fallback 2): 30 RPM, 15K TPM, 14.4K RPD
4. **gemma-3-2b** (Fallback 3): 30 RPM, 15K TPM, 14.4K RPD
5. **gemma-3-4b** (Fallback 4): 30 RPM, 15K TPM, 14.4K RPD

#### RAG Process
1. **Query Processing**: User question → TF-IDF vector
2. **Similarity Search**: Find top 3 similar Q&A pairs (FAISS)
3. **Context Building**: Use similar Q&As as context
4. **AI Generation**: Send to Gemini with context
5. **Response**: Return AI-generated answer

#### Knowledge Base
- **82 Q&A Pairs**: Comprehensive coverage of features
- **Categories**: Getting started, Attendance, Students, Batches, Homework, Reports, Troubleshooting
- **Role-specific**: Different content for tutors and students

### 12. Progressive Web App (PWA)

#### Features
- **Installable**: "Add to Home Screen" functionality
- **Offline Support**: Service worker caching
- **App-like Experience**: Standalone display mode
- **Icons**: Multiple sizes (48x48 to 512x512)
- **Manifest**: Complete PWA manifest
- **Service Worker**: Caching and offline functionality

#### Service Worker Capabilities
- **Static Caching**: Cache app icons, logos, core JS
- **Dynamic Caching**: Cache API responses
- **Push Notifications**: Handle push events
- **Offline Fallback**: Show cached content when offline

### 13. Trusted Web Activity (TWA)

#### Features
- **APK Generation**: Can be converted to Android APK
- **Fullscreen Mode**: No browser UI when installed
- **Asset Links**: Android verification file
- **Manifest**: Root-level manifest for TWA compatibility
- **Absolute URLs**: All URLs use full HTTPS paths

### 14. Payment Management (Locked Feature)

#### Features
- **Freemium Model**: Free tier with locked Pro features
- **Payment Page**: Showcase Pro tier benefits
- **Pricing**: ₹99/month (displayed, not implemented)
- **Future Features**: Payment gateway integration planned

---

## Security Implementation

### Authentication Security

#### Session Management
```python
SESSION_COOKIE_HTTPONLY = True      # Prevent XSS
SESSION_COOKIE_SECURE = True         # HTTPS only
SESSION_COOKIE_SAMESITE = 'Lax'      # CSRF protection
PERMANENT_SESSION_LIFETIME = 86400   # 24 hours
```

#### Input Validation
- **Server-side validation**: All inputs validated on server
- **SQL injection prevention**: Parameterized queries
- **XSS prevention**: Jinja2 auto-escaping
- **CSRF protection**: SameSite cookies

#### File Upload Security
- **Type validation**: Whitelist of allowed extensions
- **Size limits**: 10MB maximum
- **Filename sanitization**: Secure filename generation
- **Path validation**: Prevent directory traversal

### Database Security

#### SQL Injection Prevention
- **Parameterized queries**: All queries use placeholders
- **Input sanitization**: All user inputs sanitized
- **Type checking**: Strict type validation

#### Access Control
- **User isolation**: All queries filtered by `user_id`
- **Foreign key constraints**: Referential integrity
- **Role-based access**: Different features for different roles

### API Security

#### Authentication
- **Session-based**: All API endpoints require login
- **Role verification**: Student endpoints check student role
- **CSRF tokens**: SameSite cookies prevent CSRF

#### Rate Limiting
- **AI API**: Built-in rate limit handling with fallback
- **Database**: Connection timeout prevents resource exhaustion

### Environment Variables

#### Sensitive Data
- **SECRET_KEY**: Flask session encryption
- **VAPID keys**: Push notification authentication
- **GEMINI_API_KEY**: AI API access
- **Database**: Not exposed in code

#### Configuration
- **.env file**: Local development
- **Environment variables**: Production deployment
- **.gitignore**: Prevents committing secrets

---

## Performance Optimizations

### Database Optimizations

#### WAL Mode
- **Concurrent access**: Multiple readers, one writer
- **Better performance**: Faster than default journal mode
- **Reduced locking**: Readers don't block writers

#### PRAGMA Settings
```python
PRAGMA synchronous=NORMAL      # Balance speed and safety
PRAGMA cache_size=-64000       # 64MB cache
PRAGMA temp_store=MEMORY       # RAM for temp tables
PRAGMA mmap_size=268435456     # 256MB memory mapping
```

#### Indexes
- **Foreign keys**: All foreign keys indexed
- **Unique constraints**: Prevent duplicates efficiently
- **Query optimization**: Indexes on frequently queried fields

#### Connection Management
- **Connection pooling**: Reuse connections
- **Timeout handling**: 30-second timeout with retry
- **Retry logic**: Automatic retry on database locks

### Application Optimizations

#### Caching
- **Static assets**: Service worker caching
- **Database queries**: Efficient query design
- **Template caching**: Jinja2 template caching

#### Pagination
- **Large datasets**: 20 items per page
- **Efficient queries**: LIMIT/OFFSET optimization
- **Page validation**: Prevent invalid page numbers

#### Lazy Loading
- **RAG system**: Load index on demand
- **Images**: Lazy loading for large images
- **JavaScript**: Deferred loading where possible

### Frontend Optimizations

#### Asset Optimization
- **Image sizes**: Multiple icon sizes for different devices
- **CSS minification**: Production-ready CSS
- **JavaScript**: Optimized vanilla JS (no frameworks)

#### Mobile Optimization
- **Responsive design**: Mobile-first approach
- **Touch targets**: Minimum 44px touch targets
- **Viewport**: Optimized viewport settings

---

## Deployment Architecture

### Production Server Configuration

#### Gunicorn Configuration
```python
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2
```

#### Recommended Server Specs

| Tier | RAM | CPU | Workers | Capacity |
|------|-----|-----|---------|----------|
| **Minimum** | 1GB | 0.5 | 2 | 10-15 tutors, 30-50 students |
| **Recommended** | 2GB | 1.0 | 3 | 30-50 tutors, 100-150 students |
| **Optimal** | 4GB | 2.0 | 5 | 100+ tutors, 300+ students |

### Deployment Platforms

#### Render.com
- **Free tier**: 512MB RAM, 0.1 CPU (limited)
- **Starter**: 1GB RAM, 0.5 CPU ($7/month)
- **Standard**: 2GB RAM, 1.0 CPU ($25/month)

#### Railway.app
- **Hobby**: 1GB RAM, 0.5 CPU ($5/month)
- **Pro**: 2GB RAM, 1.0 CPU ($20/month)

### Environment Setup

#### Required Environment Variables
```bash
SECRET_KEY=<generated-secret-key>
FLASK_DEBUG=False
VAPID_PUBLIC_KEY=<generated-public-key>
VAPID_PRIVATE_KEY=<generated-private-key>
VAPID_CLAIM_EMAIL=<your-email>
GEMINI_API_KEY=<google-gemini-api-key>
SESSION_COOKIE_SECURE=True
DATABASE=tutor_app.db
```

#### Build Process
1. Install dependencies: `pip install -r requirements.txt`
2. Initialize database: `python3 -c "from database import init_db, migrate_db, add_indexes; migrate_db(); add_indexes()"`
3. Build RAG index: `python3 build_rag_index.py`
4. Start server: `gunicorn -c gunicorn_config.py app:app`

### Health Monitoring

#### Health Check Endpoint
- **URL**: `/health`
- **Response**: JSON with status, service name, version
- **Use case**: Load balancer health checks, monitoring

#### Logging
- **Access logs**: All HTTP requests logged
- **Error logs**: Exceptions and errors logged
- **Format**: Structured logging with timestamps

---

## Development Setup

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)
- Git (version control)

### Local Development

#### 1. Clone Repository
```bash
git clone <repository-url>
cd tutor-help
```

#### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Generate Keys
```bash
# Generate SECRET_KEY
python3 generate_secret_key.py

# Generate VAPID keys
python3 generate_vapid_keys.py
```

#### 5. Configure Environment
```bash
cp .env.example .env
# Edit .env with generated keys and API keys
```

#### 6. Initialize Database
```bash
python3 -c "from database import init_db, migrate_db, add_indexes; migrate_db(); add_indexes()"
```

#### 7. Build RAG Index
```bash
python3 build_rag_index.py
```

#### 8. Run Application
```bash
python app.py
# Or for production-like:
gunicorn -c gunicorn_config.py app:app
```

#### 9. Access Application
- Open browser: `http://localhost:5000`
- Login with any 10-digit mobile number

### Development Tools

#### Database Management
```bash
# Clean database
python3 clean_db.py

# Populate with sample data
python3 populate_db.py
```

#### Code Structure
- **Blueprints**: Modular route handlers
- **Utils**: Reusable utility functions
- **Templates**: Jinja2 HTML templates
- **Static**: CSS, JavaScript, images

---

## Testing & Quality Assurance

### Manual Testing Checklist

#### Authentication
- [ ] Tutor login with mobile number
- [ ] Student login with mobile + password
- [ ] Auto-signup for new users
- [ ] Session expiration (24 hours)
- [ ] Logout functionality
- [ ] Role-based redirects

#### Student Management
- [ ] Add student with validation
- [ ] Edit student details
- [ ] Delete student
- [ ] Search functionality
- [ ] Batch filtering
- [ ] Pagination

#### Batch Management
- [ ] Create batch with schedule
- [ ] Edit batch details
- [ ] Delete batch
- [ ] Batch students view
- [ ] Time validation

#### Attendance
- [ ] Mark present/absent/late
- [ ] Date selection
- [ ] Batch filtering
- [ ] Time-based restrictions
- [ ] Per-batch tracking

#### Homework
- [ ] Create homework (batch/individual)
- [ ] File upload
- [ ] YouTube link
- [ ] Edit/delete homework
- [ ] Auto-expiry

#### Reports
- [ ] Batch reports
- [ ] Student reports
- [ ] Date filtering
- [ ] Status filtering
- [ ] CSV export

#### Push Notifications
- [ ] Subscribe to notifications
- [ ] Receive notifications
- [ ] Unsubscribe
- [ ] Multiple devices

#### AI Help Bot
- [ ] Query processing
- [ ] RAG retrieval
- [ ] AI generation
- [ ] Model fallback
- [ ] Role-aware responses

### Performance Testing

#### Load Testing
- **Concurrent users**: Test with 10, 50, 100 users
- **Database queries**: Monitor query performance
- **Response times**: Target <1 second for most requests
- **Memory usage**: Monitor RAM consumption

#### Stress Testing
- **Database locks**: Test concurrent writes
- **AI API limits**: Test rate limit handling
- **File uploads**: Test large file handling
- **Pagination**: Test with large datasets

---

## Monitoring & Logging

### Application Logging

#### Log Levels
- **INFO**: General application flow
- **WARNING**: Non-critical issues
- **ERROR**: Exceptions and errors
- **DEBUG**: Detailed debugging (development only)

#### Log Format
```
%(asctime)s %(levelname)s %(name)s %(message)s
```

#### Logged Events
- HTTP requests (access logs)
- Database operations
- AI API calls
- Push notification sends
- Errors and exceptions

### Monitoring Endpoints

#### Health Check
- **Endpoint**: `/health`
- **Response**: `{"status": "healthy", "service": "TuitionTrack", "version": "1.0.0"}`
- **Use**: Load balancer health checks

### Error Tracking

#### Error Handlers
- **404**: Custom 404 page
- **500**: Custom 500 page with error logging
- **Database errors**: Retry logic with logging
- **API errors**: Graceful error messages

---

## Future Enhancements

### Planned Features

#### Payment Integration
- UPI payment gateway
- Automated fee collection
- Digital receipts
- Payment reminders

#### Advanced Notifications
- SMS integration
- WhatsApp Business API
- Email notifications
- Custom notification schedules

#### Enhanced Reporting
- Advanced analytics
- Performance trends
- Comparative reports
- Custom date ranges

#### Mobile App
- Native iOS app
- Native Android app
- Offline-first architecture
- Push notifications

#### Enterprise Features
- Multi-tutor support
- Branch management
- Advanced permissions
- White-labeling

### Technical Improvements

#### Database Migration
- PostgreSQL support
- Database replication
- Automated backups
- Data export/import

#### Performance
- Redis caching
- CDN for static assets
- Database query optimization
- API response caching

#### Security
- Two-factor authentication
- OAuth integration
- Advanced rate limiting
- Security audit logging

---

## Appendix

### A. File Structure Reference

See [System Architecture](#system-architecture) section for complete file structure.

### B. Environment Variables Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `SECRET_KEY` | Yes | Flask session secret | `generated-hex-string` |
| `FLASK_DEBUG` | No | Debug mode | `False` |
| `VAPID_PUBLIC_KEY` | Yes | Push notification public key | `base64url-string` |
| `VAPID_PRIVATE_KEY` | Yes | Push notification private key | `base64url-string` |
| `VAPID_CLAIM_EMAIL` | Yes | VAPID claim email | `your@email.com` |
| `GEMINI_API_KEY` | Yes | Google Gemini API key | `your-api-key` |
| `SESSION_COOKIE_SECURE` | No | HTTPS-only cookies | `True` |
| `DATABASE` | No | Database filename | `tutor_app.db` |

### C. API Response Formats

#### Success Response
```json
{
  "success": true,
  "data": {...}
}
```

#### Error Response
```json
{
  "success": false,
  "error": "Error message"
}
```

#### Help Bot Response
```json
{
  "query": "user question",
  "similarity_scores": [0.85, 0.78, 0.72],
  "used_rag": true,
  "response": "AI generated response",
  "rag_context": ["relevant questions"],
  "model_used": "gemini-2.5-flash"
}
```

### D. Database Connection String

```python
# SQLite connection
sqlite3.connect('tutor_app.db', timeout=30.0)
```

### E. Supported File Types

#### Homework Uploads
- PDF: `.pdf`
- Images: `.png`, `.jpg`, `.jpeg`, `.gif`
- Documents: `.doc`, `.docx`

#### Maximum File Size
- 10MB per file

---

## Version History

### Version 1.0.0 (December 2025)
- Initial production release
- Complete feature set
- PWA and TWA support
- AI help bot integration
- Push notifications
- Production-ready deployment

---

## Support & Contact

For technical support, issues, or contributions:
- **Repository**: [GitHub URL]
- **Documentation**: See `docs/` directory
- **Issues**: Use GitHub Issues

---

**Document Status**: Complete  
**Last Reviewed**: December 2025  
**Next Review**: As needed

