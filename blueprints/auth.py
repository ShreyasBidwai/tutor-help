"""Authentication blueprint for tutor, student, and enterprise logins"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db_connection, execute_with_retry
from config import Config
from utils import require_login
import re
import sqlite3

auth_bp = Blueprint('auth', __name__, url_prefix='')

def validate_name(name):
    """Validate name: only letters and spaces, no numbers or special characters"""
    if not name or not name.strip():
        return False
    # Allow only letters (including accented characters) and spaces
    name_pattern = re.compile(r'^[a-zA-Z\s\u00C0-\u017F\u0100-\u017F\u0180-\u024F\u1E00-\u1EFF]+$')
    return bool(name_pattern.match(name.strip()))

@auth_bp.route('/')
def index():
    """Welcome page"""
    if 'user_id' in session:
        return redirect(url_for('dashboard.dashboard'))
    return redirect(url_for('auth.welcome'))

@auth_bp.route('/welcome')
def welcome():
    """Welcome page with tutor/student/enterprise selection"""
    if 'user_id' in session:
        return redirect(url_for('dashboard.dashboard'))
    return render_template('auth/welcome.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """OTP-based login for tutors"""
    if 'user_id' in session:
        return redirect(url_for('dashboard.dashboard'))
    
    if request.method == 'POST':
        action = request.form.get('action', '').strip().lower()  # Explicitly get action
        mobile = request.form.get('mobile', '').strip()
        
        # Validate mobile number
        if not mobile or len(mobile) != 10 or not mobile.isdigit():
            return render_template('auth/login.html', error='Please enter a valid 10-digit mobile number', active_tab=action or 'login')
        
        # Validate action - must be either 'login' or 'signup'
        if action not in ['login', 'signup']:
            return render_template('auth/login.html', error='Invalid action. Please use the login or signup form.', active_tab='login')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        
        # Check if user exists
        cursor.execute('SELECT id, tuition_name, role, password_hash FROM users WHERE mobile = ?', (mobile,))
        user = cursor.fetchone()
        
        if action == 'login':
            # Login flow - user MUST exist
            if not user:
                conn.close()
                return render_template('auth/login.html', error='Mobile number not registered. Please sign up first.', active_tab='login')
            
            # Additional validation: ensure user has completed signup (has tuition_name)
            # This prevents login if signup was incomplete
            user_id = user['id']
            tuition_name = user['tuition_name']
            role = user['role'] or Config.ROLE_TUTOR
            
            # If tuition_name is missing, redirect to signup to complete profile
            if not tuition_name:
                conn.close()
                session['signup_mobile'] = mobile
                flash('Please complete your signup by providing your tuition name.', 'error')
                return redirect(url_for('auth.signup'))
            
            # Verify password
            password = request.form.get('password', '').strip()
            if not password:
                conn.close()
                return render_template('auth/login.html', error='Please enter your password', active_tab='login')

            if not user['password_hash'] or not check_password_hash(user['password_hash'], password):
                conn.close()
                return render_template('auth/login.html', error='Invalid mobile number or password.', active_tab='login')
            
            # Login successful
            # Force session regeneration to prevent fixation
            session.clear()
            session['user_id'] = user_id
            session['mobile'] = mobile
            session['role'] = role
            session['tuition_name'] = tuition_name
            
            conn.close()
            return redirect(url_for('dashboard.dashboard'))
        
        else:  # action == 'signup'
            # Signup flow - user must NOT exist
            if user:
                conn.close()
                return render_template('auth/login.html', error='Mobile number already registered. Please login instead.', active_tab='signup')
            
            # For signup, redirect to signup page to get tuition name
            session['signup_mobile'] = mobile
            conn.close()
            return redirect(url_for('auth.signup'))
    
    return render_template('auth/login.html', active_tab='login')

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """Signup page - collect tuition name"""
    if 'user_id' in session:
        return redirect(url_for('dashboard.dashboard'))
    
    if 'signup_mobile' not in session:
        return redirect(url_for('auth.login'))
    
    mobile = session['signup_mobile']
    
    if request.method == 'POST':
        tuition_name = request.form.get('tuition_name', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        if not password or len(password) < 6:
            return render_template('auth/signup.html', mobile=mobile, error='Password must be at least 6 characters long')
            
        if password != confirm_password:
             return render_template('auth/signup.html', mobile=mobile, error='Passwords do not match')
        
        if not tuition_name:
            return render_template('auth/signup.html', mobile=mobile, error='Please enter your tuition name')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Check if mobile already exists (race condition check)
            cursor.execute('SELECT id FROM users WHERE mobile = ?', (mobile,))
            existing_user = cursor.fetchone()
            
            if existing_user:
                conn.close()
                session.pop('signup_mobile', None)
                return render_template('auth/login.html', error='Mobile number already registered. Please login instead.', active_tab='login')
            
            # Create new user with tutor role - use retry logic for write operations
            insert_cursor = execute_with_retry(conn, 
                'INSERT INTO users (mobile, tuition_name, role, password_hash) VALUES (?, ?, ?, ?)', 
                (mobile, tuition_name, Config.ROLE_TUTOR, generate_password_hash(password)))
            conn.commit()
            user_id = insert_cursor.lastrowid
            conn.close()
        except sqlite3.OperationalError as e:
            conn.rollback()
            conn.close()
            if "database is locked" in str(e).lower():
                return render_template('auth/signup.html', mobile=mobile, error='Database is temporarily busy. Please try again in a moment.')
            raise
        except Exception as e:
            conn.rollback()
            conn.close()
            raise
        
        # Clear signup session and set login session
        session.pop('signup_mobile', None)
        session['user_id'] = user_id
        session['mobile'] = mobile
        session['tuition_name'] = tuition_name
        session['role'] = Config.ROLE_TUTOR
        
        return redirect(url_for('dashboard.dashboard'))
    
    return render_template('auth/signup.html', mobile=mobile)

@auth_bp.route('/student/login', methods=['GET', 'POST'])
def student_login():
    """OTP-based login for students"""
    if 'user_id' in session and session.get('role') == 'student':
        return redirect(url_for('student.dashboard'))
    
    if request.method == 'POST':
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '').strip()
        
        if not phone or len(phone) != 10 or not phone.isdigit():
            return render_template('auth/student_login.html', error='Please enter a valid 10-digit phone number')
            
        if not password:
            return render_template('auth/student_login.html', error='Please enter your password')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if student exists
        cursor.execute('''
            SELECT s.id, s.name, s.phone, s.batch_id, s.password_hash, b.name as batch_name
            FROM students s
            LEFT JOIN batches b ON s.batch_id = b.id
            WHERE s.phone = ?
            LIMIT 1
        ''', (phone,))
        student = cursor.fetchone()
        
        if not student:
            conn.close()
            return render_template('auth/student_login.html', error='Phone number not found. Please contact your tutor.')
        
        # Verify password
        if not student['password_hash']:
            conn.close()
            return render_template('auth/student_login.html', error='No password set. Please contact your tutor.')
            
        if not check_password_hash(student['password_hash'], password):
            conn.close()
            return render_template('auth/student_login.html', error='Invalid phone number or password.')
        
        # Login success
        session['user_id'] = student['id']
        session['mobile'] = phone
        session['role'] = 'student'
        session['student_name'] = student['name']
        session['student_id'] = student['id']
        session['batch_id'] = student['batch_id']
        if student['batch_name']:
            session['batch_name'] = student['batch_name']
        
        conn.close()
        return redirect(url_for('student.dashboard'))
    
    return render_template('auth/student_login.html')

@auth_bp.route('/enterprise/login')
def enterprise_login():
    """Enterprise login - Coming Soon"""
    return render_template('auth/enterprise_login.html')

@auth_bp.route('/profile', methods=['GET', 'POST'])
@require_login
def profile():
    """View and edit tutor profile"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        tutor_name = request.form.get('tutor_name', '').strip()
        tuition_name = request.form.get('tuition_name', '').strip()
        address = request.form.get('address', '').strip()
        
        # Validate tutor_name if provided
        if tutor_name and not validate_name(tutor_name):
            flash('Tutor name can only contain letters and spaces. No numbers or special characters allowed.', 'error')
            cursor.execute('SELECT mobile, tutor_name, tuition_name, address FROM users WHERE id = ?', (session['user_id'],))
            user = cursor.fetchone()
            conn.close()
            return render_template('auth/profile.html', user=user)
        
        if tuition_name:
            cursor.execute('''
                UPDATE users 
                SET tutor_name = ?, tuition_name = ?, address = ?
                WHERE id = ?
            ''', (tutor_name, tuition_name, address, session['user_id']))
            conn.commit()
            
            # Update session
            session['tuition_name'] = tuition_name
            flash('Profile updated successfully!', 'success')
        else:
            flash('Tuition name is required', 'error')
    
    # Get current user data
    cursor.execute('SELECT mobile, tutor_name, tuition_name, address FROM users WHERE id = ?', (session['user_id'],))
    user = cursor.fetchone()
    conn.close()
    
    return render_template('auth/profile.html', user=user)

@auth_bp.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    return redirect(url_for('auth.welcome'))

@auth_bp.route('/api/push/subscribe', methods=['POST'])
@require_login
def push_subscribe():
    """Subscribe user to push notifications using Firebase FCM token"""
    try:
        data = request.get_json()
        
        if not data or 'token' not in data:
            return jsonify({'error': 'Invalid subscription data'}), 400
        
        token = data['token']
        user_agent = request.headers.get('User-Agent', '')
        
        if not token:
            return jsonify({'error': 'Missing FCM token'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if subscription already exists
        cursor.execute('SELECT id FROM push_subscriptions WHERE endpoint = ?', (token,))
        existing = cursor.fetchone()
        
        # We store the token in the 'endpoint' column for backward compatibility with table schema
        # The p256dh and auth columns are no longer needed for FCM but kept for schema compatibility
        
        if existing:
            # Update existing subscription
            cursor.execute('''
                UPDATE push_subscriptions
                SET user_id = ?, user_agent = ?, created_at = CURRENT_TIMESTAMP
                WHERE endpoint = ?
            ''', (session['user_id'], user_agent, token))
        else:
            # Insert new subscription
            # Providing dummy values for p256dh and auth to satisfy NOT NULL constraints if migration hasn't run
            cursor.execute('''
                INSERT INTO push_subscriptions (user_id, endpoint, p256dh, auth, user_agent)
                VALUES (?, ?, ?, ?, ?)
            ''', (session['user_id'], token, 'fcm', 'fcm', user_agent))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Subscribed to push notifications'}), 200
        
    except Exception as e:
        import logging
        logging.error(f"Error subscribing to push: {e}")
        return jsonify({'error': 'Failed to subscribe'}), 500

@auth_bp.route('/api/push/unsubscribe', methods=['POST'])
@require_login
def push_unsubscribe():
    """Unsubscribe user from push notifications"""
    try:
        data = request.get_json()
        
        if not data or 'token' not in data:
            return jsonify({'error': 'Invalid request'}), 400
        
        token = data['token']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Delete subscription
        cursor.execute('''
            DELETE FROM push_subscriptions
            WHERE endpoint = ? AND user_id = ?
        ''', (token, session['user_id']))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Unsubscribed from push notifications'}), 200
        
    except Exception as e:
        import logging
        logging.error(f"Error unsubscribing from push: {e}")
        return jsonify({'error': 'Failed to unsubscribe'}), 500

