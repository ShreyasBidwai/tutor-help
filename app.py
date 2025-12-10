"""Main Flask application - Tutor Help PWA"""
from flask import Flask, jsonify
from config import Config
from database import init_db, migrate_db, add_indexes
import os
import logging

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

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

# Initialize database on startup
if not os.path.exists(Config.DATABASE):
    init_db()
    add_indexes()
else:
    migrate_db()
    add_indexes()

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
