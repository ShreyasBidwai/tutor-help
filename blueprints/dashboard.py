"""Dashboard blueprint"""
from flask import Blueprint, render_template, session, jsonify
from datetime import date, datetime, timedelta
from database import get_db_connection
from utils import require_login

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='')

@dashboard_bp.route('/dashboard')
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
    
    # Get upcoming batches for today
    now = datetime.now()
    # Map weekday to day abbreviation used in database
    weekday_map = {
        'Monday': 'mo', 'Tuesday': 'tu', 'Wednesday': 'we', 'Thursday': 'th',
        'Friday': 'fr', 'Saturday': 'sa', 'Sunday': 'su'
    }
    today_weekday = weekday_map.get(now.strftime('%A'), '')
    
    # Get batches scheduled for today (only those with notifications enabled)
    # Check if batch runs today (either daily or includes today's weekday)
    cursor.execute('''
        SELECT b.*, COUNT(s.id) as student_count
        FROM batches b
        LEFT JOIN students s ON b.id = s.batch_id AND s.user_id = ?
        WHERE b.user_id = ?
        AND b.start_time IS NOT NULL
        AND b.start_time != ''
        AND COALESCE(b.notifications_enabled, 1) = 1
        AND (
            b.days = 'daily' 
            OR b.days LIKE '%daily%'
            OR (b.days IS NOT NULL AND b.days != '' AND b.days LIKE ?)
        )
        GROUP BY b.id
        ORDER BY b.start_time
    ''', (user_id, user_id, f'%{today_weekday}%'))
    
    all_today_batches = cursor.fetchall()
    
    # Filter and categorize batches
    upcoming_batches = []
    current_batches = []
    
    for batch in all_today_batches:
        if batch['start_time']:
            try:
                batch_time = datetime.strptime(batch['start_time'], '%H:%M').time()
                batch_datetime = datetime.combine(now.date(), batch_time)
                
                # Check if batch is in next 4 hours or currently happening
                time_diff = (batch_datetime - now).total_seconds() / 60  # minutes
                
                if -15 <= time_diff <= 240:  # 15 mins before to 4 hours ahead
                    batch_info = {
                        'id': batch['id'],
                        'name': batch['name'],
                        'start_time': batch['start_time'],
                        'end_time': batch['end_time'],
                        'student_count': batch['student_count'],
                        'minutes_until': int(time_diff),
                        'status': 'upcoming' if time_diff > 0 else 'current'
                    }
                    
                    if time_diff <= 0 and time_diff >= -15:
                        current_batches.append(batch_info)
                    elif time_diff > 0:
                        upcoming_batches.append(batch_info)
            except Exception as e:
                # Skip batches with invalid time format
                pass
    
    # Sort upcoming by time
    upcoming_batches.sort(key=lambda x: x['minutes_until'])
    current_batches.sort(key=lambda x: x['minutes_until'])
    
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
    
    return render_template('dashboard/dashboard.html', 
                         student_count=student_count,
                         batch_count=batch_count,
                         attendance_count=attendance_count,
                         attendance_percentage=attendance_percentage,
                         upcoming_batches=upcoming_batches,
                         current_batches=current_batches,
                         recent_homework=recent_homework,
                         batch_stats=batch_stats,
                         today=today)

@dashboard_bp.route('/api/batches/upcoming', methods=['GET'])
@require_login
def upcoming_batches_api():
    """API endpoint to get upcoming batches (for polling)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    user_id = session['user_id']
    now = datetime.now()
    # Map weekday to day abbreviation used in database
    weekday_map = {
        'Monday': 'mo', 'Tuesday': 'tu', 'Wednesday': 'we', 'Thursday': 'th',
        'Friday': 'fr', 'Saturday': 'sa', 'Sunday': 'su'
    }
    today_weekday = weekday_map.get(now.strftime('%A'), '')
    
    # Get batches scheduled for today (only those with notifications enabled)
    cursor.execute('''
        SELECT b.*, COUNT(s.id) as student_count
        FROM batches b
        LEFT JOIN students s ON b.id = s.batch_id AND s.user_id = ?
        WHERE b.user_id = ?
        AND b.start_time IS NOT NULL
        AND b.start_time != ''
        AND COALESCE(b.notifications_enabled, 1) = 1
        AND (
            b.days = 'daily' 
            OR b.days LIKE '%daily%'
            OR (b.days IS NOT NULL AND b.days != '' AND b.days LIKE ?)
        )
        GROUP BY b.id
        ORDER BY b.start_time
    ''', (user_id, user_id, f'%{today_weekday}%'))
    
    all_today_batches = cursor.fetchall()
    
    reminders = []
    current = []
    
    homework_reminders = []
    
    for batch in all_today_batches:
        if batch['start_time']:
            try:
                batch_time = datetime.strptime(batch['start_time'], '%H:%M').time()
                batch_datetime = datetime.combine(now.date(), batch_time)
                time_diff = (batch_datetime - now).total_seconds() / 60
                
                if -15 <= time_diff <= 240:
                    batch_info = {
                        'id': batch['id'],
                        'name': batch['name'],
                        'start_time': batch['start_time'],
                        'end_time': batch['end_time'],
                        'student_count': batch['student_count'],
                        'minutes_until': int(time_diff)
                    }
                    
                    # 15 minutes before (reminder window)
                    if 14 <= time_diff <= 16:
                        reminders.append(batch_info)
                    # Currently happening (within 15 mins of start)
                    elif time_diff <= 0 and time_diff >= -15:
                        current.append(batch_info)
                    
                    # Check for homework reminders (10 minutes after batch start)
                    # time_diff will be negative after batch starts, so -11 to -9 means 9-11 minutes after start
                    if -11 <= time_diff <= -9:
                        # Check if this batch has homework assigned
                        cursor.execute('''
                            SELECT id, title, submission_date
                            FROM homework
                            WHERE batch_id = ? AND user_id = ?
                            ORDER BY created_at DESC
                            LIMIT 5
                        ''', (batch['id'], user_id))
                        homework_list = cursor.fetchall()
                        
                        if homework_list:
                            homework_reminders.append({
                                'id': batch['id'],
                                'name': batch['name'],
                                'start_time': batch['start_time'],
                                'end_time': batch['end_time'],
                                'homework': [{'id': h['id'], 'title': h['title'], 'submission_date': h['submission_date']} for h in homework_list]
                            })
            except:
                pass
    
    conn.close()
    
    return jsonify({
        'reminders': reminders,
        'current': current,
        'homework_reminders': homework_reminders
    })

