"""Admin (Superadmin) dashboard blueprint for TuitionTrack
Moved to separate module for maintainability.
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from database import get_db_connection
from functools import wraps
from utils import get_ist_today
from datetime import timedelta

# Blueprint with separate templates folder
admin_bp = Blueprint('admin', __name__, url_prefix='/tut-admin', template_folder='templates')

def require_admin(f):
    """Decorator to require admin login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

# ─── Auth ───────────────────────────────────────────────

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page"""
    if 'admin_id' in session:
        return redirect(url_for('admin.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            return render_template('admin/login.html', error='Please enter username and password')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, password_hash, name FROM admins WHERE username = ?', (username,))
        admin = cursor.fetchone()
        conn.close()
        
        if not admin or not check_password_hash(admin['password_hash'], password):
            return render_template('admin/login.html', error='Invalid username or password')
        
        session['admin_id'] = admin['id']
        session['admin_name'] = admin['name'] or admin['username']
        return redirect(url_for('admin.dashboard'))
    
    return render_template('admin/login.html')

@admin_bp.route('/logout')
def logout():
    """Admin logout"""
    session.pop('admin_id', None)
    session.pop('admin_name', None)
    return redirect(url_for('admin.login'))

# ─── Dashboard Overview ─────────────────────────────────

@admin_bp.route('/')
@require_admin
def dashboard():
    """Admin dashboard overview with key metrics"""
    conn = get_db_connection()
    cursor = conn.cursor()
    today = get_ist_today()
    
    cursor.execute('SELECT COUNT(*) as count FROM users')
    total_teachers = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM students')
    total_students = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM batches')
    total_batches = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM attendance WHERE date = ?', (today.isoformat(),))
    today_attendance = cursor.fetchone()['count']
    
    week_ago = (today - timedelta(days=7)).isoformat()
    cursor.execute('SELECT COUNT(DISTINCT user_id) as count FROM attendance WHERE date >= ?', (week_ago,))
    active_teachers = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM users WHERE created_at >= ?', (week_ago,))
    new_signups = cursor.fetchone()['count']
    
    cursor.execute('SELECT id, mobile, tutor_name, tuition_name, created_at FROM users ORDER BY created_at DESC LIMIT 10')
    recent_teachers = cursor.fetchall()
    
    conn.close()
    
    return render_template('admin/dashboard.html',
        total_teachers=total_teachers,
        total_students=total_students,
        total_batches=total_batches,
        today_attendance=today_attendance,
        active_teachers=active_teachers,
        new_signups=new_signups,
        recent_teachers=recent_teachers,
        today=today
    )

# ─── Teachers & Students Lists ────────────────────────

@admin_bp.route('/teachers')
@require_admin
def teachers():
    """List all tutors"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT u.id, u.mobile, u.tutor_name, u.tuition_name, u.created_at,
               (SELECT COUNT(*) FROM students WHERE user_id = u.id) as student_count,
               (SELECT COUNT(*) FROM batches WHERE user_id = u.id) as batch_count,
               (SELECT MAX(date) FROM attendance WHERE user_id = u.id) as last_active
        FROM users u ORDER BY u.created_at DESC
    ''')
    teachers_list = cursor.fetchall()
    conn.close()
    
    return render_template('admin/teachers.html', teachers=teachers_list)

@admin_bp.route('/students')
@require_admin
def students():
    """List all students"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT s.id, s.name, s.phone, s.created_at,
               b.name as batch_name, u.tuition_name, u.tutor_name
        FROM students s
        LEFT JOIN batches b ON s.batch_id = b.id
        LEFT JOIN users u ON s.user_id = u.id
        ORDER BY s.created_at DESC LIMIT 200
    ''')
    students_list = cursor.fetchall()
    conn.close()
    
    return render_template('admin/students.html', students=students_list)


@admin_bp.route('/teachers/<int:teacher_id>')
@require_admin
def teacher_detail(teacher_id):
    """Detailed view of a single tutor"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM users WHERE id = ?', (teacher_id,))
    teacher = cursor.fetchone()
    if not teacher:
        conn.close()
        flash('Teacher not found', 'error')
        return redirect(url_for('admin.teachers'))

    cursor.execute('''
        SELECT b.*, (SELECT COUNT(*) FROM students WHERE batch_id = b.id) as student_count
        FROM batches b WHERE b.user_id = ? ORDER BY b.name
    ''', (teacher_id,))
    batches = cursor.fetchall()

    cursor.execute('''
        SELECT s.*, b.name as batch_name
        FROM students s LEFT JOIN batches b ON s.batch_id = b.id
        WHERE s.user_id = ? ORDER BY s.name
    ''', (teacher_id,))
    students_list = cursor.fetchall()

    today = get_ist_today()
    cursor.execute('SELECT COUNT(*) as total FROM attendance WHERE user_id = ? AND date = ?',
                   (teacher_id, today.isoformat()))
    today_attendance = cursor.fetchone()['total']

    month_start = today.replace(day=1).isoformat()
    cursor.execute('SELECT COUNT(*) as total FROM attendance WHERE user_id = ? AND date >= ?',
                   (teacher_id, month_start))
    month_attendance = cursor.fetchone()['total']

    conn.close()

    return render_template('admin/teacher_detail.html',
        teacher=teacher, batches=batches, students=students_list,
        today_attendance=today_attendance, month_attendance=month_attendance
    )
