from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory, flash
from datetime import datetime, date, timedelta
import sqlite3
import os
import secrets
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Database file path
DATABASE = 'tutor_app.db'

# Upload configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.join(UPLOAD_FOLDER, 'homework'), exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with required tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mobile TEXT UNIQUE NOT NULL,
            tuition_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Batches table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS batches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            start_time TEXT,
            end_time TEXT,
            days TEXT,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Students table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            batch_id INTEGER NOT NULL,
            address TEXT,
            school_name TEXT,
            standard TEXT,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (batch_id) REFERENCES batches (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Add new columns to existing students table if they don't exist
    try:
        cursor.execute('ALTER TABLE students ADD COLUMN address TEXT')
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    try:
        cursor.execute('ALTER TABLE students ADD COLUMN school_name TEXT')
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    try:
        cursor.execute('ALTER TABLE students ADD COLUMN standard TEXT')
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    # Attendance table
    # status: 0 = absent, 1 = present, 2 = late
    # Note: For backward compatibility, we support both 'present' and 'status' columns
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
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
        )
    ''')
    
    # Homework table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS homework (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT,
            file_path TEXT,
            youtube_url TEXT,
            batch_id INTEGER,
            student_id INTEGER,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (batch_id) REFERENCES batches (id),
            FOREIGN KEY (student_id) REFERENCES students (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def migrate_db():
    """Migrate existing database to add new columns"""
    if not os.path.exists(DATABASE):
        return
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if columns exist and add them if they don't
    cursor.execute("PRAGMA table_info(students)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'address' not in columns:
        try:
            cursor.execute('ALTER TABLE students ADD COLUMN address TEXT')
        except sqlite3.OperationalError:
            pass
    
    if 'school_name' not in columns:
        try:
            cursor.execute('ALTER TABLE students ADD COLUMN school_name TEXT')
        except sqlite3.OperationalError:
            pass
    
    if 'standard' not in columns:
        try:
            cursor.execute('ALTER TABLE students ADD COLUMN standard TEXT')
        except sqlite3.OperationalError:
            pass
    
    # Migrate users table: add tuition_name column
    cursor.execute("PRAGMA table_info(users)")
    user_columns = [row[1] for row in cursor.fetchall()]
    
    if 'tuition_name' not in user_columns:
        try:
            cursor.execute('ALTER TABLE users ADD COLUMN tuition_name TEXT')
        except sqlite3.OperationalError:
            pass
    
    # Migrate homework table: update columns
    cursor.execute("PRAGMA table_info(homework)")
    homework_columns = [row[1] for row in cursor.fetchall()]
    
    if 'file_path' not in homework_columns:
        try:
            cursor.execute('ALTER TABLE homework ADD COLUMN file_path TEXT')
        except sqlite3.OperationalError:
            pass
    
    if 'youtube_url' not in homework_columns:
        try:
            cursor.execute('ALTER TABLE homework ADD COLUMN youtube_url TEXT')
        except sqlite3.OperationalError:
            pass
    
    # Migrate attendance table: add 'status' column if needed
    cursor.execute("PRAGMA table_info(attendance)")
    attendance_columns = [row[1] for row in cursor.fetchall()]
    
    if 'status' not in attendance_columns:
        try:
            # Add status column and migrate data from present column
            cursor.execute('ALTER TABLE attendance ADD COLUMN status INTEGER DEFAULT 1')
            cursor.execute('UPDATE attendance SET status = COALESCE(present, 1) WHERE status IS NULL')
            # Note: SQLite doesn't support DROP COLUMN, so we'll keep both for backward compatibility
            # In practice, we'll use 'status' going forward
        except sqlite3.OperationalError:
            pass
    
    conn.commit()
    conn.close()

# Initialize database on startup
if not os.path.exists(DATABASE):
    init_db()
else:
    migrate_db()

def require_login(f):
    """Decorator to require login and load user data"""
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        # Load tuition_name into session if not already there
        if 'tuition_name' not in session:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT tuition_name FROM users WHERE id = ?', (session['user_id'],))
            user = cursor.fetchone()
            if user and user['tuition_name']:
                session['tuition_name'] = user['tuition_name']
            conn.close()
        
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Authentication Routes
@app.route('/')
def index():
    """Welcome page"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('welcome'))

@app.route('/welcome')
def welcome():
    """Welcome page with tutor/student selection"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('welcome.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """OTP-based login for tutors"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        action = request.form.get('action', 'login')  # 'login' or 'signup'
        mobile = request.form.get('mobile', '').strip()
        
        if not mobile or len(mobile) != 10 or not mobile.isdigit():
            return render_template('login.html', error='Please enter a valid 10-digit mobile number', active_tab=action)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute('SELECT id, tuition_name FROM users WHERE mobile = ?', (mobile,))
        user = cursor.fetchone()
        
        if action == 'login':
            # Login flow
            if not user:
                conn.close()
                return render_template('login.html', error='Mobile number not found. Please sign up first.', active_tab='login')
            
            user_id = user['id']
            tuition_name = user['tuition_name']
            
            # Simulate OTP verification (auto-login)
            session['user_id'] = user_id
            session['mobile'] = mobile
            if tuition_name:
                session['tuition_name'] = tuition_name
            
            conn.close()
            return redirect(url_for('dashboard'))
        
        else:  # signup
            # Signup flow - check if already exists
            if user:
                conn.close()
                return render_template('login.html', error='Mobile number already registered. Please login instead.', active_tab='signup')
            
            # For signup, redirect to signup page to get tuition name
            session['signup_mobile'] = mobile
            conn.close()
            return redirect(url_for('signup'))
    
    return render_template('login.html', active_tab='login')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Signup page - collect tuition name"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    if 'signup_mobile' not in session:
        return redirect(url_for('login'))
    
    mobile = session['signup_mobile']
    
    if request.method == 'POST':
        tuition_name = request.form.get('tuition_name', '').strip()
        
        if not tuition_name:
            return render_template('signup.html', mobile=mobile, error='Please enter your tuition name')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if mobile already exists (race condition check)
        cursor.execute('SELECT id FROM users WHERE mobile = ?', (mobile,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            conn.close()
            session.pop('signup_mobile', None)
            return render_template('login.html', error='Mobile number already registered. Please login instead.', active_tab='login')
        
        # Create new user
        cursor.execute('INSERT INTO users (mobile, tuition_name) VALUES (?, ?)', (mobile, tuition_name))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        
        # Clear signup session and set login session
        session.pop('signup_mobile', None)
        session['user_id'] = user_id
        session['mobile'] = mobile
        session['tuition_name'] = tuition_name
        
        return redirect(url_for('dashboard'))
    
    return render_template('signup.html', mobile=mobile)

@app.route('/student/login')
def student_login():
    """Student login - Coming Soon"""
    return render_template('student_login.html')

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    return redirect(url_for('welcome'))

# Dashboard
@app.route('/dashboard')
@require_login
def dashboard():
    """Main dashboard"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    user_id = session['user_id']
    today = date.today().isoformat()
    
    # Get stats
    cursor.execute('SELECT COUNT(*) as count FROM students WHERE user_id = ?', (user_id,))
    student_count = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM batches WHERE user_id = ?', (user_id,))
    batch_count = cursor.fetchone()['count']
    
    # Get today's attendance count
    # Count distinct students who are present or late (status 1 or 2)
    cursor.execute('''
        SELECT COUNT(DISTINCT student_id) as count 
        FROM attendance 
        WHERE user_id = ? AND date = ? 
        AND COALESCE(status, present, 0) IN (1, 2)
    ''', (user_id, today))
    attendance_result = cursor.fetchone()
    attendance_count = attendance_result['count'] if attendance_result else 0
    
    # Calculate attendance percentage
    # Percentage = (students marked present or late / total students) * 100
    if student_count > 0:
        attendance_percentage = round((attendance_count / student_count) * 100)
        # Cap at 100% to prevent showing more than 100%
        attendance_percentage = min(attendance_percentage, 100)
    else:
        attendance_percentage = 0
    
    # Get recent students (last 5)
    cursor.execute('''
        SELECT s.*, b.name as batch_name 
        FROM students s 
        LEFT JOIN batches b ON s.batch_id = b.id 
        WHERE s.user_id = ? 
        ORDER BY s.created_at DESC 
        LIMIT 5
    ''', (user_id,))
    recent_students = cursor.fetchall()
    
    # Get recent homework (last 3)
    cursor.execute('''
        SELECT h.*, b.name as batch_name, s.name as student_name
        FROM homework h
        LEFT JOIN batches b ON h.batch_id = b.id
        LEFT JOIN students s ON h.student_id = s.id
        WHERE h.user_id = ?
        ORDER BY h.created_at DESC
        LIMIT 3
    ''', (user_id,))
    recent_homework = cursor.fetchall()
    
    # Get students per batch
    cursor.execute('''
        SELECT b.name, COUNT(s.id) as student_count
        FROM batches b
        LEFT JOIN students s ON b.id = s.batch_id AND s.user_id = ?
        WHERE b.user_id = ?
        GROUP BY b.id
        ORDER BY student_count DESC
    ''', (user_id, user_id))
    batch_stats = cursor.fetchall()
    
    conn.close()
    
    return render_template('dashboard.html', 
                         student_count=student_count,
                         batch_count=batch_count,
                         attendance_count=attendance_count,
                         attendance_percentage=attendance_percentage,
                         recent_students=recent_students,
                         recent_homework=recent_homework,
                         batch_stats=batch_stats,
                         today=today)

# Batch Management
@app.route('/batches')
@require_login
def batches():
    """List all batches"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM batches WHERE user_id = ? ORDER BY created_at DESC', (session['user_id'],))
    batches = cursor.fetchall()
    conn.close()
    return render_template('batches.html', batches=batches)

@app.route('/batches/<int:batch_id>/students')
@require_login
def batch_students(batch_id):
    """View students in a specific batch"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get batch details
    cursor.execute('SELECT * FROM batches WHERE id = ? AND user_id = ?', (batch_id, session['user_id']))
    batch = cursor.fetchone()
    
    if not batch:
        conn.close()
        flash('Batch not found', 'error')
        return redirect(url_for('batches'))
    
    # Get search query
    search_query = request.args.get('search', '').strip()
    
    # Build query for students in this batch
    query = '''
        SELECT s.*, b.name as batch_name 
        FROM students s 
        LEFT JOIN batches b ON s.batch_id = b.id 
        WHERE s.user_id = ? AND s.batch_id = ?
    '''
    params = [session['user_id'], batch_id]
    
    if search_query:
        query += ' AND (s.name LIKE ? OR s.phone LIKE ?)'
        search_pattern = f'%{search_query}%'
        params.extend([search_pattern, search_pattern])
    
    query += ' ORDER BY s.name'
    
    cursor.execute(query, params)
    students = cursor.fetchall()
    
    conn.close()
    return render_template('batch_students.html', 
                         batch=batch,
                         students=students,
                         search_query=search_query)

@app.route('/batches/add', methods=['GET', 'POST'])
@require_login
def add_batch():
    """Add a new batch"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        start_time = request.form.get('start_time', '').strip()
        end_time = request.form.get('end_time', '').strip()
        
        # Get selected days
        days_list = []
        day_names = ['mo', 'tu', 'we', 'th', 'fr', 'sa', 'su']
        for day in day_names:
            if request.form.get(f'day_{day}') == 'on':
                days_list.append(day)
        days = ','.join(days_list) if days_list else ''
        
        if name:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO batches (name, description, start_time, end_time, days, user_id) 
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, description, start_time, end_time, days, session['user_id']))
            conn.commit()
            conn.close()
            return redirect(url_for('batches'))
    
    return render_template('add_batch.html')

@app.route('/batches/<int:batch_id>/edit', methods=['GET', 'POST'])
@require_login
def edit_batch(batch_id):
    """Edit a batch"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        start_time = request.form.get('start_time', '').strip()
        end_time = request.form.get('end_time', '').strip()
        
        # Get selected days
        days_list = []
        day_names = ['mo', 'tu', 'we', 'th', 'fr', 'sa', 'su']
        for day in day_names:
            if request.form.get(f'day_{day}') == 'on':
                days_list.append(day)
        days = ','.join(days_list) if days_list else ''
        
        if name:
            cursor.execute('''
                UPDATE batches 
                SET name = ?, description = ?, start_time = ?, end_time = ?, days = ?
                WHERE id = ? AND user_id = ?
            ''', (name, description, start_time, end_time, days, batch_id, session['user_id']))
            conn.commit()
            conn.close()
            return redirect(url_for('batches'))
    
    # Get batch
    cursor.execute('SELECT * FROM batches WHERE id = ? AND user_id = ?', (batch_id, session['user_id']))
    batch = cursor.fetchone()
    
    if not batch:
        conn.close()
        return redirect(url_for('batches'))
    
    # Parse days string to list for template
    batch_days = batch['days'].split(',') if batch['days'] else []
    
    conn.close()
    return render_template('edit_batch.html', batch=batch, batch_days=batch_days)

@app.route('/api/batches/<int:batch_id>', methods=['DELETE'])
@require_login
def delete_batch(batch_id):
    """Delete a batch (API endpoint)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if batch has students
    cursor.execute('SELECT COUNT(*) as count FROM students WHERE batch_id = ? AND user_id = ?', 
                   (batch_id, session['user_id']))
    student_count = cursor.fetchone()['count']
    
    if student_count > 0:
        conn.close()
        return jsonify({'success': False, 'error': 'Cannot delete batch with students. Please remove students first.'}), 400
    
    cursor.execute('DELETE FROM batches WHERE id = ? AND user_id = ?', (batch_id, session['user_id']))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

# Student Management
@app.route('/students')
@require_login
def students():
    """List all students"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get search and filter parameters
    search_query = request.args.get('search', '').strip()
    batch_filter = request.args.get('batch', type=int)
    
    # Build query
    query = '''
        SELECT s.*, b.name as batch_name 
        FROM students s 
        LEFT JOIN batches b ON s.batch_id = b.id 
        WHERE s.user_id = ?
    '''
    params = [session['user_id']]
    
    if search_query:
        query += ' AND (s.name LIKE ? OR s.phone LIKE ?)'
        search_pattern = f'%{search_query}%'
        params.extend([search_pattern, search_pattern])
    
    if batch_filter:
        query += ' AND s.batch_id = ?'
        params.append(batch_filter)
    
    query += ' ORDER BY s.name'
    
    cursor.execute(query, params)
    students = cursor.fetchall()
    
    # Get all batches for filter dropdown
    cursor.execute('SELECT * FROM batches WHERE user_id = ? ORDER BY name', (session['user_id'],))
    batches = cursor.fetchall()
    
    conn.close()
    return render_template('students.html', 
                         students=students, 
                         batches=batches,
                         search_query=search_query,
                         batch_filter=batch_filter)

@app.route('/students/add', methods=['GET', 'POST'])
@require_login
def add_student():
    """Add a new student"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        batch_id = request.form.get('batch_id')
        address = request.form.get('address', '').strip()
        school_name = request.form.get('school_name', '').strip()
        standard = request.form.get('standard', '').strip()
        
        if name and phone and batch_id:
            cursor.execute('''
                INSERT INTO students (name, phone, batch_id, address, school_name, standard, user_id) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, phone, int(batch_id), address, school_name, standard, session['user_id']))
            conn.commit()
            conn.close()
            return redirect(url_for('students'))
    
    # Get batches for dropdown
    cursor.execute('SELECT * FROM batches WHERE user_id = ? ORDER BY name', (session['user_id'],))
    batches = cursor.fetchall()
    conn.close()
    
    return render_template('add_student.html', batches=batches)

@app.route('/students/<int:student_id>/edit', methods=['GET', 'POST'])
@require_login
def edit_student(student_id):
    """Edit a student"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        batch_id = request.form.get('batch_id')
        address = request.form.get('address', '').strip()
        school_name = request.form.get('school_name', '').strip()
        standard = request.form.get('standard', '').strip()
        
        if name and phone and batch_id:
            cursor.execute('''
                UPDATE students 
                SET name = ?, phone = ?, batch_id = ?, address = ?, school_name = ?, standard = ?
                WHERE id = ? AND user_id = ?
            ''', (name, phone, int(batch_id), address, school_name, standard, student_id, session['user_id']))
            conn.commit()
            conn.close()
            return redirect(url_for('students'))
    
    # Get student
    cursor.execute('SELECT * FROM students WHERE id = ? AND user_id = ?', (student_id, session['user_id']))
    student = cursor.fetchone()
    
    if not student:
        conn.close()
        return redirect(url_for('students'))
    
    # Get batches
    cursor.execute('SELECT * FROM batches WHERE user_id = ? ORDER BY name', (session['user_id'],))
    batches = cursor.fetchall()
    conn.close()
    
    return render_template('edit_student.html', student=student, batches=batches)

@app.route('/students/<int:student_id>')
@require_login
def view_student(student_id):
    """View student details"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get student with batch info
    cursor.execute('''
        SELECT s.*, b.name as batch_name 
        FROM students s 
        LEFT JOIN batches b ON s.batch_id = b.id 
        WHERE s.id = ? AND s.user_id = ?
    ''', (student_id, session['user_id']))
    student = cursor.fetchone()
    
    if not student:
        conn.close()
        return redirect(url_for('students'))
    
    # Get attendance stats
    # Use COALESCE to handle both 'status' and 'present' columns during migration
    cursor.execute('''
        SELECT 
            COUNT(*) as total_days,
            SUM(CASE WHEN COALESCE(status, present, 0) = 1 THEN 1 ELSE 0 END) as present_days,
            SUM(CASE WHEN COALESCE(status, present, 0) = 2 THEN 1 ELSE 0 END) as late_days
        FROM attendance 
        WHERE student_id = ? AND user_id = ?
    ''', (student_id, session['user_id']))
    attendance_stats = cursor.fetchone()
    
    # Get recent attendance (last 10 days)
    cursor.execute('''
        SELECT date, COALESCE(status, present, 0) as status
        FROM attendance 
        WHERE student_id = ? AND user_id = ?
        ORDER BY date DESC
        LIMIT 10
    ''', (student_id, session['user_id']))
    recent_attendance = cursor.fetchall()
    
    conn.close()
    
    return render_template('view_student.html', 
                         student=student, 
                         attendance_stats=attendance_stats,
                         recent_attendance=recent_attendance,
                         today=date.today().isoformat())

@app.route('/api/students/<int:student_id>', methods=['DELETE'])
@require_login
def delete_student(student_id):
    """Delete a student (API endpoint)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM students WHERE id = ? AND user_id = ?', (student_id, session['user_id']))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

# Attendance Management
@app.route('/attendance')
@require_login
def attendance():
    """Attendance tracker page"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get selected date and batch filter from query parameters
    selected_date = request.args.get('date', date.today().isoformat())
    batch_filter = request.args.get('batch', type=int)
    
    # Build query for students with attendance status
    query = '''
        SELECT s.*, b.name as batch_name,
               COALESCE(a.status, -1) as attendance_status
        FROM students s
        LEFT JOIN batches b ON s.batch_id = b.id
        LEFT JOIN attendance a ON s.id = a.student_id AND a.date = ?
        WHERE s.user_id = ?
    '''
    params = [selected_date, session['user_id']]
    
    if batch_filter:
        query += ' AND s.batch_id = ?'
        params.append(batch_filter)
    
    query += ' ORDER BY b.name, s.name'
    
    cursor.execute(query, params)
    students = cursor.fetchall()
    
    # Group students by batch
    students_by_batch = {}
    for student in students:
        batch_name = student['batch_name'] or 'No Batch'
        if batch_name not in students_by_batch:
            students_by_batch[batch_name] = []
        students_by_batch[batch_name].append(student)
    
    # Get all batches for filter dropdown
    cursor.execute('SELECT * FROM batches WHERE user_id = ? ORDER BY name', (session['user_id'],))
    batches = cursor.fetchall()
    
    conn.close()
    
    return render_template('attendance.html', 
                         students_by_batch=students_by_batch,
                         students=students,  # Keep for backward compatibility
                         selected_date=selected_date,
                         today=date.today().isoformat(),
                         batches=batches,
                         batch_filter=batch_filter)

@app.route('/api/attendance/mark', methods=['POST'])
@require_login
def mark_attendance():
    """Mark attendance for a student
    status: 0 = absent, 1 = present, 2 = late
    """
    data = request.get_json()
    student_id = data.get('student_id')
    status = data.get('status', 1)  # Default to present
    date_str = data.get('date', date.today().isoformat())
    
    # Validate status
    if status not in [0, 1, 2]:
        return jsonify({'success': False, 'error': 'Invalid status'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if student belongs to user
    cursor.execute('SELECT id FROM students WHERE id = ? AND user_id = ?', (student_id, session['user_id']))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'success': False, 'error': 'Student not found'}), 404
    
    # Insert or update attendance
    # Use status column, fallback to present for migration compatibility
    cursor.execute('''
        INSERT OR REPLACE INTO attendance (student_id, date, status, user_id)
        VALUES (?, ?, ?, ?)
    ''', (student_id, date_str, status, session['user_id']))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/attendance/history')
@require_login
def attendance_history():
    """View attendance history for a student"""
    student_id = request.args.get('student_id', type=int)
    if not student_id:
        return redirect(url_for('students'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Verify student belongs to user
    cursor.execute('SELECT * FROM students WHERE id = ? AND user_id = ?', (student_id, session['user_id']))
    student = cursor.fetchone()
    if not student:
        conn.close()
        return redirect(url_for('students'))
    
    # Get attendance history
    cursor.execute('''
        SELECT date, present 
        FROM attendance 
        WHERE student_id = ? AND user_id = ?
        ORDER BY date DESC
        LIMIT 30
    ''', (student_id, session['user_id']))
    attendance_records = cursor.fetchall()
    
    conn.close()
    
    return render_template('attendance_history.html', student=student, attendance_records=attendance_records)

# Homework Management
@app.route('/homework')
@require_login
def homework():
    """List all homework"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT h.*, b.name as batch_name, s.name as student_name
        FROM homework h
        LEFT JOIN batches b ON h.batch_id = b.id
        LEFT JOIN students s ON h.student_id = s.id
        WHERE h.user_id = ?
        ORDER BY h.created_at DESC
    ''', (session['user_id'],))
    homework_list = cursor.fetchall()
    conn.close()
    return render_template('homework.html', homework_list=homework_list)

@app.route('/homework/share', methods=['GET', 'POST'])
@require_login
def share_homework():
    """Share homework form"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        youtube_url = request.form.get('youtube_url', '').strip()
        batch_id = request.form.get('batch_id') or None
        student_id = request.form.get('student_id') or None
        
        # Handle file upload
        file_path = None
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Add timestamp to avoid conflicts
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                filename = timestamp + filename
                file_path = os.path.join('homework', filename)
                full_path = os.path.join(app.config['UPLOAD_FOLDER'], file_path)
                file.save(full_path)
                file_path = file_path.replace('\\', '/')  # Normalize path
        
        if title:
            if batch_id:
                batch_id = int(batch_id)
            else:
                batch_id = None
            if student_id:
                student_id = int(student_id)
            else:
                student_id = None
            
            cursor.execute('''
                INSERT INTO homework (title, content, file_path, youtube_url, batch_id, student_id, user_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (title, content, file_path, youtube_url, batch_id, student_id, session['user_id']))
            conn.commit()
            conn.close()
            return redirect(url_for('homework'))
    
    # Get batches and students for dropdowns
    cursor.execute('SELECT * FROM batches WHERE user_id = ? ORDER BY name', (session['user_id'],))
    batches = cursor.fetchall()
    
    cursor.execute('SELECT * FROM students WHERE user_id = ? ORDER BY name', (session['user_id'],))
    students = cursor.fetchall()
    
    conn.close()
    
    return render_template('share_homework.html', batches=batches, students=students)

@app.route('/uploads/<path:filename>')
@require_login
def uploaded_file(filename):
    """Serve uploaded files"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/homework/<int:homework_id>/edit', methods=['GET', 'POST'])
@require_login
def edit_homework(homework_id):
    """Edit homework"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        youtube_url = request.form.get('youtube_url', '').strip()
        batch_id = request.form.get('batch_id') or None
        student_id = request.form.get('student_id') or None
        remove_file = request.form.get('remove_file') == '1'
        
        # Handle file upload
        file_path = None
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                filename = timestamp + filename
                file_path = os.path.join('homework', filename)
                full_path = os.path.join(app.config['UPLOAD_FOLDER'], file_path)
                file.save(full_path)
                file_path = file_path.replace('\\', '/')
        
        if title:
            if batch_id:
                batch_id = int(batch_id)
            else:
                batch_id = None
            if student_id:
                student_id = int(student_id)
            else:
                student_id = None
            
            # Get existing homework to preserve file_path if not updating
            cursor.execute('SELECT file_path FROM homework WHERE id = ? AND user_id = ?', 
                         (homework_id, session['user_id']))
            existing = cursor.fetchone()
            
            if remove_file:
                file_path = None
            elif not file_path and existing:
                file_path = existing['file_path']
            
            cursor.execute('''
                UPDATE homework 
                SET title = ?, content = ?, file_path = ?, youtube_url = ?, batch_id = ?, student_id = ?
                WHERE id = ? AND user_id = ?
            ''', (title, content, file_path, youtube_url, batch_id, student_id, homework_id, session['user_id']))
            conn.commit()
            conn.close()
            return redirect(url_for('homework'))
    
    # Get homework
    cursor.execute('SELECT * FROM homework WHERE id = ? AND user_id = ?', (homework_id, session['user_id']))
    homework = cursor.fetchone()
    
    if not homework:
        conn.close()
        return redirect(url_for('homework'))
    
    # Get batches and students
    cursor.execute('SELECT * FROM batches WHERE user_id = ? ORDER BY name', (session['user_id'],))
    batches = cursor.fetchall()
    
    cursor.execute('SELECT * FROM students WHERE user_id = ? ORDER BY name', (session['user_id'],))
    students = cursor.fetchall()
    
    conn.close()
    
    return render_template('edit_homework.html', homework=homework, batches=batches, students=students)

@app.route('/api/homework/<int:homework_id>', methods=['DELETE'])
@require_login
def delete_homework(homework_id):
    """Delete homework (API endpoint)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM homework WHERE id = ? AND user_id = ?', (homework_id, session['user_id']))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

# Payment Management (Locked Feature)
@app.route('/payments/locked')
@require_login
def payments_locked():
    """Locked payment management system"""
    return render_template('payments_locked.html')

# Attendance Reports
@app.route('/reports')
@require_login
def reports():
    """Attendance summary report for all batches (last 7 days)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    user_id = session['user_id']
    today = date.today()
    
    # Calculate date range (last 7 days including today)
    date_range = []
    for i in range(6, -1, -1):  # 6 days ago to today
        d = today - timedelta(days=i)
        date_range.append(d.isoformat())
    
    # Get all batches
    cursor.execute('SELECT * FROM batches WHERE user_id = ? ORDER BY name', (user_id,))
    batches = cursor.fetchall()
    
    batch_reports = []
    for batch in batches:
        batch_id = batch['id']
        
        # Get all students in this batch
        cursor.execute('SELECT id FROM students WHERE batch_id = ? AND user_id = ?', (batch_id, user_id))
        students = cursor.fetchall()
        student_ids = [s['id'] for s in students]
        
        if not student_ids:
            continue
        
        # Calculate attendance for last 7 days
        # Total expected sessions = number of students * 7 days
        total_expected = len(student_ids) * 7
        
        # Get actual attendance records for these students in the date range
        # Initialize to 0 to prevent None errors
        total_sessions = 0
        attended_sessions = 0
        
        if student_ids:
            placeholders = ','.join(['?'] * len(student_ids))
            date_placeholders = ','.join(['?'] * len(date_range))
            
            # Check if 'present' column exists in attendance table
            cursor.execute("PRAGMA table_info(attendance)")
            columns = [row[1] for row in cursor.fetchall()]
            has_present_column = 'present' in columns
            has_status_column = 'status' in columns
            
            # Build query based on available columns
            if has_status_column:
                # Use status column (new schema)
                query = f'''
                    SELECT 
                        COUNT(*) as total_sessions,
                        COALESCE(SUM(CASE WHEN status IN (1, 2) THEN 1 ELSE 0 END), 0) as attended_sessions
                    FROM attendance
                    WHERE student_id IN ({placeholders})
                    AND user_id = ?
                    AND date IN ({date_placeholders})
                '''
            elif has_present_column:
                # Use present column (old schema)
                query = f'''
                    SELECT 
                        COUNT(*) as total_sessions,
                        COALESCE(SUM(CASE WHEN present = 1 THEN 1 ELSE 0 END), 0) as attended_sessions
                    FROM attendance
                    WHERE student_id IN ({placeholders})
                    AND user_id = ?
                    AND date IN ({date_placeholders})
                '''
            else:
                # No attendance table structure - use defaults (already 0)
                query = None
            
            if query:
                params = student_ids + [user_id] + date_range
                cursor.execute(query, params)
                result = cursor.fetchone()
                if result:
                    total_sessions = result['total_sessions'] if result['total_sessions'] is not None else 0
                    attended_sessions = result['attended_sessions'] if result['attended_sessions'] is not None else 0
        
        # Calculate attendance percentage
        if total_expected > 0:
            attendance_percentage = round((attended_sessions / total_expected) * 100)
            attendance_percentage = min(attendance_percentage, 100)
        else:
            attendance_percentage = 0
        
        batch_reports.append({
            'batch_id': batch_id,
            'batch_name': batch['name'],
            'student_count': len(student_ids),
            'total_expected': total_expected,
            'attended_sessions': attended_sessions,
            'attendance_percentage': attendance_percentage
        })
    
    conn.close()
    
    return render_template('reports.html', 
                         batch_reports=batch_reports,
                         date_range=date_range)

@app.route('/reports/batch/<int:batch_id>')
@require_login
def batch_report_detail(batch_id):
    """Detailed attendance report for a specific batch (last 7 days)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    user_id = session['user_id']
    today = date.today()
    
    # Verify batch belongs to user
    cursor.execute('SELECT * FROM batches WHERE id = ? AND user_id = ?', (batch_id, user_id))
    batch = cursor.fetchone()
    
    if not batch:
        conn.close()
        return redirect(url_for('reports'))
    
    # Calculate date range (last 7 days including today)
    date_range = []
    for i in range(6, -1, -1):  # 6 days ago to today
        d = today - timedelta(days=i)
        date_range.append(d.isoformat())
    
    # Get all students in this batch
    cursor.execute('''
        SELECT s.* 
        FROM students s
        WHERE s.batch_id = ? AND s.user_id = ?
        ORDER BY s.name
    ''', (batch_id, user_id))
    students = cursor.fetchall()
    
    student_reports = []
    for student in students:
        student_id = student['id']
        
        # Get attendance for each day in the date range
        # Check which columns exist
        cursor.execute("PRAGMA table_info(attendance)")
        columns = [row[1] for row in cursor.fetchall()]
        has_present_column = 'present' in columns
        has_status_column = 'status' in columns
        
        attendance_by_date = {}
        for date_str in date_range:
            if has_status_column:
                # Use status column
                cursor.execute('''
                    SELECT status
                    FROM attendance
                    WHERE student_id = ? AND date = ? AND user_id = ?
                ''', (student_id, date_str, user_id))
            elif has_present_column:
                # Use present column and convert to status format
                cursor.execute('''
                    SELECT present
                    FROM attendance
                    WHERE student_id = ? AND date = ? AND user_id = ?
                ''', (student_id, date_str, user_id))
            else:
                # No attendance table structure
                result = None
            
            result = cursor.fetchone()
            if result:
                if has_status_column:
                    attendance_by_date[date_str] = result['status'] if result['status'] is not None else -1
                else:
                    # Convert present (0/1) to status format (0=absent, 1=present, -1=no record)
                    attendance_by_date[date_str] = result['present'] if result['present'] is not None else -1
            else:
                attendance_by_date[date_str] = -1  # -1 means no record
        
        # Calculate student statistics
        total_days = len(date_range)
        present_count = sum(1 for status in attendance_by_date.values() if status == 1)
        late_count = sum(1 for status in attendance_by_date.values() if status == 2)
        absent_count = sum(1 for status in attendance_by_date.values() if status == 0)
        na_count = sum(1 for status in attendance_by_date.values() if status == -1)
        attended_count = present_count + late_count
        
        # Calculate attendance percentage (only for days with records)
        days_with_records = total_days - na_count
        if days_with_records > 0:
            attendance_percentage = round((attended_count / days_with_records) * 100)
        else:
            attendance_percentage = 0
        
        student_reports.append({
            'student_id': student_id,
            'student_name': student['name'],
            'student_phone': student['phone'],
            'attendance_by_date': attendance_by_date,
            'total_days': total_days,
            'present_count': present_count,
            'late_count': late_count,
            'absent_count': absent_count,
            'na_count': na_count,
            'attended_count': attended_count,
            'attendance_percentage': attendance_percentage,
            'has_been_absent': absent_count > 0,
            'is_high_attendance': attendance_percentage >= 80
        })
    
    conn.close()
    
    return render_template('batch_report_detail.html',
                         batch=batch,
                         student_reports=student_reports,
                         date_range=date_range)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

