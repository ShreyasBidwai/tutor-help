from flask import Blueprint, request, jsonify, current_app
import logging
from jobs import check_batch_start_reminders, check_attendance_reminders, \
    generate_monthly_fees, send_fee_reminders, mark_overdue_fees
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
    Endpoint hit by an external cron service every 5 minutes.
    Batch/attendance reminders, plus daily fee jobs (self-guarded by date).
    """
    logger.info("External Cron Webhook Triggered")

    try:
        # Batch notifications
        check_batch_start_reminders()
        check_attendance_reminders()

        # Payment jobs — each function is self-guarded:
        # send_fee_reminders only acts on tutor due_days matching today
        # mark_overdue_fees only marks overdue if past due_day + 3
        send_fee_reminders()
        mark_overdue_fees()

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


@webhooks_bp.route('/api/webhooks/cron/monthly', methods=['POST', 'GET'])
@require_cron_secret
def trigger_monthly_jobs():
    """
    Endpoint hit once on the 1st of each month to generate fee records.
    Schedule this on cron-job.org as: 0 8 1 * * (8 AM IST on 1st of month).
    """
    logger.info("Monthly Cron Webhook Triggered")

    try:
        generate_monthly_fees()

        return jsonify({
            'status': 'success',
            'message': 'Monthly fee records generated',
            'timestamp': request.args.get('time', 'unknown')
        }), 200

    except Exception as e:
        logger.error(f"Error in monthly cron: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
