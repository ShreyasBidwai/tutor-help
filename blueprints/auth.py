"""Authentication blueprint for tutor, student, and enterprise logins"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database import get_db_connection
from config import Config
from utils import require_login
import re

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
        cursor.execute('SELECT id, tuition_name, role FROM users WHERE mobile = ?', (mobile,))
        user = cursor.fetchone()
        
        if action == 'login':
            # Login flow - user MUST exist
            if not user:
                conn.close()
                flash('Mobile number not found. Please sign up first.', 'error')
                return render_template('auth/login.html', error='Mobile number not found. Please sign up first.', active_tab='login')
            
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
            
            # Simulate OTP verification (auto-login)
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
                flash('Mobile number already registered. Please login instead.', 'error')
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
        
        if not tuition_name:
            return render_template('auth/signup.html', mobile=mobile, error='Please enter your tuition name')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if mobile already exists (race condition check)
        cursor.execute('SELECT id FROM users WHERE mobile = ?', (mobile,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            conn.close()
            session.pop('signup_mobile', None)
            return render_template('auth/login.html', error='Mobile number already registered. Please login instead.', active_tab='login')
        
        # Create new user with tutor role
        cursor.execute('INSERT INTO users (mobile, tuition_name, role) VALUES (?, ?, ?)', 
                      (mobile, tuition_name, Config.ROLE_TUTOR))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        
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
        
        if not phone or len(phone) != 10 or not phone.isdigit():
            return render_template('auth/student_login.html', error='Please enter a valid 10-digit phone number')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if student exists
        cursor.execute('''
            SELECT s.id, s.name, s.phone, s.batch_id, b.name as batch_name
            FROM students s
            LEFT JOIN batches b ON s.batch_id = b.id
            WHERE s.phone = ?
            LIMIT 1
        ''', (phone,))
        student = cursor.fetchone()
        
        if not student:
            conn.close()
            return render_template('auth/student_login.html', error='Phone number not found. Please contact your tutor.')
        
        # Simulate OTP verification (auto-login)
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

