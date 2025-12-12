"""Attendance reports blueprint"""
from flask import Blueprint, render_template, redirect, url_for, session, request
from datetime import date, timedelta
from calendar import monthrange
from database import get_db_connection
from utils import require_login, get_ist_today, cleanup_old_attendance

# Map day abbreviations to weekday numbers (0=Monday, 6=Sunday)
DAY_MAP = {
    'mo': 0,  # Monday
    'tu': 1,  # Tuesday
    'we': 2,  # Wednesday
    'th': 3,  # Thursday
    'fr': 4,  # Friday
    'sa': 5,  # Saturday
    'su': 6   # Sunday
}

reports_bp = Blueprint('reports', __name__, url_prefix='')

@reports_bp.route('/reports')
@require_login
def reports():
    """Attendance summary report for all batches and students (current month)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    user_id = session['user_id']
    today = get_ist_today()
    active_tab = request.args.get('tab', 'batches')  # Default to batches tab
    
    # Get current month date range
    current_month = today.month
    current_year = today.year
    month_days = monthrange(current_year, current_month)[1]
    
    # Generate all dates for current month (up to today)
    current_month_dates = []
    for day in range(1, month_days + 1):
        d = date(current_year, current_month, day)
        if d <= today:
            current_month_dates.append(d)
    
    # Get all batches with their schedule days
    cursor.execute('SELECT * FROM batches WHERE user_id = ? ORDER BY name', (user_id,))
    batches = cursor.fetchall()
    
    batch_reports = []
    for batch in batches:
        batch_id = batch['id']
        batch_days_str = batch['days'] or ''
        
        # Parse batch days (e.g., "mo,tu,we" -> [0, 1, 2])
        batch_weekdays = []
        if batch_days_str:
            day_list = [d.strip() for d in batch_days_str.split(',') if d.strip()]
            batch_weekdays = [DAY_MAP[day] for day in day_list if day in DAY_MAP]
        
        # Get all students in this batch
        cursor.execute('SELECT id FROM students WHERE batch_id = ? AND user_id = ?', (batch_id, user_id))
        students = cursor.fetchall()
        student_ids = [s['id'] for s in students]
        
        if not student_ids:
            continue
        
        # Calculate total expected sessions for current month
        # Count class days in current month (up to today) based on batch schedule
        total_class_days = 0
        if batch_weekdays:
            for d in current_month_dates:
                if d.weekday() in batch_weekdays:
                    total_class_days += 1
        else:
            # If no batch days specified, count all days up to today
            total_class_days = len(current_month_dates)
        
        # Total expected = number of students * number of class days
        total_expected = len(student_ids) * total_class_days
        
        # Get actual attendance records for these students in current month
        attended_sessions = 0
        
        if student_ids and total_class_days > 0:
            placeholders = ','.join(['?'] * len(student_ids))
            month_date_strings = [d.isoformat() for d in current_month_dates]
            date_placeholders = ','.join(['?'] * len(month_date_strings))
            
            # Check if 'present' column exists in attendance table
            cursor.execute("PRAGMA table_info(attendance)")
            columns = [row[1] for row in cursor.fetchall()]
            has_present_column = 'present' in columns
            has_status_column = 'status' in columns
            
            # Build query based on available columns
            if has_status_column:
                # Use status column (new schema) - count present (1) or late (2)
                query = f'''
                    SELECT 
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
                params = student_ids + [user_id] + month_date_strings
                cursor.execute(query, params)
                result = cursor.fetchone()
                if result:
                    attended_sessions = result['attended_sessions'] if result['attended_sessions'] is not None else 0
        
        # Calculate attendance percentage
        if total_expected > 0:
            attendance_percentage = round((attended_sessions / total_expected) * 100)
            attendance_percentage = min(attendance_percentage, 100)
        else:
            attendance_percentage = 0
        
        # Get today's attendance stats (Present and Absent)
        today_str = today.isoformat()
        present_today = 0
        absent_today = 0
        
        if student_ids:
            placeholders = ','.join(['?'] * len(student_ids))
            cursor.execute("PRAGMA table_info(attendance)")
            columns = [row[1] for row in cursor.fetchall()]
            has_present_column = 'present' in columns
            has_status_column = 'status' in columns
            
            if has_status_column:
                # Count present (1) and late (2) as present, absent (0) as absent
                query = f'''
                    SELECT 
                        COALESCE(SUM(CASE WHEN status IN (1, 2) THEN 1 ELSE 0 END), 0) as present_count,
                        COALESCE(SUM(CASE WHEN status = 0 THEN 1 ELSE 0 END), 0) as absent_count
                    FROM attendance
                    WHERE student_id IN ({placeholders})
                    AND user_id = ?
                    AND date = ?
                '''
            elif has_present_column:
                query = f'''
                    SELECT 
                        COALESCE(SUM(CASE WHEN present = 1 THEN 1 ELSE 0 END), 0) as present_count,
                        COALESCE(SUM(CASE WHEN present = 0 THEN 1 ELSE 0 END), 0) as absent_count
                    FROM attendance
                    WHERE student_id IN ({placeholders})
                    AND user_id = ?
                    AND date = ?
                '''
            else:
                query = None
            
            if query:
                params = student_ids + [user_id, today_str]
                cursor.execute(query, params)
                result = cursor.fetchone()
                if result:
                    present_today = result['present_count'] if result['present_count'] is not None else 0
                    absent_today = result['absent_count'] if result['absent_count'] is not None else 0
        
        batch_reports.append({
            'batch_id': batch_id,
            'batch_name': batch['name'],
            'student_count': len(student_ids),
            'total_expected': total_expected,
            'attended_sessions': attended_sessions,
            'attendance_percentage': attendance_percentage,
            'present_today': present_today,
            'absent_today': absent_today
        })
    
    # Get all students for student reports with batch info
    cursor.execute('''
        SELECT s.*, b.name as batch_name, b.days as batch_days
        FROM students s
        LEFT JOIN batches b ON s.batch_id = b.id
        WHERE s.user_id = ?
        ORDER BY s.name
    ''', (user_id,))
    all_students = cursor.fetchall()
    
    # Get current month date range
    today = get_ist_today()
    current_month = today.month
    current_year = today.year
    month_days = monthrange(current_year, current_month)[1]
    
    # Generate all dates for current month
    current_month_dates = []
    for day in range(1, month_days + 1):
        d = date(current_year, current_month, day)
        # Only include dates up to today (not future dates)
        if d <= today:
            current_month_dates.append(d)
    
    student_reports = []
    for student in all_students:
        student_id = student['id']
        batch_days_str = student['batch_days'] or ''
        
        # Parse batch days (e.g., "mo,tu,we" -> [0, 1, 2])
        batch_weekdays = []
        if batch_days_str:
            day_list = [d.strip() for d in batch_days_str.split(',') if d.strip()]
            batch_weekdays = [DAY_MAP[day] for day in day_list if day in DAY_MAP]
        
        # Calculate total days classes happened in current month
        # Count dates that are:
        # 1. In the current month (up to today)
        # 2. On the batch's scheduled days
        total_days_classes = 0
        if batch_weekdays:
            for d in current_month_dates:
                if d.weekday() in batch_weekdays:
                    total_days_classes += 1
        else:
            # If no batch days specified, count all days up to today
            total_days_classes = len(current_month_dates)
        
        # Get present days (status 1 or 2) for current month
        present_days = 0
        if total_days_classes > 0:
            # Check which columns exist
            cursor.execute("PRAGMA table_info(attendance)")
            columns = [row[1] for row in cursor.fetchall()]
            has_present_column = 'present' in columns
            has_status_column = 'status' in columns
            
            # Get dates in current month as strings
            month_date_strings = [d.isoformat() for d in current_month_dates]
            
            if month_date_strings:
                placeholders = ','.join(['?'] * len(month_date_strings))
                
                if has_status_column:
                    query = f'''
                        SELECT COUNT(*) as present_count
                        FROM attendance
                        WHERE student_id = ?
                        AND user_id = ?
                        AND date IN ({placeholders})
                        AND status IN (1, 2)
                    '''
                elif has_present_column:
                    query = f'''
                        SELECT COUNT(*) as present_count
                        FROM attendance
                        WHERE student_id = ?
                        AND user_id = ?
                        AND date IN ({placeholders})
                        AND present = 1
                    '''
                else:
                    query = None
                
                if query:
                    params = [student_id, user_id] + month_date_strings
                    cursor.execute(query, params)
                    result = cursor.fetchone()
                    if result:
                        present_days = result['present_count'] if result['present_count'] is not None else 0
        
        # Calculate attendance percentage
        if total_days_classes > 0:
            attendance_percentage = round((present_days / total_days_classes) * 100)
            attendance_percentage = min(attendance_percentage, 100)
        else:
            attendance_percentage = 0
        
        student_reports.append({
            'student_id': student_id,
            'student_name': student['name'],
            'student_phone': student['phone'],
            'batch_name': student['batch_name'] or 'No Batch',
            'total_expected': total_days_classes,  # Total days classes happened
            'attended_sessions': present_days,  # Present days
            'attendance_percentage': attendance_percentage
        })
    
    conn.close()
    
    return render_template('reports/reports.html', 
                         batch_reports=batch_reports,
                         student_reports=student_reports,
                         active_tab=active_tab)

@reports_bp.route('/reports/batch/<int:batch_id>')
@require_login
def batch_report_detail(batch_id):
    """Detailed attendance report for a specific batch with date selection"""
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
    
    # Get selected date from query parameter (default to today)
    selected_date_str = request.args.get('date', today.isoformat())
    try:
        selected_date = date.fromisoformat(selected_date_str)
        # Ensure date is within current month
        if selected_date.month != today.month or selected_date.year != today.year:
            selected_date = today
    except (ValueError, AttributeError):
        selected_date = today
    
    selected_date_str = selected_date.isoformat()
    
    # Get all dates in current month for date picker
    current_month = today.month
    current_year = today.year
    month_days = monthrange(current_year, current_month)[1]
    month_date_range = []
    month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
    for day in range(1, month_days + 1):
        d = date(current_year, current_month, day)
        if d <= today:  # Only show dates up to today
            month_date_range.append({
                'date': d,
                'formatted': f"{d.day} {month_names[d.month - 1]} {d.year}"
            })
    
    # Calculate date range (last 30 days including today) for student reports
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
        
        # Get status for selected date
        selected_date_status = attendance_by_date.get(selected_date_str, -1)
        is_present_selected_date = selected_date_status == 1
        is_absent_selected_date = selected_date_status == 0
        is_late_selected_date = selected_date_status == 2
        
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
            'is_present_selected_date': is_present_selected_date,
            'is_absent_selected_date': is_absent_selected_date,
            'is_late_selected_date': is_late_selected_date,
            'selected_date_status': selected_date_status
        })
    
    # Get today's stats for the selected date
    cursor.execute("PRAGMA table_info(attendance)")
    columns = [row[1] for row in cursor.fetchall()]
    has_present_column = 'present' in columns
    has_status_column = 'status' in columns
    
    # Get all students in batch for stats
    cursor.execute('SELECT id FROM students WHERE batch_id = ? AND user_id = ?', (batch_id, user_id))
    all_students = cursor.fetchall()
    all_student_ids = [s['id'] for s in all_students]
    
    total_present = 0
    total_absent = 0
    total_late = 0
    
    if all_student_ids:
        placeholders = ','.join(['?'] * len(all_student_ids))
        
        if has_status_column:
            query = f'''
                SELECT 
                    COALESCE(SUM(CASE WHEN status = 1 THEN 1 ELSE 0 END), 0) as present_count,
                    COALESCE(SUM(CASE WHEN status = 0 THEN 1 ELSE 0 END), 0) as absent_count,
                    COALESCE(SUM(CASE WHEN status = 2 THEN 1 ELSE 0 END), 0) as late_count
                FROM attendance
                WHERE student_id IN ({placeholders})
                AND user_id = ?
                AND date = ?
            '''
        elif has_present_column:
            query = f'''
                SELECT 
                    COALESCE(SUM(CASE WHEN present = 1 THEN 1 ELSE 0 END), 0) as present_count,
                    COALESCE(SUM(CASE WHEN present = 0 THEN 1 ELSE 0 END), 0) as absent_count,
                    0 as late_count
                FROM attendance
                WHERE student_id IN ({placeholders})
                AND user_id = ?
                AND date = ?
            '''
        else:
            query = None
        
        if query:
            params = all_student_ids + [user_id, selected_date_str]
            cursor.execute(query, params)
            result = cursor.fetchone()
            if result:
                total_present = result['present_count'] if result['present_count'] is not None else 0
                total_absent = result['absent_count'] if result['absent_count'] is not None else 0
                total_late = result['late_count'] if result['late_count'] is not None else 0
    
    conn.close()
    
    return render_template('reports/batch_report_detail.html',
                         batch=batch,
                         student_reports=student_reports,
                         date_range=date_range,
                         selected_date=selected_date,
                         selected_date_str=selected_date_str,
                         month_date_range=month_date_range,
                         today=today,
                         total_present=total_present,
                         total_absent=total_absent,
                         total_late=total_late)

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

