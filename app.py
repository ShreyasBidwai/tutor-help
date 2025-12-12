"""Main Flask application - TuitionTrack PWA"""
from flask import Flask, jsonify
from config import Config
from database import init_db, migrate_db, add_indexes
from datetime import datetime, date
import os
import logging

# Set timezone to IST (Indian Standard Time)
os.environ['TZ'] = 'Asia/Kolkata'
try:
    import time
    time.tzset()  # Unix/Linux only
except AttributeError:
    # Windows doesn't have tzset, but we'll use timezone-aware datetime instead
    pass

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Production session security (for HTTPS)
# These settings ensure secure cookies when deployed with HTTPS
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access to cookies
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 hours

# Configure logging
if not app.debug:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s %(message)s'
    )

# Create uploads directory if it doesn't exist
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.join(Config.UPLOAD_FOLDER, 'homework'), exist_ok=True)

# Register blueprints
from blueprints.auth import auth_bp
from blueprints.dashboard import dashboard_bp
from blueprints.students import students_bp
from blueprints.batches import batches_bp
from blueprints.attendance import attendance_bp
from blueprints.homework import homework_bp
from blueprints.reports import reports_bp
from blueprints.payments import payments_bp
from blueprints.student import student_bp
from blueprints.export import export_bp
from blueprints.help_bot import help_bot_bp

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(students_bp)
app.register_blueprint(batches_bp)
app.register_blueprint(attendance_bp)
app.register_blueprint(homework_bp)
app.register_blueprint(reports_bp)
app.register_blueprint(payments_bp)
app.register_blueprint(student_bp)
app.register_blueprint(export_bp)
app.register_blueprint(help_bot_bp)

# Make VAPID_PUBLIC_KEY available to all templates
@app.context_processor
def inject_config():
    return dict(config=Config)

# Custom Jinja2 filter for DD/MM/YYYY date format
@app.template_filter('ddmmyyyy')
def ddmmyyyy_filter(value):
    """Format date as DD/MM/YYYY"""
    if not value:
        return ''
    
    try:
        # Handle string dates (YYYY-MM-DD format)
        if isinstance(value, str):
            if len(value) == 10 and '-' in value:
                # Parse YYYY-MM-DD format
                date_obj = datetime.strptime(value, '%Y-%m-%d').date()
            else:
                return value
        elif isinstance(value, date):
            date_obj = value
        elif isinstance(value, datetime):
            date_obj = value.date()
        else:
            return str(value)
        
        # Format as DD/MM/YYYY
        return date_obj.strftime('%d/%m/%Y')
    except (ValueError, AttributeError, TypeError):
        return str(value)

# Initialize database on startup
if not os.path.exists(Config.DATABASE):
    init_db()
    add_indexes()
else:
    migrate_db()
    add_indexes()

# Serve manifest.json at root for TWA compatibility
@app.route('/manifest.json')
def manifest():
    """Serve manifest.json for PWA/TWA"""
    from flask import send_from_directory
    return send_from_directory(
        os.path.join(app.root_path, 'static'), 
        'manifest.json', 
        mimetype='application/manifest+json'
    )

# Serve assetlinks.json for Android TWA verification
@app.route('/.well-known/assetlinks.json')
def assetlinks():
    """Serve assetlinks.json for Android TWA verification"""
    from flask import send_from_directory
    return send_from_directory(
        os.path.join(app.root_path, 'static', '.well-known'), 
        'assetlinks.json', 
        mimetype='application/json'
    )

# Health check endpoint for monitoring
@app.route('/health')
def health():
    """Health check endpoint for production monitoring"""
    return jsonify({
        'status': 'healthy',
        'service': 'TuitionTrack',
        'version': '1.0.0'
    }), 200

# Error handlers
@app.errorhandler(404)
def not_found(error):
    from flask import render_template
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    from flask import render_template
    import logging
    logging.error(f'Server Error: {error}', exc_info=True)
    return render_template('errors/500.html'), 500

if __name__ == '__main__':
    app.run(
        debug=Config.DEBUG,
        host=Config.HOST,
        port=Config.PORT
    )
