"""Authentication blueprint for tutor, student, and enterprise logins"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database import get_db_connection
from config import Config
from utils import require_login

auth_bp = Blueprint('auth', __name__, url_prefix='')

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
        action = request.form.get('action', 'login')  # 'login' or 'signup'
        mobile = request.form.get('mobile', '').strip()
        
        if not mobile or len(mobile) != 10 or not mobile.isdigit():
            return render_template('auth/login.html', error='Please enter a valid 10-digit mobile number', active_tab=action)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute('SELECT id, tuition_name, role FROM users WHERE mobile = ?', (mobile,))
        user = cursor.fetchone()
        
        if action == 'login':
            # Login flow
            if not user:
                conn.close()
                return render_template('auth/login.html', error='Mobile number not found. Please sign up first.', active_tab='login')
            
            user_id = user['id']
            tuition_name = user['tuition_name']
            role = user['role'] or Config.ROLE_TUTOR
            
            # Simulate OTP verification (auto-login)
            session['user_id'] = user_id
            session['mobile'] = mobile
            session['role'] = role
            if tuition_name:
                session['tuition_name'] = tuition_name
            
            conn.close()
            return redirect(url_for('dashboard.dashboard'))
        
        else:  # signup
            # Signup flow - check if already exists
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

@auth_bp.route('/student/login')
def student_login():
    """Student login - Coming Soon"""
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

