"""Student portal blueprint"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from datetime import date, timedelta, datetime
from calendar import monthrange
from database import get_db_connection
from utils import require_login, get_ist_now, get_ist_today, cleanup_expired_homework

student_bp = Blueprint('student', __name__, url_prefix='')

@student_bp.route('/student/dashboard')
@require_login
def dashboard():
    """Student dashboard"""
    # Check if user is a student
    if session.get('role') != 'student':
        return redirect(url_for('dashboard.dashboard'))
    
    student_id = session.get('student_id')
    if not student_id:
        return redirect(url_for('auth.student_login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get student info
    cursor.execute('''
        SELECT s.*, b.name as batch_name, b.description as batch_description
        FROM students s
        LEFT JOIN batches b ON s.batch_id = b.id
        WHERE s.id = ?
    ''', (student_id,))
    student = cursor.fetchone()
    
    if not student:
        conn.close()
        session.clear()
        return redirect(url_for('auth.student_login'))
    
    # Get today's attendance (IST)
    today = get_ist_today().isoformat()
    cursor.execute('''
        SELECT status, present
        FROM attendance
        WHERE student_id = ? AND date = ?
    ''', (student_id, today))
    today_attendance = cursor.fetchone()
    
    # Get attendance stats (last 30 days)
    thirty_days_ago = (get_ist_today() - timedelta(days=29)).isoformat()
    cursor.execute('''
        SELECT 
            COUNT(*) as total_days,
            SUM(CASE WHEN COALESCE(status, present, 0) IN (1, 2) THEN 1 ELSE 0 END) as attended_days,
            SUM(CASE WHEN COALESCE(status, present, 0) = 1 THEN 1 ELSE 0 END) as present_days,
            SUM(CASE WHEN COALESCE(status, present, 0) = 2 THEN 1 ELSE 0 END) as late_days,
            SUM(CASE WHEN COALESCE(status, present, 0) = 0 THEN 1 ELSE 0 END) as absent_days
        FROM attendance
        WHERE student_id = ? AND date >= ?
    ''', (student_id, thirty_days_ago))
    attendance_stats = cursor.fetchone()
    
    # Calculate attendance percentage
    if attendance_stats and attendance_stats['total_days'] and attendance_stats['total_days'] > 0:
        attendance_percentage = round((attendance_stats['attended_days'] / attendance_stats['total_days']) * 100)
    else:
        attendance_percentage = 0
    
    # Clean up expired homework before showing list
    cleanup_expired_homework()
    
    # Calculate cutoff date to exclude expired homework
    today = get_ist_today()
    cutoff_date = (today - timedelta(days=1)).isoformat()
    
    # Get recent homework (last 10, excluding expired)
    cursor.execute('''
        SELECT h.*, b.name as batch_name
        FROM homework h
        LEFT JOIN batches b ON h.batch_id = b.id
        WHERE (h.batch_id = ? OR h.student_id = ?)
        AND h.user_id = (SELECT user_id FROM students WHERE id = ?)
        AND h.submission_date >= ?
        ORDER BY h.created_at DESC
        LIMIT 10
    ''', (student['batch_id'], student_id, student_id, cutoff_date))
    recent_homework = cursor.fetchall()
    
    # Get upcoming classes
    upcoming_classes = []
    if student['batch_id']:
        cursor.execute('SELECT * FROM batches WHERE id = ?', (student['batch_id'],))
        batch = cursor.fetchone()
        
        if batch and batch['start_time'] and batch['days']:
            # Parse days
            batch_days = batch['days'].split(',') if batch['days'] else []
            is_daily = 'daily' in batch_days or batch['days'] == 'daily'
            
            # Day name mapping
            day_map = {
                'mo': 'Monday', 'tu': 'Tuesday', 'we': 'Wednesday', 'th': 'Thursday',
                'fr': 'Friday', 'sa': 'Saturday', 'su': 'Sunday'
            }
            
            # Get next 5 upcoming classes
            now = get_ist_now()
            for i in range(14):  # Check next 14 days
                check_date = now.date() + timedelta(days=i)
                weekday_name = check_date.strftime('%A')
                weekday_abbr = {
                    'Monday': 'mo', 'Tuesday': 'tu', 'Wednesday': 'we', 'Thursday': 'th',
                    'Friday': 'fr', 'Saturday': 'sa', 'Sunday': 'su'
                }.get(weekday_name, '')
                
                # Check if batch runs on this day
                if is_daily or weekday_abbr in batch_days:
                    try:
                        start_time_obj = datetime.strptime(batch['start_time'], '%H:%M').time()
                        class_datetime = datetime.combine(check_date, start_time_obj)
                        
                        # Only show future classes
                        if class_datetime > now:
                            date_display = check_date.strftime('%B %d, %Y')
                            if i == 0:
                                date_display = 'Today'
                            elif i == 1:
                                date_display = 'Tomorrow'
                            else:
                                date_display = check_date.strftime('%A, %B %d')
                            
                            time_display = batch['start_time']
                            if batch['end_time']:
                                time_display += f" - {batch['end_time']}"
                            
                            upcoming_classes.append({
                                'batch_name': batch['name'],
                                'date_display': date_display,
                                'time_display': time_display,
                                'datetime': class_datetime
                            })
                            
                            if len(upcoming_classes) >= 5:
                                break
                    except:
                        pass
    
    # For students, we'll use localStorage to track their own onboarding
    # This allows each student to have their own tour experience
    # We don't need to pass onboarding_completed for students as it's handled client-side
    
    conn.close()
    
    return render_template('student/dashboard.html',
                         student=student,
                         today_attendance=today_attendance,
                         attendance_stats=attendance_stats,
                         attendance_percentage=attendance_percentage,
                         recent_homework=recent_homework,
                         upcoming_classes=upcoming_classes,
                         today=today)

@student_bp.route('/student/attendance')
@require_login
def attendance():
    """Student attendance view"""
    if session.get('role') != 'student':
        return redirect(url_for('dashboard.dashboard'))
    
    student_id = session.get('student_id')
    if not student_id:
        return redirect(url_for('auth.student_login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get student info
    cursor.execute('SELECT * FROM students WHERE id = ?', (student_id,))
    student = cursor.fetchone()
    
    if not student:
        conn.close()
        session.clear()
        return redirect(url_for('auth.student_login'))
    
    # Get attendance stats (last 30 days)
    thirty_days_ago = (get_ist_today() - timedelta(days=29)).isoformat()
    cursor.execute('''
        SELECT 
            COUNT(*) as total_days,
            SUM(CASE WHEN COALESCE(status, present, 0) IN (1, 2) THEN 1 ELSE 0 END) as attended_days,
            SUM(CASE WHEN COALESCE(status, present, 0) = 1 THEN 1 ELSE 0 END) as present_days,
            SUM(CASE WHEN COALESCE(status, present, 0) = 2 THEN 1 ELSE 0 END) as late_days,
            SUM(CASE WHEN COALESCE(status, present, 0) = 0 THEN 1 ELSE 0 END) as absent_days
        FROM attendance
        WHERE student_id = ? AND date >= ?
    ''', (student_id, thirty_days_ago))
    attendance_stats = cursor.fetchone()
    
    # Get current month dates (e.g., December 1-31) - IST
    today = get_ist_today()
    current_month = today.month
    current_year = today.year
    
    # Generate all dates for current month
    month_days = monthrange(current_year, current_month)[1]  # Number of days in month
    
    date_range = []
    for day in range(1, month_days + 1):
        d = date(current_year, current_month, day)
        date_range.append(d.isoformat())
    
    # Get first day of month to calculate which day of week it starts on
    first_day = date(current_year, current_month, 1)
    first_day_weekday = first_day.weekday()  # 0 = Monday, 6 = Sunday
    
    attendance_by_date = {}
    for date_str in date_range:
        cursor.execute('''
            SELECT COALESCE(status, present, -1) as status
            FROM attendance
            WHERE student_id = ? AND date = ?
        ''', (student_id, date_str))
        result = cursor.fetchone()
        if result:
            attendance_by_date[date_str] = result['status'] if result['status'] is not None else -1
        else:
            attendance_by_date[date_str] = -1
    
    conn.close()
    
    # Get month name
    month_names = ['January', 'February', 'March', 'April', 'May', 'June', 
                   'July', 'August', 'September', 'October', 'November', 'December']
    month_name = month_names[current_month - 1]
    
    return render_template('student/attendance.html',
                         student=student,
                         attendance_by_date=attendance_by_date,
                         date_range=date_range,
                         attendance_stats=attendance_stats,
                         current_month=current_month,
                         current_year=current_year,
                         month_name=month_name,
                         first_day_weekday=first_day_weekday,
                         today=today.isoformat())

@student_bp.route('/student/homework')
@require_login
def homework():
    """Student homework view"""
    if session.get('role') != 'student':
        return redirect(url_for('dashboard.dashboard'))
    
    student_id = session.get('student_id')
    if not student_id:
        return redirect(url_for('auth.student_login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get student info
    cursor.execute('SELECT * FROM students WHERE id = ?', (student_id,))
    student = cursor.fetchone()
    
    if not student:
        conn.close()
        session.clear()
        return redirect(url_for('auth.student_login'))
    
    # Clean up expired homework before showing list
    cleanup_expired_homework()
    
    # Calculate cutoff date to exclude expired homework
    today = get_ist_today()
    cutoff_date = (today - timedelta(days=1)).isoformat()
    
    # Get all homework assigned to this student (excluding expired)
    cursor.execute('''
        SELECT h.*, b.name as batch_name
        FROM homework h
        LEFT JOIN batches b ON h.batch_id = b.id
        WHERE (h.batch_id = ? OR h.student_id = ?)
        AND h.user_id = (SELECT user_id FROM students WHERE id = ?)
        AND h.submission_date >= ?
        ORDER BY h.created_at DESC
    ''', (student['batch_id'], student_id, student_id, cutoff_date))
    homework_list = cursor.fetchall()
    
    conn.close()
    
    return render_template('student/homework.html',
                         student=student,
                         homework_list=homework_list)

@student_bp.route('/api/student/homework/reminders', methods=['GET'])
@require_login
def homework_reminders_api():
    """API endpoint to get homework reminders for students"""
    if session.get('role') != 'student':
        return redirect(url_for('dashboard.dashboard'))
    
    student_id = session.get('student_id')
    if not student_id:
        return jsonify({'new_homework': [], 'due_soon': [], 'due_very_soon': []})
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get student's batch_id
    cursor.execute('SELECT batch_id, user_id FROM students WHERE id = ?', (student_id,))
    student = cursor.fetchone()
    
    if not student:
        conn.close()
        return jsonify({'new_homework': [], 'due_soon': [], 'due_very_soon': []})
    
    now = datetime.now()
    today = now.date()
    tomorrow = today + timedelta(days=1)
    # 30 minutes before midnight of due date (11:30 PM the day before)
    thirty_minutes_before_midnight = datetime.combine(today, datetime.max.time()) - timedelta(minutes=30)
    
    # Calculate cutoff date to exclude expired homework
    today_ist = get_ist_today()
    cutoff_date = (today_ist - timedelta(days=1)).isoformat()
    
    # Get all homework assigned to this student with batch timing (excluding expired)
    cursor.execute('''
        SELECT h.*, b.name as batch_name, b.start_time as batch_start_time
        FROM homework h
        LEFT JOIN batches b ON h.batch_id = b.id
        WHERE (h.batch_id = ? OR h.student_id = ?)
        AND h.user_id = ?
        AND h.submission_date IS NOT NULL
        AND h.submission_date >= ?
        ORDER BY h.created_at DESC
    ''', (student['batch_id'], student_id, student['user_id'], cutoff_date))
    all_homework = cursor.fetchall()
    
    new_homework = []
    due_soon = []  # Due in 1 day
    due_very_soon = []  # Due in 30 minutes
    
    for hw in all_homework:
        if not hw['submission_date']:
            continue
        
        try:
            submission_date = datetime.strptime(hw['submission_date'], '%Y-%m-%d').date()
            submission_datetime = datetime.combine(submission_date, datetime.min.time())
            
            # Check if homework was created in the last 5 minutes (new assignment)
            created_at = datetime.strptime(hw['created_at'], '%Y-%m-%d %H:%M:%S') if isinstance(hw['created_at'], str) else hw['created_at']
            if isinstance(created_at, str):
                created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
            
            time_since_created = (now - created_at).total_seconds()
            if time_since_created <= 300:  # 5 minutes
                new_homework.append({
                    'id': hw['id'],
                    'title': hw['title'],
                    'submission_date': hw['submission_date'],
                    'batch_name': hw['batch_name']
                })
            
            # Check if due tomorrow (submission_date is tomorrow)
            if submission_date == tomorrow:
                due_soon.append({
                    'id': hw['id'],
                    'title': hw['title'],
                    'submission_date': hw['submission_date'],
                    'batch_name': hw['batch_name']
                })
            
            # Check if due in 30 minutes before batch time on due date
            # Only if homework has a batch with start_time
            if hw['batch_start_time'] and (submission_date == today or submission_date == tomorrow):
                try:
                    # Parse batch start time
                    batch_start_time = datetime.strptime(hw['batch_start_time'], '%H:%M').time()
                    batch_datetime = datetime.combine(submission_date, batch_start_time)
                    
                    # Check if current time is within 25-35 minutes before batch time
                    time_diff = (batch_datetime - now).total_seconds()
                    if 25 * 60 <= time_diff <= 35 * 60:  # 25-35 minutes before batch
                        due_very_soon.append({
                            'id': hw['id'],
                            'title': hw['title'],
                            'submission_date': hw['submission_date'],
                            'batch_name': hw['batch_name'],
                            'batch_time': hw['batch_start_time']
                        })
                except:
                    pass
        except:
            pass
    
    conn.close()
    
    return jsonify({
        'new_homework': new_homework,
        'due_soon': due_soon,
        'due_very_soon': due_very_soon
    })

@student_bp.route('/api/student/attendance/notifications', methods=['GET'])
@require_login
def attendance_notifications_api():
    """API endpoint to check for new attendance notifications"""
    if session.get('role') != 'student':
        return jsonify({'notifications': [], 'should_poll': False})
    
    student_id = session.get('student_id')
    if not student_id:
        return jsonify({'notifications': [], 'should_poll': False})
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get student's batch info and last notification check time
    cursor.execute('''
        SELECT s.last_attendance_notification, s.batch_id, b.start_time, b.days
        FROM students s
        LEFT JOIN batches b ON s.batch_id = b.id
        WHERE s.id = ?
    ''', (student_id,))
    student = cursor.fetchone()
    
    if not student:
        conn.close()
        return jsonify({'notifications': [], 'should_poll': False})
    
    now = datetime.now()
    today = date.today()
    today_str = today.isoformat()
    should_poll = False
    
    # First, check if attendance already exists for today
    cursor.execute('''
        SELECT a.*
        FROM attendance a
        WHERE a.student_id = ? AND a.date = ?
        ORDER BY a.created_at DESC
        LIMIT 1
    ''', (student_id, today_str))
    existing_attendance = cursor.fetchone()
    
    # If attendance already exists and was already notified, don't poll
    if existing_attendance and student['last_attendance_notification']:
        try:
            last_notification_str = student['last_attendance_notification']
            if isinstance(last_notification_str, str):
                last_notification = datetime.strptime(last_notification_str, '%Y-%m-%d %H:%M:%S')
            else:
                last_notification = last_notification_str
            
            attendance_created_str = existing_attendance['created_at']
            if isinstance(attendance_created_str, str):
                attendance_created = datetime.strptime(attendance_created_str, '%Y-%m-%d %H:%M:%S')
            else:
                attendance_created = attendance_created_str
            
            # If attendance was created before last notification, it was already notified
            if attendance_created <= last_notification:
                conn.close()
                return jsonify({'notifications': [], 'should_poll': False, 'attendance_exists': True})
        except:
            pass
    
    # Check if we should poll based on batch timing
    if student['batch_id'] and student['start_time']:
        try:
            batch_start = datetime.strptime(student['start_time'], '%H:%M').time()
            batch_datetime = datetime.combine(today, batch_start)
            
            # Poll if current time is at or after batch start time
            if now >= batch_datetime:
                should_poll = True
        except:
            pass
    
    # If no batch timing, poll during school hours (8 AM - 10 PM)
    if not should_poll:
        current_hour = now.hour
        if 8 <= current_hour < 22:
            should_poll = True
    
    notifications = []
    
    # Only check for attendance if we should be polling
    if should_poll:
        # Check if there's a new attendance record for today
        cursor.execute('''
            SELECT a.*, s.name as student_name
            FROM attendance a
            INNER JOIN students s ON a.student_id = s.id
            WHERE a.student_id = ? AND a.date = ?
            ORDER BY a.created_at DESC
            LIMIT 1
        ''', (student_id, today_str))
        attendance = cursor.fetchone()
        
        if attendance:
            # Check if this attendance was marked after the last notification
            should_notify = False
            
            if student['last_attendance_notification']:
                try:
                    last_notification_str = student['last_attendance_notification']
                    if isinstance(last_notification_str, str):
                        last_notification = datetime.strptime(last_notification_str, '%Y-%m-%d %H:%M:%S')
                    else:
                        last_notification = last_notification_str
                    
                    attendance_created_str = attendance['created_at']
                    if isinstance(attendance_created_str, str):
                        attendance_created = datetime.strptime(attendance_created_str, '%Y-%m-%d %H:%M:%S')
                    else:
                        attendance_created = attendance_created_str
                    
                    if attendance_created > last_notification:
                        should_notify = True
                except:
                    should_notify = True
            else:
                # First time checking, show notification if attendance exists
                should_notify = True
            
            if should_notify:
                status_text = 'Present' if attendance['status'] == 1 else ('Late' if attendance['status'] == 2 else 'Absent')
                notifications.append({
                    'type': 'attendance_marked',
                    'message': f'Your attendance has been marked as {status_text} for today',
                    'date': today_str,
                    'status': attendance['status']
                })
    
    # Update last notification check time (only if we're not showing a notification)
    # If showing notification, we'll update it after the student sees it
    if not notifications:
        cursor.execute('''
            UPDATE students 
            SET last_attendance_notification = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (student_id,))
        conn.commit()
    
    conn.close()
    
    # Stop polling if:
    # 1. Attendance was found and notified
    # 2. Attendance exists and was already notified
    # 3. It's not batch time yet
    stop_polling = (len(notifications) > 0) or (existing_attendance and not should_poll) or not should_poll
    
    return jsonify({
        'notifications': notifications,
        'should_poll': should_poll and not stop_polling  # Stop polling if attendance found or not batch time
    })

@student_bp.route('/student/profile')
@require_login
def profile():
    """Student profile view"""
    if session.get('role') != 'student':
        return redirect(url_for('dashboard.dashboard'))
    
    student_id = session.get('student_id')
    if not student_id:
        return redirect(url_for('auth.student_login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get student info with batch details
    cursor.execute('''
        SELECT s.*, b.name as batch_name, b.description as batch_description
        FROM students s
        LEFT JOIN batches b ON s.batch_id = b.id
        WHERE s.id = ?
    ''', (student_id,))
    student = cursor.fetchone()
    
    if not student:
        conn.close()
        session.clear()
        return redirect(url_for('auth.student_login'))
    
    conn.close()
    
    return render_template('student/profile.html', student=student)

