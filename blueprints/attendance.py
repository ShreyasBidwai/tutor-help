"""Attendance management blueprint"""
from flask import Blueprint, render_template, request, session, jsonify
from datetime import date
from database import get_db_connection
from utils import require_login

attendance_bp = Blueprint('attendance', __name__, url_prefix='')

@attendance_bp.route('/attendance')
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
    
    return render_template('attendance/attendance.html', 
                         students_by_batch=students_by_batch,
                         students=students,  # Keep for backward compatibility
                         selected_date=selected_date,
                         today=date.today().isoformat(),
                         batches=batches,
                         batch_filter=batch_filter)

@attendance_bp.route('/api/attendance/mark', methods=['POST'])
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

