"""Student management blueprint"""
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, flash
from datetime import date
from database import get_db_connection
from utils import require_login, get_ist_today
import sqlite3
import re

students_bp = Blueprint('students', __name__, url_prefix='')

def validate_name(name):
    """Validate name: only letters and spaces, no numbers or special characters"""
    if not name or not name.strip():
        return False
    # Allow only letters (including accented characters) and spaces
    name_pattern = re.compile(r'^[a-zA-Z\s\u00C0-\u017F\u0100-\u017F\u0180-\u024F\u1E00-\u1EFF]+$')
    return bool(name_pattern.match(name.strip()))

@students_bp.route('/students')
@require_login
def students():
    """List all students with pagination"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get pagination parameters
    page = max(1, request.args.get('page', 1, type=int))
    per_page = 20
    offset = (page - 1) * per_page
    
    # Get search and filter parameters
    search_query = request.args.get('search', '').strip()
    batch_filter = request.args.get('batch', type=int)
    
    # Build base query for counting
    count_query = '''
        SELECT COUNT(*) as total
        FROM students s 
        WHERE s.user_id = ?
    '''
    count_params = [session['user_id']]
    
    # Build query for fetching data
    query = '''
        SELECT s.*, b.name as batch_name 
        FROM students s 
        LEFT JOIN batches b ON s.batch_id = b.id 
        WHERE s.user_id = ?
    '''
    params = [session['user_id']]
    
    if search_query:
        query += ' AND (s.name LIKE ? OR s.phone LIKE ?)'
        count_query += ' AND (s.name LIKE ? OR s.phone LIKE ?)'
        search_pattern = f'%{search_query}%'
        params.extend([search_pattern, search_pattern])
        count_params.extend([search_pattern, search_pattern])
    
    if batch_filter:
        query += ' AND s.batch_id = ?'
        count_query += ' AND s.batch_id = ?'
        params.append(batch_filter)
        count_params.append(batch_filter)
    
    query += ' ORDER BY s.name LIMIT ? OFFSET ?'
    params.extend([per_page, offset])
    
    # Get total count
    cursor.execute(count_query, count_params)
    total_count = cursor.fetchone()['total']
    total_pages = (total_count + per_page - 1) // per_page if total_count > 0 else 1
    
    # Validate page number
    if page > total_pages and total_pages > 0:
        page = total_pages
        offset = (page - 1) * per_page
        params[-2] = per_page
        params[-1] = offset
    
    # Get paginated students
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
                         batch_filter=batch_filter,
                         page=page,
                         total_pages=total_pages,
                         total_count=total_count,
                         per_page=per_page)

@students_bp.route('/students/add', methods=['GET', 'POST'])
@require_login
def add_student():
    """Add a new student"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get batches for dropdown (needed for both GET and error cases)
    cursor.execute('SELECT * FROM batches WHERE user_id = ? ORDER BY name', (session['user_id'],))
    batches = cursor.fetchall()
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        batch_id = request.form.get('batch_id')
        address = request.form.get('address', '').strip()
        school_name = request.form.get('school_name', '').strip()
        standard = request.form.get('standard', '').strip()
        
        # Validation
        if not name or not name.strip():
            flash('Student name is required', 'error')
            conn.close()
            return render_template('students/add_student.html', batches=batches)
        
        if not validate_name(name):
            flash('Student name can only contain letters and spaces. No numbers or special characters allowed.', 'error')
            conn.close()
            return render_template('students/add_student.html', batches=batches)
        
        if not phone or len(phone) != 10 or not phone.isdigit():
            flash('Please enter a valid 10-digit phone number', 'error')
            conn.close()
            return render_template('students/add_student.html', batches=batches)
        
        if not batch_id:
            flash('Please select a batch', 'error')
            conn.close()
            return render_template('students/add_student.html', batches=batches)
        
        # Check for duplicate phone number
        cursor.execute('SELECT id FROM students WHERE phone = ? AND user_id = ?', (phone, session['user_id']))
        if cursor.fetchone():
            flash('A student with this phone number already exists', 'error')
            conn.close()
            return render_template('students/add_student.html', batches=batches)
        
        if name and phone and batch_id:
            try:
                cursor.execute('''
                    INSERT INTO students (name, phone, batch_id, address, school_name, standard, user_id) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (name, phone, int(batch_id), address, school_name, standard, session['user_id']))
                conn.commit()
                conn.close()
                flash('Student added successfully!', 'success')
                return redirect(url_for('students.students'))
            except sqlite3.IntegrityError:
                conn.rollback()
                conn.close()
                flash('A student with this phone number already exists', 'error')
                return render_template('students/add_student.html', batches=batches)
    
    # GET request - batches already fetched above
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
        
        # Validation
        if not name or not name.strip():
            flash('Student name is required', 'error')
            conn.close()
            cursor.execute('SELECT * FROM batches WHERE user_id = ? ORDER BY name', (session['user_id'],))
            batches = cursor.fetchall()
            cursor.execute('SELECT * FROM students WHERE id = ? AND user_id = ?', (student_id, session['user_id']))
            student = cursor.fetchone()
            conn.close()
            return render_template('students/edit_student.html', student=student, batches=batches)
        
        if not validate_name(name):
            flash('Student name can only contain letters and spaces. No numbers or special characters allowed.', 'error')
            conn.close()
            cursor.execute('SELECT * FROM batches WHERE user_id = ? ORDER BY name', (session['user_id'],))
            batches = cursor.fetchall()
            cursor.execute('SELECT * FROM students WHERE id = ? AND user_id = ?', (student_id, session['user_id']))
            student = cursor.fetchone()
            conn.close()
            return render_template('students/edit_student.html', student=student, batches=batches)
        
        if not phone or len(phone) != 10 or not phone.isdigit():
            flash('Please enter a valid 10-digit phone number', 'error')
            conn.close()
            cursor.execute('SELECT * FROM batches WHERE user_id = ? ORDER BY name', (session['user_id'],))
            batches = cursor.fetchall()
            cursor.execute('SELECT * FROM students WHERE id = ? AND user_id = ?', (student_id, session['user_id']))
            student = cursor.fetchone()
            conn.close()
            return render_template('students/edit_student.html', student=student, batches=batches)
        
        if not batch_id:
            flash('Please select a batch', 'error')
            conn.close()
            cursor.execute('SELECT * FROM batches WHERE user_id = ? ORDER BY name', (session['user_id'],))
            batches = cursor.fetchall()
            cursor.execute('SELECT * FROM students WHERE id = ? AND user_id = ?', (student_id, session['user_id']))
            student = cursor.fetchone()
            conn.close()
            return render_template('students/edit_student.html', student=student, batches=batches)
        
        # Check for duplicate phone number (excluding current student)
        cursor.execute('SELECT id FROM students WHERE phone = ? AND user_id = ? AND id != ?', (phone, session['user_id'], student_id))
        if cursor.fetchone():
            flash('A student with this phone number already exists', 'error')
            conn.close()
            cursor.execute('SELECT * FROM batches WHERE user_id = ? ORDER BY name', (session['user_id'],))
            batches = cursor.fetchall()
            cursor.execute('SELECT * FROM students WHERE id = ? AND user_id = ?', (student_id, session['user_id']))
            student = cursor.fetchone()
            conn.close()
            return render_template('students/edit_student.html', student=student, batches=batches)
        
        if name and phone and batch_id:
            try:
                cursor.execute('''
                    UPDATE students 
                    SET name = ?, phone = ?, batch_id = ?, address = ?, school_name = ?, standard = ?
                    WHERE id = ? AND user_id = ?
                ''', (name, phone, int(batch_id), address, school_name, standard, student_id, session['user_id']))
                conn.commit()
                conn.close()
                flash('Student updated successfully!', 'success')
                return redirect(url_for('students.students'))
            except sqlite3.IntegrityError:
                conn.rollback()
                conn.close()
                flash('A student with this phone number already exists', 'error')
                cursor.execute('SELECT * FROM batches WHERE user_id = ? ORDER BY name', (session['user_id'],))
                batches = cursor.fetchall()
                cursor.execute('SELECT * FROM students WHERE id = ? AND user_id = ?', (student_id, session['user_id']))
                student = cursor.fetchone()
                conn.close()
                return render_template('students/edit_student.html', student=student, batches=batches)
    
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
                         today=get_ist_today().isoformat())

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

