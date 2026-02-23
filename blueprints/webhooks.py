from flask import Blueprint, request, jsonify, current_app
import logging
from jobs import check_batch_start_reminders, check_attendance_reminders
import os
from functools import wraps

# Setup Blueprint
webhooks_bp = Blueprint('webhooks', __name__)
logger = logging.getLogger(__name__)

def require_cron_secret(f):
    """Decorator to require a valid CRON_SECRET_KEY header or query param"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        expected_secret = current_app.config.get('CRON_SECRET_KEY') or os.environ.get('CRON_SECRET_KEY')
        
        # If no secret is configured in the environment, reject all requests for security
        if not expected_secret:
            logger.error("CRON_SECRET_KEY is not configured in the environment.")
            return jsonify({'error': 'Webhook service not configured'}), 500

        # Check Authorization header (Bearer token) or X-Cron-Secret custom header
        auth_header = request.headers.get('Authorization')
        custom_header = request.headers.get('X-Cron-Secret')
        query_param = request.args.get('secret')

        provided_secret = None
        if auth_header and auth_header.startswith('Bearer '):
            provided_secret = auth_header.split(' ')[1]
        elif custom_header:
            provided_secret = custom_header
        elif query_param:
            provided_secret = query_param

        if not provided_secret or provided_secret != expected_secret:
            logger.warning(f"Unauthorized cron webhook attempt from {request.remote_addr}")
            return jsonify({'error': 'Unauthorized'}), 401
            
        return f(*args, **kwargs)
    return decorated_function

@webhooks_bp.route('/api/webhooks/cron', methods=['POST', 'GET'])
@require_cron_secret
def trigger_cron_jobs():
    """
    Endpoint intended to be hit by an external cron service (like cron-job.org)
    every 5 minutes.
    """
    logger.info("External Cron Webhook Triggered")

    try:
        # Run batch start reminders
        check_batch_start_reminders()
        
        # Run attendance reminders
        check_attendance_reminders()

        return jsonify({
            'status': 'success',
            'message': 'Cron jobs executed successfully',
            'timestamp': request.args.get('time', 'unknown')
        }), 200

    except Exception as e:
        logger.error(f"Error executing cron jobs via webhook: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
