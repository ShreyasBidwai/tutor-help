"""Admin (Superadmin) dashboard blueprint for TuitionTrack
Moved to separate module for maintainability.
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash
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

# ─── Teachers ──────────────────────────────────────────

@admin_bp.route('/teachers')
@require_admin
def teachers():
    """List all tutors"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT u.id, u.mobile, u.tutor_name, u.tuition_name, u.created_at, u.is_active,
               (SELECT COUNT(*) FROM students WHERE user_id = u.id) as student_count,
               (SELECT COUNT(*) FROM batches WHERE user_id = u.id) as batch_count,
               (SELECT MAX(date) FROM attendance WHERE user_id = u.id) as last_active
        FROM users u ORDER BY u.created_at DESC
    ''')
    teachers_list = cursor.fetchall()
    conn.close()
    
    return render_template('admin/teachers.html', teachers=teachers_list)

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

@admin_bp.route('/teachers/<int:teacher_id>/edit', methods=['POST'])
@require_admin
def edit_teacher(teacher_id):
    """Update teacher details"""
    tutor_name = request.form.get('tutor_name', '').strip()
    tuition_name = request.form.get('tuition_name', '').strip()
    address = request.form.get('address', '').strip()
    
    conn = get_db_connection()
    conn.execute(
        'UPDATE users SET tutor_name = ?, tuition_name = ?, address = ? WHERE id = ?',
        (tutor_name or None, tuition_name or None, address or None, teacher_id)
    )
    conn.commit()
    conn.close()
    
    flash('Teacher updated successfully', 'success')
    return redirect(url_for('admin.teacher_detail', teacher_id=teacher_id))

@admin_bp.route('/teachers/<int:teacher_id>/reset-password', methods=['POST'])
@require_admin
def reset_teacher_password(teacher_id):
    """Reset a teacher's password"""
    new_password = request.form.get('new_password', '').strip()
    if not new_password or len(new_password) < 4:
        flash('Password must be at least 4 characters', 'error')
        return redirect(url_for('admin.teacher_detail', teacher_id=teacher_id))
    
    conn = get_db_connection()
    conn.execute(
        'UPDATE users SET password_hash = ? WHERE id = ?',
        (generate_password_hash(new_password), teacher_id)
    )
    conn.commit()
    conn.close()
    
    flash('Password reset successfully', 'success')
    return redirect(url_for('admin.teacher_detail', teacher_id=teacher_id))

@admin_bp.route('/teachers/<int:teacher_id>/delete', methods=['POST'])
@require_admin
def delete_teacher(teacher_id):
    """Delete a teacher and all their related data"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get teacher info for flash message
    cursor.execute('SELECT tutor_name, mobile FROM users WHERE id = ?', (teacher_id,))
    teacher = cursor.fetchone()
    if not teacher:
        conn.close()
        flash('Teacher not found', 'error')
        return redirect(url_for('admin.teachers'))
    
    # Cascade delete: fees → attendance → homework → students → push_subscriptions → batches → payment_config → user
    cursor.execute('DELETE FROM student_fee_records WHERE user_id = ?', (teacher_id,))
    cursor.execute('DELETE FROM attendance WHERE user_id = ?', (teacher_id,))
    cursor.execute('DELETE FROM homework WHERE user_id = ?', (teacher_id,))
    cursor.execute('DELETE FROM students WHERE user_id = ?', (teacher_id,))
    cursor.execute('DELETE FROM push_subscriptions WHERE user_id = ?', (teacher_id,))
    cursor.execute('DELETE FROM batches WHERE user_id = ?', (teacher_id,))
    cursor.execute('DELETE FROM tutor_payment_config WHERE user_id = ?', (teacher_id,))
    cursor.execute('DELETE FROM users WHERE id = ?', (teacher_id,))
    
    conn.commit()
    conn.close()
    
    flash(f'Teacher "{teacher["tutor_name"] or teacher["mobile"]}" deleted successfully', 'success')
    return redirect(url_for('admin.teachers'))

@admin_bp.route('/teachers/<int:teacher_id>/toggle', methods=['POST'])
@require_admin
def toggle_teacher(teacher_id):
    """Enable or disable a teacher"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT is_active, tutor_name, mobile FROM users WHERE id = ?', (teacher_id,))
    teacher = cursor.fetchone()
    if not teacher:
        conn.close()
        flash('Teacher not found', 'error')
        return redirect(url_for('admin.teachers'))
    
    new_status = 0 if teacher['is_active'] else 1
    conn.execute('UPDATE users SET is_active = ? WHERE id = ?', (new_status, teacher_id))
    conn.commit()
    conn.close()
    
    name = teacher['tutor_name'] or teacher['mobile']
    action = 'enabled' if new_status else 'disabled'
    flash(f'Teacher "{name}" {action} successfully', 'success')
    return redirect(request.referrer or url_for('admin.teachers'))

# ─── Students ──────────────────────────────────────────

@admin_bp.route('/students')
@require_admin
def students():
    """List all students"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT s.id, s.name, s.phone, s.created_at, s.is_active,
               b.name as batch_name, u.tuition_name, u.tutor_name
        FROM students s
        LEFT JOIN batches b ON s.batch_id = b.id
        LEFT JOIN users u ON s.user_id = u.id
        ORDER BY s.created_at DESC LIMIT 500
    ''')
    students_list = cursor.fetchall()
    conn.close()
    
    return render_template('admin/students.html', students=students_list)

@admin_bp.route('/students/<int:student_id>/edit', methods=['GET', 'POST'])
@require_admin
def edit_student(student_id):
    """Edit a student's details"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM students WHERE id = ?', (student_id,))
    student = cursor.fetchone()
    if not student:
        conn.close()
        flash('Student not found', 'error')
        return redirect(url_for('admin.students'))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        batch_id = request.form.get('batch_id', type=int)
        school_name = request.form.get('school_name', '').strip()
        standard = request.form.get('standard', '').strip()
        address = request.form.get('address', '').strip()
        
        if not name or not phone:
            flash('Name and phone are required', 'error')
        else:
            conn.execute(
                '''UPDATE students SET name = ?, phone = ?, batch_id = ?,
                   school_name = ?, standard = ?, address = ? WHERE id = ?''',
                (name, phone, batch_id, school_name or None, standard or None, address or None, student_id)
            )
            conn.commit()
            flash('Student updated successfully', 'success')
        
        conn.close()
        return redirect(url_for('admin.edit_student', student_id=student_id))
    
    # GET: fetch batches for the same tutor
    cursor.execute('SELECT id, name FROM batches WHERE user_id = ? ORDER BY name', (student['user_id'],))
    batches = cursor.fetchall()
    
    cursor.execute('SELECT tutor_name, tuition_name FROM users WHERE id = ?', (student['user_id'],))
    user = cursor.fetchone()
    conn.close()
    
    return render_template('admin/student_edit.html',
        student=student, batches=batches,
        teacher_name=user['tutor_name'] if user else None,
        tuition_name=user['tuition_name'] if user else None
    )

@admin_bp.route('/students/<int:student_id>/delete', methods=['POST'])
@require_admin
def delete_student(student_id):
    """Delete a student and related data"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT name FROM students WHERE id = ?', (student_id,))
    student = cursor.fetchone()
    if not student:
        conn.close()
        flash('Student not found', 'error')
        return redirect(url_for('admin.students'))
    
    # Cascade delete: fees → attendance → homework → student
    cursor.execute('DELETE FROM student_fee_records WHERE student_id = ?', (student_id,))
    cursor.execute('DELETE FROM attendance WHERE student_id = ?', (student_id,))
    cursor.execute('DELETE FROM homework WHERE student_id = ?', (student_id,))
    cursor.execute('DELETE FROM students WHERE id = ?', (student_id,))
    
    conn.commit()
    conn.close()
    
    flash(f'Student "{student["name"]}" deleted successfully', 'success')
    return redirect(url_for('admin.students'))

@admin_bp.route('/students/<int:student_id>/toggle', methods=['POST'])
@require_admin
def toggle_student(student_id):
    """Enable or disable a student"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT is_active, name FROM students WHERE id = ?', (student_id,))
    student = cursor.fetchone()
    if not student:
        conn.close()
        flash('Student not found', 'error')
        return redirect(url_for('admin.students'))
    
    new_status = 0 if student['is_active'] else 1
    conn.execute('UPDATE students SET is_active = ? WHERE id = ?', (new_status, student_id))
    conn.commit()
    conn.close()
    
    action = 'enabled' if new_status else 'disabled'
    flash(f'Student "{student["name"]}" {action} successfully', 'success')
    return redirect(request.referrer or url_for('admin.students'))

# ─── Batches ───────────────────────────────────────────

@admin_bp.route('/batches')
@require_admin
def batches():
    """List all batches across all tutors"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT b.id, b.name, b.start_time, b.end_time, b.days, b.created_at, b.is_active,
               u.tutor_name, u.tuition_name,
               (SELECT COUNT(*) FROM students WHERE batch_id = b.id) as student_count
        FROM batches b
        LEFT JOIN users u ON b.user_id = u.id
        ORDER BY b.created_at DESC
    ''')
    batches_list = cursor.fetchall()
    conn.close()
    
    return render_template('admin/batches.html', batches=batches_list)

@admin_bp.route('/batches/<int:batch_id>')
@require_admin
def batch_detail(batch_id):
    """Detail view of a batch with its students"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM batches WHERE id = ?', (batch_id,))
    batch = cursor.fetchone()
    if not batch:
        conn.close()
        flash('Batch not found', 'error')
        return redirect(url_for('admin.batches'))
    
    cursor.execute('SELECT tutor_name, tuition_name FROM users WHERE id = ?', (batch['user_id'],))
    user = cursor.fetchone()
    
    cursor.execute('''
        SELECT id, name, phone, school_name, standard, created_at
        FROM students WHERE batch_id = ? ORDER BY name
    ''', (batch_id,))
    students_list = cursor.fetchall()
    
    conn.close()
    
    return render_template('admin/batch_detail.html',
        batch=batch, students=students_list,
        tutor_name=user['tutor_name'] if user else None,
        tuition_name=user['tuition_name'] if user else None
    )

@admin_bp.route('/batches/<int:batch_id>/delete', methods=['POST'])
@require_admin
def delete_batch(batch_id):
    """Delete a batch (only if it has no students)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT name FROM batches WHERE id = ?', (batch_id,))
    batch = cursor.fetchone()
    if not batch:
        conn.close()
        flash('Batch not found', 'error')
        return redirect(url_for('admin.batches'))
    
    # Check for students in this batch
    cursor.execute('SELECT COUNT(*) as count FROM students WHERE batch_id = ?', (batch_id,))
    student_count = cursor.fetchone()['count']
    
    if student_count > 0:
        conn.close()
        flash(f'Cannot delete batch "{batch["name"]}" — it still has {student_count} student(s). Remove them first.', 'warning')
        return redirect(url_for('admin.batch_detail', batch_id=batch_id))
    
    cursor.execute('DELETE FROM batches WHERE id = ?', (batch_id,))
    conn.commit()
    conn.close()
    
    flash(f'Batch "{batch["name"]}" deleted successfully', 'success')
    return redirect(url_for('admin.batches'))

@admin_bp.route('/batches/<int:batch_id>/toggle', methods=['POST'])
@require_admin
def toggle_batch(batch_id):
    """Enable or disable a batch"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT is_active, name FROM batches WHERE id = ?', (batch_id,))
    batch = cursor.fetchone()
    if not batch:
        conn.close()
        flash('Batch not found', 'error')
        return redirect(url_for('admin.batches'))
    
    new_status = 0 if batch['is_active'] else 1
    conn.execute('UPDATE batches SET is_active = ? WHERE id = ?', (new_status, batch_id))
    conn.commit()
    conn.close()
    
    action = 'enabled' if new_status else 'disabled'
    flash(f'Batch "{batch["name"]}" {action} successfully', 'success')
    return redirect(request.referrer or url_for('admin.batches'))

# ─── Fees ──────────────────────────────────────────────

@admin_bp.route('/fees')
@require_admin
def fees():
    """Aggregate fee overview across all tutors"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Aggregate stats
    cursor.execute("SELECT COALESCE(SUM(paid_amount), 0) as total FROM student_fee_records WHERE status = 'paid'")
    total_collected = cursor.fetchone()['total']
    
    cursor.execute("SELECT COALESCE(SUM(amount - paid_amount), 0) as total FROM student_fee_records WHERE status = 'pending'")
    total_pending = cursor.fetchone()['total']
    
    cursor.execute("SELECT COALESCE(SUM(amount - paid_amount), 0) as total FROM student_fee_records WHERE status = 'overdue'")
    total_overdue = cursor.fetchone()['total']
    
    cursor.execute('SELECT COUNT(*) as total FROM student_fee_records')
    total_records = cursor.fetchone()['total']
    
    # Recent fee records
    cursor.execute('''
        SELECT f.month, f.amount, f.paid_amount, f.status, f.updated_at,
               s.name as student_name, u.tuition_name
        FROM student_fee_records f
        LEFT JOIN students s ON f.student_id = s.id
        LEFT JOIN users u ON f.user_id = u.id
        ORDER BY f.updated_at DESC LIMIT 200
    ''')
    fee_records = cursor.fetchall()
    
    conn.close()
    
    return render_template('admin/fees.html',
        total_collected=total_collected,
        total_pending=total_pending,
        total_overdue=total_overdue,
        total_records=total_records,
        fee_records=fee_records
    )
