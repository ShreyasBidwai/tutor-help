"""Export functionality blueprint - CSV exports for mobile-friendly downloads"""
from flask import Blueprint, Response, session, request
from database import get_db_connection
from utils import require_login, get_ist_today
from datetime import date, datetime, timedelta
import csv
import io

export_bp = Blueprint('export', __name__, url_prefix='')

@export_bp.route('/export/students')
@require_login
def export_students():
    """Export students as CSV"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT s.name, s.phone, b.name as batch_name, s.standard, s.school_name, s.address, s.created_at
        FROM students s
        LEFT JOIN batches b ON s.batch_id = b.id
        WHERE s.user_id = ?
        ORDER BY s.name
    ''', (session['user_id'],))
    students = cursor.fetchall()
    conn.close()
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Name', 'Phone', 'Batch', 'Standard', 'School', 'Address', 'Added Date'])
    
    # Write data
    for student in students:
        writer.writerow([
            student['name'],
            student['phone'],
            student['batch_name'] or '',
            student['standard'] or '',
            student['school_name'] or '',
            student['address'] or '',
            student['created_at'] or ''
        ])
    
    # Create response
    output.seek(0)
    response = Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=students_{get_ist_today().isoformat()}.csv'}
    )
    
    return response

@export_bp.route('/export/attendance')
@require_login
def export_attendance():
    """Export attendance as CSV"""
    date_from = request.args.get('from', (get_ist_today() - timedelta(days=30)).isoformat())
    date_to = request.args.get('to', get_ist_today().isoformat())
    batch_id = request.args.get('batch', type=int)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Build query
    query = '''
        SELECT s.name as student_name, b.name as batch_name, a.date,
               CASE 
                   WHEN COALESCE(a.status, a.present, 0) = 1 THEN 'Present'
                   WHEN COALESCE(a.status, a.present, 0) = 2 THEN 'Late'
                   ELSE 'Absent'
               END as status
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        LEFT JOIN batches b ON s.batch_id = b.id
        WHERE a.user_id = ? AND a.date BETWEEN ? AND ?
    '''
    params = [session['user_id'], date_from, date_to]
    
    if batch_id:
        query += ' AND s.batch_id = ?'
        params.append(batch_id)
    
    query += ' ORDER BY a.date DESC, s.name'
    
    cursor.execute(query, params)
    attendance_records = cursor.fetchall()
    conn.close()
    
    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Date', 'Student Name', 'Batch', 'Status'])
    
    # Write data
    for record in attendance_records:
        writer.writerow([
            record['date'],
            record['student_name'],
            record['batch_name'] or '',
            record['status']
        ])
    
    output.seek(0)
    response = Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=attendance_{date_from}_to_{date_to}.csv'}
    )
    
    return response

@export_bp.route('/export/reports/batch/<int:batch_id>')
@require_login
def export_batch_report(batch_id):
    """Export batch report as CSV"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Verify batch belongs to user
    cursor.execute('SELECT name FROM batches WHERE id = ? AND user_id = ?', (batch_id, session['user_id']))
    batch = cursor.fetchone()
    
    if not batch:
        conn.close()
        return {'error': 'Batch not found'}, 404
    
    # Get 30-day attendance for students in batch
    today = get_ist_today()
    thirty_days_ago = today - timedelta(days=30)
    
    cursor.execute('''
        SELECT s.name, s.phone,
               COUNT(a.id) as total_days,
               SUM(CASE WHEN COALESCE(a.status, a.present, 0) = 1 THEN 1 ELSE 0 END) as present_days,
               SUM(CASE WHEN COALESCE(a.status, a.present, 0) = 2 THEN 1 ELSE 0 END) as late_days,
               SUM(CASE WHEN COALESCE(a.status, a.present, 0) = 0 THEN 1 ELSE 0 END) as absent_days,
               ROUND(100.0 * SUM(CASE WHEN COALESCE(a.status, a.present, 0) IN (1, 2) THEN 1 ELSE 0 END) / NULLIF(COUNT(a.id), 0), 1) as attendance_percentage
        FROM students s
        LEFT JOIN attendance a ON s.id = a.student_id AND a.date >= ? AND a.date <= ? AND a.user_id = ?
        WHERE s.batch_id = ? AND s.user_id = ?
        GROUP BY s.id, s.name, s.phone
        ORDER BY s.name
    ''', (thirty_days_ago.isoformat(), today.isoformat(), session['user_id'], batch_id, session['user_id']))
    
    students = cursor.fetchall()
    conn.close()
    
    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Student Name', 'Phone', 'Total Days', 'Present', 'Late', 'Absent', 'Attendance %'])
    
    # Write data
    for student in students:
        writer.writerow([
            student['name'],
            student['phone'],
            student['total_days'] or 0,
            student['present_days'] or 0,
            student['late_days'] or 0,
            student['absent_days'] or 0,
            f"{student['attendance_percentage'] or 0}%"
        ])
    
    output.seek(0)
    batch_name_safe = batch['name'].replace(' ', '_')
    response = Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=batch_report_{batch_name_safe}_{get_ist_today().isoformat()}.csv'}
    )
    
    return response

