# TuitionTrack - MVP for Home Tutors

A hyper-simple Progressive Web App (PWA) prototype built with Flask for individual home tutors in India. This MVP provides essential tools for managing students, tracking attendance, and sharing homework, with a freemium model featuring a locked payment management system.

## Features

### Free Tier (Fully Functional)

- **OTP-based Login Simulation**: Simple mobile number-based authentication (no email/password required)
- **Student Management**: Complete CRUD operations for student records
- **Batch Management**: Organize students into batches (e.g., "Class 10 PCM", "Class 12 Commerce")
- **Attendance Tracker**: Quick single-tap attendance marking for today's classes
- **Homework Sharing**: Share homework with students/batches, including text and image support with WhatsApp integration

### Pro Tier (Locked Feature)

- **Payment Management System**: Locked page showcasing automated UPI fee collection and digital receipts
- **Automated Reminders**: SMS/WhatsApp reminder system (feature preview)

## Technology Stack

- **Backend**: Python 3 + Flask (Micro-framework)
- **Database**: SQLite (zero-config, built-in)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript (mobile-first PWA design)

## Project Structure

```
tutor-help/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── tutor_app.db          # SQLite database (created on first run)
├── templates/            # HTML templates
│   ├── base.html         # Base template with PWA styling
│   ├── login.html        # Login page
│   ├── dashboard.html    # Main dashboard
│   ├── students.html     # Student list
│   ├── add_student.html  # Add student form
│   ├── edit_student.html # Edit student form
│   ├── batches.html      # Batch list
│   ├── add_batch.html    # Create batch form
│   ├── attendance.html   # Attendance tracker
│   ├── homework.html     # Homework list
│   ├── share_homework.html # Share homework form
│   └── payments_locked.html # Locked payment feature
└── static/               # Static files (CSS, JS, images)
```

## Database Schema

The application uses SQLite with the following tables:

- **users**: Stores user mobile numbers
- **batches**: Stores batch information (name, description)
- **students**: Stores student details (name, phone, batch_id)
- **attendance**: Tracks daily attendance (student_id, date, present)
- **homework**: Stores homework assignments (title, content, image_url, batch_id/student_id)

## Setup Instructions

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Installation Steps

1. **Clone or navigate to the project directory**:
   ```bash
   cd tutor-help
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   python app.py
   ```

5. **Access the application**:
   - Open your browser and navigate to: `http://localhost:5000`
   - The database (`tutor_app.db`) will be automatically created on first run

### First Time Setup

1. **Login**: Enter any 10-digit mobile number (e.g., `9876543210`)
   - The system will automatically create a new user account
   - OTP verification is simulated (auto-login)

2. **Create a Batch**: 
   - Navigate to Students → Add New Student
   - You'll be prompted to create a batch first
   - Or use the dashboard "Create Batch" button

3. **Add Students**: Add your students with their names and parent phone numbers

4. **Start Using**: 
   - Mark attendance daily
   - Share homework with students
   - Explore the locked payment feature

## Usage Guide

### Student Management

1. **Add Student**: Click "Add New Student" → Fill in name, parent phone, and select batch
2. **Edit Student**: Click "Edit" on any student → Modify details → Save
3. **Delete Student**: Click "Delete" on any student → Confirm deletion

### Attendance Tracking

1. Navigate to the **Attendance** tab
2. Toggle the switch next to each student to mark present/absent
3. Attendance is automatically saved for today's date

### Homework Sharing

1. Click **"Share New Homework"**
2. Enter title, content, and optionally an image URL
3. Select a batch or specific student
4. Click **"Share Homework"**
5. Use the **"Share via WhatsApp"** button to send homework to parents

### Payment Management (Locked)

- Navigate to the **Payments** tab to view the locked feature
- This showcases the Pro tier benefits (₹99/month)
- Feature is not implemented (prototype only)

## Mobile-First PWA Features

- **Responsive Design**: Optimized for mobile devices with thumb-friendly navigation
- **Touch Targets**: All buttons and interactive elements are at least 44px tall
- **Bottom Navigation**: Fixed bottom navigation bar for easy access
- **Sticky Header**: Fixed header with gradient design
- **PWA Meta Tags**: Configured for mobile app-like experience

## API Endpoints

### Authentication
- `GET /login` - Login page
- `POST /login` - Process login (mobile number)
- `GET /logout` - Logout user

### Students
- `GET /students` - List all students
- `GET /students/add` - Add student form
- `POST /students/add` - Create student
- `GET /students/<id>/edit` - Edit student form
- `POST /students/<id>/edit` - Update student
- `DELETE /api/students/<id>` - Delete student (API)

### Attendance
- `GET /attendance` - Attendance tracker page
- `POST /api/attendance/mark` - Mark attendance (API)

### Homework
- `GET /homework` - List all homework
- `GET /homework/share` - Share homework form
- `POST /homework/share` - Create homework

### Payments
- `GET /payments/locked` - Locked payment feature page

## Development Notes

- **Database**: SQLite database file is created automatically
- **Sessions**: Uses Flask sessions for authentication
- **OTP Simulation**: Login automatically succeeds with any valid 10-digit mobile number
- **File Uploads**: Currently supports image URLs only (not direct file uploads)

## Future Enhancements (Not Implemented)

- Actual OTP verification via SMS gateway
- Direct file upload for homework images
- Payment gateway integration for Pro tier
- SMS/WhatsApp API integration for reminders
- Payment tracking and receipt generation
- Advanced reporting and analytics

## License

This is a prototype/MVP for demonstration purposes.

## Support

For issues or questions, please refer to the code comments or Flask documentation.
