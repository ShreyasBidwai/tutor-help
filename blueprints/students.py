"""Student management blueprint"""
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from datetime import date
from database import get_db_connection
from utils import require_login

students_bp = Blueprint('students', __name__, url_prefix='')

@students_bp.route('/students')
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
    return render_template('students/students.html', 
                         students=students, 
                         batches=batches,
                         search_query=search_query,
                         batch_filter=batch_filter)

@students_bp.route('/students/add', methods=['GET', 'POST'])
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
            return redirect(url_for('students.students'))
    
    # Get batches for dropdown
    cursor.execute('SELECT * FROM batches WHERE user_id = ? ORDER BY name', (session['user_id'],))
    batches = cursor.fetchall()
    conn.close()
    
    return render_template('students/add_student.html', batches=batches)

@students_bp.route('/students/<int:student_id>/edit', methods=['GET', 'POST'])
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
            return redirect(url_for('students.students'))
    
    # Get student
    cursor.execute('SELECT * FROM students WHERE id = ? AND user_id = ?', (student_id, session['user_id']))
    student = cursor.fetchone()
    
    if not student:
        conn.close()
        return redirect(url_for('students.students'))
    
    # Get batches
    cursor.execute('SELECT * FROM batches WHERE user_id = ? ORDER BY name', (session['user_id'],))
    batches = cursor.fetchall()
    conn.close()
    
    return render_template('students/edit_student.html', student=student, batches=batches)

@students_bp.route('/students/<int:student_id>')
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
        return redirect(url_for('students.students'))
    
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
    
    return render_template('students/view_student.html', 
                         student=student, 
                         attendance_stats=attendance_stats,
                         recent_attendance=recent_attendance,
                         today=date.today().isoformat())

@students_bp.route('/api/students/<int:student_id>', methods=['DELETE'])
@require_login
def delete_student(student_id):
    """Delete a student (API endpoint)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM students WHERE id = ? AND user_id = ?', (student_id, session['user_id']))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

