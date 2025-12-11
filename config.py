"""Configuration settings for the TuitionTrack application"""
import os
import secrets

# Try to load dotenv if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, use environment variables directly

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(16)
    DATABASE = os.environ.get('DATABASE', 'tutor_app.db')
    
    # Upload configuration
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    # User roles (for future student/enterprise login)
    ROLE_TUTOR = 'tutor'
    ROLE_STUDENT = 'student'
    ROLE_ENTERPRISE = 'enterprise'
    
    # Production settings
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 5000))
    
    # Timezone settings - Use IST (Indian Standard Time)
    TIMEZONE = 'Asia/Kolkata'  # IST timezone
    
    # Push Notification Configuration (VAPID)
    VAPID_PUBLIC_KEY = os.environ.get('VAPID_PUBLIC_KEY', 'BCrDZAbfKeme-jufCd1hg2TJYMnyIHDn-0HmY0e5oiQhHFeNLvLhcYUAPC38YZethfRoHiex1CN20HEOOGs4tZ8')
    VAPID_PRIVATE_KEY = os.environ.get('VAPID_PRIVATE_KEY', 'MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgweP4mxrIzmwF3_GW-gkWYxr4_psgmn9_wjh6yITAGoyhRANCAAQqw2QG3ynpnvo7nwndYYNkyWDJ8iBw5_tB5mNHuaIkIRxXjS7y4XGFADwt_GGXrYX0aB4nsdQjdtBxDjhrOLWf')
    VAPID_CLAIM_EMAIL = os.environ.get('VAPID_CLAIM_EMAIL', 'tuitiontrack@example.com')

