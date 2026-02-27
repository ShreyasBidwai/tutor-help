"""Main Flask application - TuitionTrack PWA"""
from flask import Flask, jsonify, request
from config import Config
from database import init_db, migrate_db, add_indexes
from datetime import datetime, date
import os
import logging
import firebase_admin
from firebase_admin import credentials

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

# Prevent caching of dynamic pages only — static assets (images, JS, CSS) should be cached
@app.after_request
def add_header(response):
    # Skip cache control for static files so that images, JS,
    # and CSS are cached by the browser (avoids logo / asset flicker)
    if request.path.startswith('/static/'):
        # Cache static assets for 1 hour; use ETag for revalidation
        response.headers['Cache-Control'] = 'public, max-age=3600, stale-while-revalidate=60'
        response.headers.pop('Pragma', None)
        response.headers.pop('Expires', None)
        return response

    # Dynamic pages: prevent caching so session changes are always fresh
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# Initialize Firebase Admin SDK
try:
    service_account_path = os.environ.get('FIREBASE_SERVICE_ACCOUNT_KEY', 'firebase-service-account.json')
    cred = credentials.Certificate(service_account_path)
    firebase_admin.initialize_app(cred)
    print("Firebase Admin SDK initialized successfully")
except Exception as e:
    print(f"Error initializing Firebase Admin SDK: {e}")

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
from blueprints.webhooks import webhooks_bp


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
app.register_blueprint(webhooks_bp)


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

# Test notification endpoint
@app.route('/test-notification')
def test_notification():
    """Send a test notification to the current user"""
    from flask import session, jsonify
    from jobs import send_fcm_notification
    
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
        
    try:
        send_fcm_notification(
            session['user_id'],
            "Test Notification",
            "This is a test notification from TuitionTrack"
        )
        return jsonify({'success': True, 'message': 'Test notification sent'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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

# Serve firebase-messaging-sw.js at root for Firebase Cloud Messaging
@app.route('/firebase-messaging-sw.js')
def firebase_messaging_sw():
    """Serve firebase-messaging-sw.js with Firebase config injected from env vars"""
    from flask import render_template, make_response
    response = make_response(
        render_template('firebase-messaging-sw.js')
    )
    response.headers['Content-Type'] = 'application/javascript'
    response.headers['Service-Worker-Allowed'] = '/'
    return response

# Push Notification Debugger Route
@app.route('/debug/push')
def debug_push():
    """Render push notification debugger page"""
    from flask import render_template
    return render_template('debug_push.html')

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
