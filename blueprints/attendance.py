"""Attendance management blueprint"""
from flask import Blueprint, render_template, request, session, jsonify, flash
from datetime import date, datetime, timedelta
from database import get_db_connection
from utils import require_login, get_ist_now, get_ist_today, cleanup_old_attendance
from utils.push_notifications import send_notification_to_user

attendance_bp = Blueprint('attendance', __name__, url_prefix='')

@attendance_bp.route('/attendance')
@require_login
def attendance():
    """Attendance tracker page"""
    # Clean up old attendance records (keep only current month)
    cleanup_old_attendance()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get selected date and batch filter from query parameters
    date_param = request.args.get('date', '').strip()
    # Handle empty date - default to today (IST)
    if not date_param:
        selected_date = get_ist_today().isoformat()
    else:
        try:
            # Validate date format
            selected_date_obj_test = date.fromisoformat(date_param)
            selected_date = date_param
        except (ValueError, AttributeError):
            # Invalid date format, default to today (IST)
            selected_date = get_ist_today().isoformat()
    
    batch_filter = request.args.get('batch', type=int)
    
    # Get all batches for filter dropdown (needed for default selection)
    conn_temp = get_db_connection()
    cursor_temp = conn_temp.cursor()
    cursor_temp.execute('SELECT * FROM batches WHERE user_id = ? ORDER BY name', (session['user_id'],))
    all_batches = cursor_temp.fetchall()
    conn_temp.close()
    
    # Set default batch to first batch if no batch is selected
    if not batch_filter and all_batches:
        batch_filter = all_batches[0]['id']
        # Redirect to include batch in URL so it's selected in dropdown
        from flask import redirect, url_for
        return redirect(url_for('attendance.attendance', date=selected_date, batch=batch_filter))
    
    # Build query for students with attendance status and batch timing
    query = '''
        SELECT s.*, b.name as batch_name, b.start_time as batch_start_time,
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
    
    # Logic: Allow marking attendance for today and yesterday only (IST)
    attendance_already_saved = False
    now = get_ist_now()
    today = get_ist_today()
    yesterday = today - timedelta(days=1)
    
    # Parse selected date with error handling
    try:
        selected_date_obj = date.fromisoformat(selected_date)
    except (ValueError, AttributeError):
        # If date parsing fails, default to today (IST)
        selected_date = get_ist_today().isoformat()
        selected_date_obj = today
    
    is_today = selected_date == today.isoformat()
    is_yesterday = selected_date == yesterday.isoformat()
    is_future = selected_date_obj > today
    is_past_before_yesterday = selected_date_obj < yesterday
    
    # Check if attendance already exists per batch (not globally)
    # We'll check this per batch later, not globally
    attendance_already_saved = False  # This is now batch-specific, checked per batch
    
    # Group students by batch first
    students_by_batch = {}
    batch_can_mark = {}  # Track which batches can have attendance marked
    batch_attendance_saved = {}  # Track which batches already have attendance saved (per batch)
    
    # First pass: Group students by batch
    if not is_future:
        for student in students:
            batch_name = student['batch_name'] or 'No Batch'
            if batch_name not in students_by_batch:
                students_by_batch[batch_name] = []
            students_by_batch[batch_name].append(student)
    
    # Second pass: Check attendance status and timing per batch
    if not is_future:
        for batch_name, batch_students in students_by_batch.items():
            # Allow marking for today and yesterday
            can_mark_this_batch = is_today or is_yesterday
            
            # Check if attendance is already saved for THIS batch only (not globally)
            # Get ALL students in this batch from database (not just current view)
            # Find batch_id from batch name
            cursor.execute('''
                SELECT id FROM batches 
                WHERE name = ? AND user_id = ?
            ''', (batch_name, session['user_id']))
            batch_row = cursor.fetchone()
            
            if batch_row:
                batch_id = batch_row['id']
                # Get ALL students in this batch
                cursor.execute('''
                    SELECT id FROM students 
                    WHERE batch_id = ? AND user_id = ?
                ''', (batch_id, session['user_id']))
                all_batch_students_db = cursor.fetchall()
                all_batch_student_ids = [s['id'] for s in all_batch_students_db]
                
                if all_batch_student_ids and (is_today or is_yesterday):
                    placeholders = ','.join(['?' for _ in all_batch_student_ids])
                    # Count how many students in this batch have attendance marked for this date
                    cursor.execute(f'''
                        SELECT COUNT(DISTINCT student_id) as count
                        FROM attendance
                        WHERE student_id IN ({placeholders}) AND date = ?
                    ''', all_batch_student_ids + [selected_date])
                    result = cursor.fetchone()
                    # Check if ALL students in this batch have attendance marked
                    total_students_in_batch = len(all_batch_student_ids)
                    if result and result['count'] > 0:
                        # Only mark as "saved" if ALL students have attendance (prevents re-marking)
                        if result['count'] >= total_students_in_batch:
                            batch_attendance_saved[batch_name] = True
                        else:
                            batch_attendance_saved[batch_name] = False  # Partial attendance, can still mark
                    else:
                        batch_attendance_saved[batch_name] = False
                else:
                    batch_attendance_saved[batch_name] = False
            else:
                # Batch not found or "No Batch"
                batch_attendance_saved[batch_name] = False
            
            # If today, check if batch time has started
            if is_today and batch_students:
                # Get batch start time from first student in batch
                first_student = batch_students[0]
                batch_start_time = first_student['batch_start_time'] if 'batch_start_time' in first_student.keys() else None
                if batch_start_time:
                    try:
                        from utils import IST
                        batch_start = datetime.strptime(batch_start_time, '%H:%M').time()
                        batch_datetime = datetime.combine(today, batch_start).replace(tzinfo=IST)
                        # Only allow marking if batch has started
                        if now < batch_datetime:
                            can_mark_this_batch = False
                    except:
                        pass
            # For yesterday, allow marking without time restrictions
            elif is_yesterday:
                can_mark_this_batch = True
            
            # Can't mark if attendance is already fully saved for this batch
            if batch_attendance_saved.get(batch_name, False):
                can_mark_this_batch = False
            
            batch_can_mark[batch_name] = can_mark_this_batch
    
    # Use batches we already fetched
    batches = all_batches
    
    conn.close()
    
    # Global can_mark_attendance: true if it's today or yesterday and at least one batch can be marked
    can_mark_attendance = (is_today or is_yesterday) and (any(batch_can_mark.values()) if batch_can_mark else False)
    
    return render_template('attendance/attendance.html', 
                         students_by_batch=students_by_batch,
                         students=students,  # Keep for backward compatibility
                         selected_date=selected_date,
                         today=date.today().isoformat(),
                         yesterday=yesterday.isoformat(),
                         batches=batches,
                         batch_filter=batch_filter,
                         can_mark_attendance=can_mark_attendance,
                         batch_can_mark=batch_can_mark,  # Per-batch marking permission
                         batch_attendance_saved=batch_attendance_saved,  # Per-batch attendance status
                         attendance_already_saved=attendance_already_saved,  # Keep for backward compatibility
                         is_today=is_today,
                         is_yesterday=is_yesterday,
                         is_future=is_future,
                         is_past_before_yesterday=is_past_before_yesterday)

@attendance_bp.route('/api/attendance/save', methods=['POST'])
@require_login
def save_attendance():
    """Save attendance for multiple students at once"""
    data = request.get_json()
    attendance_data = data.get('attendance', [])  # List of {student_id, status, date}
    date_str = data.get('date', get_ist_today().isoformat())
    
    if not attendance_data:
        return jsonify({'success': False, 'error': 'No attendance data provided'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    now = get_ist_now()
    today = get_ist_today()
    
    # Only allow saving attendance for today or yesterday
    yesterday = today - timedelta(days=1)
    if date_str != today.isoformat() and date_str != yesterday.isoformat():
        conn.close()
        return jsonify({'success': False, 'error': 'Attendance can only be marked for today or yesterday'}), 400
    
    # Validate and save attendance
    saved_students = []
    for item in attendance_data:
        student_id = item.get('student_id')
        status = item.get('status', 0)
        
        # Validate status
        if status not in [0, 1, 2]:
            continue
        
        # Check if student belongs to user
        cursor.execute('SELECT id, batch_id FROM students WHERE id = ? AND user_id = ?', (student_id, session['user_id']))
        student = cursor.fetchone()
        if not student:
            continue
        
        # Check if attendance already exists for this student and date
        cursor.execute('SELECT id FROM attendance WHERE student_id = ? AND date = ?', (student_id, date_str))
        existing_attendance = cursor.fetchone()
        if existing_attendance:
            # Attendance already saved, skip (locked)
            continue
        
        # For today's attendance, check if batch time has started
        if date_str == today.isoformat() and student['batch_id']:
            cursor.execute('SELECT start_time FROM batches WHERE id = ?', (student['batch_id'],))
            batch = cursor.fetchone()
            if batch and batch['start_time']:
                try:
                    batch_start = datetime.strptime(batch['start_time'], '%H:%M').time()
                    batch_datetime = datetime.combine(today, batch_start)
                    if now < batch_datetime:
                        continue  # Skip if batch hasn't started yet
                except:
                    pass
        
        # Insert attendance (only if not already saved)
        cursor.execute('''
            INSERT INTO attendance (student_id, date, status, user_id)
            VALUES (?, ?, ?, ?)
        ''', (student_id, date_str, status, session['user_id']))
        
        saved_students.append(student_id)
    
    conn.commit()
    
    # Notify students about attendance being marked
    # Update last_attendance_notification timestamp for each student
    if saved_students:
        placeholders = ','.join(['?' for _ in saved_students])
        cursor.execute(f'''
            UPDATE students 
            SET last_attendance_notification = CURRENT_TIMESTAMP
            WHERE id IN ({placeholders})
        ''', saved_students)
        conn.commit()
        
        # Send push notifications to students
        status_text_map = {0: 'Absent', 1: 'Present', 2: 'Late'}
        for item in attendance_data:
            student_id = item.get('student_id')
            status = item.get('status', 0)
            
            if student_id in saved_students:
                status_text = status_text_map.get(status, 'Unknown')
                title = 'Attendance Marked!'
                body = f'Your attendance has been marked as {status_text} for {date_str}'
                url = '/student/attendance'
                
                # Send push notification
                send_notification_to_user(
                    student_id,
                    title,
                    body,
                    url=url,
                    notification_type='attendance'
                )
    
    conn.close()
    
    if len(saved_students) > 0:
        return jsonify({
            'success': True, 
            'saved_count': len(saved_students),
            'message': f'Attendance saved for {len(saved_students)} student(s)'
        })
    else:
        return jsonify({
            'success': False,
            'error': 'No attendance was saved. Attendance may already be marked or batch time has not started.'
        }), 400

