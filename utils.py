"""Utility functions for the TuitionTrack application"""
from functools import wraps
from flask import session, redirect, url_for
from werkzeug.utils import secure_filename
from config import Config
from datetime import datetime, date, timezone, timedelta

# IST timezone (UTC+5:30)
IST = timezone(timedelta(hours=5, minutes=30))

def get_ist_now():
    """Get current datetime in IST timezone"""
    return datetime.now(IST)

def get_ist_today():
    """Get current date in IST timezone"""
    return get_ist_now().date()

def get_ist_datetime():
    """Get current datetime in IST (alias for get_ist_now)"""
    return get_ist_now()

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def require_login(f):
    """Decorator to require login and load user data"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import request
        if 'user_id' not in session:
            # Redirect based on intended route
            if request.endpoint and 'student' in request.endpoint:
                return redirect(url_for('auth.student_login'))
            return redirect(url_for('auth.welcome'))
        
        # Load tuition_name into session if not already there
        if 'tuition_name' not in session:
            from database import get_db_connection
            conn = get_db_connection()
            cursor = conn.cursor()
            
            if session.get('role') == 'tutor':
                cursor.execute('SELECT tuition_name FROM users WHERE id = ?', (session['user_id'],))
                user = cursor.fetchone()
                if user and user['tuition_name']:
                    session['tuition_name'] = user['tuition_name']
            elif session.get('role') == 'student':
                # Get tuition name from the tutor who owns this student
                student_id = session.get('student_id')
                if student_id:
                    cursor.execute('''
                        SELECT u.tuition_name 
                        FROM users u
                        INNER JOIN students s ON u.id = s.user_id
                        WHERE s.id = ?
                    ''', (student_id,))
                    result = cursor.fetchone()
                    if result and result['tuition_name']:
                        session['tuition_name'] = result['tuition_name']
            
            conn.close()
        
        return f(*args, **kwargs)
    return decorated_function

def require_role(*allowed_roles):
    """Decorator to require specific user role(s)"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('auth.login'))
            
            user_role = session.get('role', 'tutor')
            if user_role not in allowed_roles:
                return redirect(url_for('dashboard.dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_secure_filename(filename):
    """Get secure filename for uploads"""
    return secure_filename(filename)

def cleanup_expired_homework():
    """Delete homework that is past due date + 1 day and remove associated files"""
    from database import get_db_connection
    from config import Config
    import os
    from datetime import timedelta
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Calculate cutoff date: today - 1 day (so homework with due date < today gets deleted)
    # This means homework is deleted 1 day after the due date
    today = get_ist_today()
    cutoff_date = (today - timedelta(days=1)).isoformat()
    
    # Find all expired homework
    cursor.execute('''
        SELECT id, file_path, user_id 
        FROM homework 
        WHERE submission_date < ?
    ''', (cutoff_date,))
    expired_homework = cursor.fetchall()
    
    deleted_count = 0
    deleted_files = 0
    
    for hw in expired_homework:
        # Delete associated file if it exists
        if hw['file_path']:
            file_path = os.path.join(Config.UPLOAD_FOLDER, hw['file_path'])
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    deleted_files += 1
            except Exception as e:
                # Log error but continue with deletion
                print(f"Error deleting file {file_path}: {e}")
        
        # Delete homework record
        cursor.execute('DELETE FROM homework WHERE id = ?', (hw['id'],))
        deleted_count += 1
    
    if deleted_count > 0:
        conn.commit()
    
    conn.close()
    return deleted_count, deleted_files

