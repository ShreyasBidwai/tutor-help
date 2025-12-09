"""Configuration settings for the Tutor Help application"""
import os
import secrets

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(16)
    DATABASE = 'tutor_app.db'
    
    # Upload configuration
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    # User roles (for future student/enterprise login)
    ROLE_TUTOR = 'tutor'
    ROLE_STUDENT = 'student'
    ROLE_ENTERPRISE = 'enterprise'

