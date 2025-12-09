# Tutor Help - Code Structure

This document explains the modular structure of the Tutor Help application, designed to support tutor, student, and enterprise logins.

## Project Structure

```
tutor-help/
├── app.py                 # Main Flask application entry point
├── config.py              # Configuration settings
├── database.py            # Database connection and initialization
├── utils.py               # Utility functions (decorators, file handling)
├── requirements.txt       # Python dependencies
│
├── blueprints/            # Route modules organized by feature
│   ├── __init__.py
│   ├── auth.py           # Authentication (tutor, student, enterprise)
│   ├── dashboard.py      # Dashboard routes
│   ├── students.py       # Student management
│   ├── batches.py        # Batch management
│   ├── attendance.py     # Attendance tracking
│   ├── homework.py       # Homework sharing
│   ├── reports.py        # Attendance reports
│   └── payments.py       # Payment management
│
├── templates/            # HTML templates organized by feature
│   ├── base.html         # Base template with navigation
│   ├── auth/            # Authentication templates
│   │   ├── welcome.html
│   │   ├── login.html
│   │   ├── signup.html
│   │   ├── student_login.html
│   │   └── enterprise_login.html
│   ├── dashboard/
│   │   └── dashboard.html
│   ├── students/
│   │   ├── students.html
│   │   ├── add_student.html
│   │   ├── edit_student.html
│   │   └── view_student.html
│   ├── batches/
│   │   ├── batches.html
│   │   ├── add_batch.html
│   │   ├── edit_batch.html
│   │   └── batch_students.html
│   ├── attendance/
│   │   └── attendance.html
│   ├── homework/
│   │   ├── homework.html
│   │   ├── share_homework.html
│   │   └── edit_homework.html
│   ├── reports/
│   │   ├── reports.html
│   │   └── batch_report_detail.html
│   └── payments/
│       └── payments_locked.html
│
├── static/               # Static files (CSS, JS, images)
│   └── manifest.json    # PWA manifest
│
└── uploads/             # User-uploaded files
    └── homework/
```

## Key Components

### 1. Configuration (`config.py`)
- Centralized configuration settings
- Database path, upload settings, file extensions
- User roles: `ROLE_TUTOR`, `ROLE_STUDENT`, `ROLE_ENTERPRISE`

### 2. Database (`database.py`)
- Database connection management
- Schema initialization (`init_db()`)
- Migration support (`migrate_db()`) for adding new columns
- Supports backward compatibility during schema changes

### 3. Utilities (`utils.py`)
- `require_login`: Decorator for authentication
- `require_role`: Decorator for role-based access control
- `allowed_file`: File upload validation
- `get_secure_filename`: Secure filename generation

### 4. Blueprints

#### Auth Blueprint (`blueprints/auth.py`)
- `/` - Redirects to welcome or dashboard
- `/welcome` - Welcome page with role selection
- `/login` - Tutor login/signup
- `/signup` - Tutor registration (collects tuition name)
- `/student/login` - Student login (Coming Soon)
- `/enterprise/login` - Enterprise login (Coming Soon)
- `/logout` - Logout

#### Dashboard Blueprint (`blueprints/dashboard.py`)
- `/dashboard` - Main dashboard with stats and recent activity

#### Students Blueprint (`blueprints/students.py`)
- `/students` - List all students (with search/filter)
- `/students/add` - Add new student
- `/students/<id>/edit` - Edit student
- `/students/<id>` - View student details
- `/api/students/<id>` - Delete student (API)

#### Batches Blueprint (`blueprints/batches.py`)
- `/batches` - List all batches
- `/batches/add` - Create new batch
- `/batches/<id>/edit` - Edit batch
- `/batches/<id>/students` - View students in batch
- `/api/batches/<id>` - Delete batch (API)

#### Attendance Blueprint (`blueprints/attendance.py`)
- `/attendance` - Mark attendance (with date/batch filters)
- `/api/attendance/mark` - Mark attendance (API)

#### Homework Blueprint (`blueprints/homework.py`)
- `/homework` - List all homework
- `/homework/share` - Share homework
- `/homework/<id>/edit` - Edit homework
- `/uploads/<filename>` - Serve uploaded files
- `/api/homework/<id>` - Delete homework (API)

#### Reports Blueprint (`blueprints/reports.py`)
- `/reports` - Summary report (all batches, last 7 days)
- `/reports/batch/<id>` - Detailed batch report

#### Payments Blueprint (`blueprints/payments.py`)
- `/payments/locked` - Locked payment feature

## Adding New Features

### Adding a New Blueprint

1. Create a new file in `blueprints/` directory:
```python
from flask import Blueprint
from utils import require_login

my_feature_bp = Blueprint('my_feature', __name__, url_prefix='')

@my_feature_bp.route('/my-feature')
@require_login
def my_feature():
    return render_template('my_feature/index.html')
```

2. Register in `app.py`:
```python
from blueprints.my_feature import my_feature_bp
app.register_blueprint(my_feature_bp)
```

3. Create templates in `templates/my_feature/`

### Adding Student/Enterprise Login

The structure is already prepared for student and enterprise logins:

1. **Database**: Users table has a `role` column (default: 'tutor')
2. **Auth Blueprint**: Routes exist for `/student/login` and `/enterprise/login`
3. **Role-based Access**: Use `@require_role('student')` or `@require_role('enterprise')` decorators

Example:
```python
@students_bp.route('/student/dashboard')
@require_role(Config.ROLE_STUDENT)
def student_dashboard():
    # Student-specific dashboard
    pass
```

## Database Schema

### Users Table
- `id` - Primary key
- `mobile` - Unique mobile number
- `tuition_name` - Name of tuition/coaching (for tutors)
- `role` - User role ('tutor', 'student', 'enterprise')
- `created_at` - Timestamp

### Other Tables
- `batches` - Batch/class information
- `students` - Student records
- `attendance` - Attendance records (supports both `present` and `status` columns for migration)
- `homework` - Homework/notes shared with students

## Benefits of This Structure

1. **Modularity**: Each feature is in its own blueprint
2. **Maintainability**: Easy to find and update specific features
3. **Scalability**: Easy to add new features or user roles
4. **Organization**: Templates organized by feature
5. **Separation of Concerns**: Configuration, database, utilities separated
6. **Future-Ready**: Prepared for student and enterprise logins

## Running the Application

```bash
python app.py
```

The application will:
1. Initialize database if it doesn't exist
2. Run migrations if needed
3. Start Flask development server on `http://0.0.0.0:5000`

