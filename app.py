"""Main Flask application - Tutor Help PWA"""
from flask import Flask
from config import Config
from database import init_db, migrate_db
import os

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

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

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(students_bp)
app.register_blueprint(batches_bp)
app.register_blueprint(attendance_bp)
app.register_blueprint(homework_bp)
app.register_blueprint(reports_bp)
app.register_blueprint(payments_bp)

# Initialize database on startup
if not os.path.exists(Config.DATABASE):
    init_db()
else:
    migrate_db()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
