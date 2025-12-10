"""Utility functions for the Tutor Help application"""
from functools import wraps
from flask import session, redirect, url_for
from werkzeug.utils import secure_filename
from config import Config

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

