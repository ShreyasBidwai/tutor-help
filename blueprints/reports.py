"""Attendance reports blueprint"""
from flask import Blueprint, render_template, redirect, url_for, session, request
from datetime import date, timedelta
from calendar import monthrange
from database import get_db_connection
from utils import require_login, get_ist_today, cleanup_old_attendance

reports_bp = Blueprint('reports', __name__, url_prefix='')

@reports_bp.route('/reports')
@require_login
def reports():
    """Attendance summary report for all batches and students (last 7 days)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    user_id = session['user_id']
    today = get_ist_today()
    active_tab = request.args.get('tab', 'batches')  # Default to batches tab
    
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
    
    # Get all students for student reports
    cursor.execute('''
        SELECT s.*, b.name as batch_name
        FROM students s
        LEFT JOIN batches b ON s.batch_id = b.id
        WHERE s.user_id = ?
        ORDER BY s.name
    ''', (user_id,))
    all_students = cursor.fetchall()
    
    student_reports = []
    for student in all_students:
        student_id = student['id']
        
        # Get attendance for last 7 days
        placeholders = ','.join(['?'] * len(date_range))
        
        # Check which columns exist
        cursor.execute("PRAGMA table_info(attendance)")
        columns = [row[1] for row in cursor.fetchall()]
        has_present_column = 'present' in columns
        has_status_column = 'status' in columns
        
        total_sessions = 0
        attended_sessions = 0
        
        if has_status_column:
            query = f'''
                SELECT 
                    COUNT(*) as total_sessions,
                    COALESCE(SUM(CASE WHEN status IN (1, 2) THEN 1 ELSE 0 END), 0) as attended_sessions
                FROM attendance
                WHERE student_id = ?
                AND user_id = ?
                AND date IN ({placeholders})
            '''
        elif has_present_column:
            query = f'''
                SELECT 
                    COUNT(*) as total_sessions,
                    COALESCE(SUM(CASE WHEN present = 1 THEN 1 ELSE 0 END), 0) as attended_sessions
                FROM attendance
                WHERE student_id = ?
                AND user_id = ?
                AND date IN ({placeholders})
            '''
        else:
            query = None
        
        if query:
            params = [student_id, user_id] + date_range
            cursor.execute(query, params)
            result = cursor.fetchone()
            if result:
                total_sessions = result['total_sessions'] if result['total_sessions'] is not None else 0
                attended_sessions = result['attended_sessions'] if result['attended_sessions'] is not None else 0
        
        # Calculate attendance percentage
        total_expected = 7  # 7 days
        if total_expected > 0:
            attendance_percentage = round((attended_sessions / total_expected) * 100)
            attendance_percentage = min(attendance_percentage, 100)
        else:
            attendance_percentage = 0
        
        student_reports.append({
            'student_id': student_id,
            'student_name': student['name'],
            'student_phone': student['phone'],
            'batch_name': student['batch_name'] or 'No Batch',
            'total_expected': total_expected,
            'attended_sessions': attended_sessions,
            'attendance_percentage': attendance_percentage
        })
    
    conn.close()
    
    return render_template('reports/reports.html', 
                         batch_reports=batch_reports,
                         student_reports=student_reports,
                         date_range=date_range,
                         active_tab=active_tab)

@reports_bp.route('/reports/batch/<int:batch_id>')
@require_login
def batch_report_detail(batch_id):
    """Detailed attendance report for a specific batch (last 30 days)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    user_id = session['user_id']
    today = get_ist_today()
    
    # Verify batch belongs to user
    cursor.execute('SELECT * FROM batches WHERE id = ? AND user_id = ?', (batch_id, user_id))
    batch = cursor.fetchone()
    
    if not batch:
        conn.close()
        return redirect(url_for('reports.reports'))
    
    # Calculate date range (last 30 days including today)
    date_range = []
    for i in range(29, -1, -1):  # 29 days ago to today
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
        
        # Calculate student statistics for 30 days
        total_days = len(date_range)
        present_count = sum(1 for status in attendance_by_date.values() if status == 1)
        late_count = sum(1 for status in attendance_by_date.values() if status == 2)
        absent_count = sum(1 for status in attendance_by_date.values() if status == 0)
        na_count = sum(1 for status in attendance_by_date.values() if status == -1)
        attended_count = present_count + late_count
        
        # Check if absent today
        today_str = today.isoformat()
        is_absent_today = attendance_by_date.get(today_str, -1) == 0
        
        # Calculate attendance percentage (only for days with records)
        days_with_records = total_days - na_count
        if days_with_records > 0:
            attendance_percentage = round((attended_count / days_with_records) * 100)
        else:
            attendance_percentage = 0
        
        student_reports.append({
            'student_id': student_id,
            'student_name': student['name'],
            'attendance_percentage': attendance_percentage,
            'is_absent_today': is_absent_today,
            'is_high_attendance': attendance_percentage >= 80,
            'is_low_attendance': attendance_percentage < 60
        })
    
    conn.close()
    
    return render_template('reports/batch_report_detail.html',
                         batch=batch,
                         student_reports=student_reports,
                         date_range=date_range)

@reports_bp.route('/reports/student/<int:student_id>')
@require_login
def student_report_detail(student_id):
    """Monthly attendance grid for a specific student (current month only)"""
    # Clean up old attendance records before showing report
    cleanup_old_attendance()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    user_id = session['user_id']
    today = get_ist_today()
    
    # Verify student belongs to user
    cursor.execute('''
        SELECT s.*, b.name as batch_name
        FROM students s
        LEFT JOIN batches b ON s.batch_id = b.id
        WHERE s.id = ? AND s.user_id = ?
    ''', (student_id, user_id))
    student = cursor.fetchone()
    
    if not student:
        conn.close()
        return redirect(url_for('reports.reports'))
    
    # Only allow viewing current month - ignore month/year params
    month = today.month
    year = today.year
    
    # Generate all dates for the selected month
    month_days = monthrange(year, month)[1]  # Number of days in month
    
    date_range = []
    for day in range(1, month_days + 1):
        d = date(year, month, day)
        date_range.append(d.isoformat())
    
    # Get first day of month to calculate which day of week it starts on
    first_day = date(year, month, 1)
    first_day_weekday = first_day.weekday()  # 0 = Monday, 6 = Sunday
    
    # Get last day of month to calculate which day of week it ends on
    last_day = date(year, month, month_days)
    last_day_weekday = last_day.weekday()  # 0 = Monday, 6 = Sunday
    remaining_cells = 6 - last_day_weekday  # Empty cells needed after month ends
    
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
            # Use present column
            cursor.execute('''
                SELECT present
                FROM attendance
                WHERE student_id = ? AND date = ? AND user_id = ?
            ''', (student_id, date_str, user_id))
        else:
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
    
    # Calculate statistics for the month
    present_count = sum(1 for status in attendance_by_date.values() if status == 1)
    late_count = sum(1 for status in attendance_by_date.values() if status == 2)
    absent_count = sum(1 for status in attendance_by_date.values() if status == 0)
    na_count = sum(1 for status in attendance_by_date.values() if status == -1)
    attended_count = present_count + late_count
    
    # Calculate attendance percentage (only for days with records)
    days_with_records = month_days - na_count
    if days_with_records > 0:
        attendance_percentage = round((attended_count / days_with_records) * 100)
    else:
        attendance_percentage = 0
    
    # Month names
    month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
    month_name = month_names[month - 1]
    
    conn.close()
    
    return render_template('reports/student_report_detail.html',
                         student=student,
                         attendance_by_date=attendance_by_date,
                         date_range=date_range,
                         present_count=present_count,
                         late_count=late_count,
                         absent_count=absent_count,
                         na_count=na_count,
                         attended_count=attended_count,
                         attendance_percentage=attendance_percentage,
                         today=today,
                         month=month,
                         year=year,
                         month_name=month_name,
                         month_days=month_days,
                         first_day_weekday=first_day_weekday,
                         last_day_weekday=last_day_weekday,
                         remaining_cells=remaining_cells)

