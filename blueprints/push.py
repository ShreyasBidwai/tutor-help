from flask import Blueprint, request, jsonify, session, current_app
from database import get_db_connection
import json
import logging

push_bp = Blueprint('push', __name__)
logger = logging.getLogger(__name__)

@push_bp.route('/api/push/subscribe', methods=['POST'])
def subscribe():
    """Subscribe a user to push notifications"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    if not data or 'endpoint' not in data or 'keys' not in data:
        return jsonify({'error': 'Invalid subscription data'}), 400
    
    endpoint = data['endpoint']
    keys = data['keys']
    p256dh = keys.get('p256dh')
    auth = keys.get('auth')
    user_id = session['user_id']
    user_agent = request.headers.get('User-Agent')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if subscription already exists
        cursor.execute('SELECT id FROM push_subscriptions WHERE endpoint = ?', (endpoint,))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing subscription
            cursor.execute('''
                UPDATE push_subscriptions 
                SET user_id = ?, p256dh = ?, auth = ?, user_agent = ?, created_at = CURRENT_TIMESTAMP
                WHERE endpoint = ?
            ''', (user_id, p256dh, auth, user_agent, endpoint))
        else:
            # Create new subscription
            cursor.execute('''
                INSERT INTO push_subscriptions (user_id, endpoint, p256dh, auth, user_agent)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, endpoint, p256dh, auth, user_agent))
            
        conn.commit()
        logger.info(f"Push subscription saved for user {user_id}")
        return jsonify({'status': 'success', 'message': 'Subscribed successfully'}), 201
        
    except Exception as e:
        logger.error(f"Error saving push subscription: {e}")
        return jsonify({'error': 'Database error'}), 500
    finally:
        conn.close()

@push_bp.route('/api/push/unsubscribe', methods=['POST'])
def unsubscribe():
    """Unsubscribe a user from push notifications"""
    data = request.get_json()
    if not data or 'endpoint' not in data:
        return jsonify({'error': 'Invalid data'}), 400
        
    endpoint = data['endpoint']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('DELETE FROM push_subscriptions WHERE endpoint = ?', (endpoint,))
        conn.commit()
        return jsonify({'status': 'success', 'message': 'Unsubscribed successfully'}), 200
    except Exception as e:
        logger.error(f"Error removing push subscription: {e}")
        return jsonify({'error': 'Database error'}), 500
    finally:
        conn.close()

@push_bp.route('/api/push/status', methods=['GET'])
def check_status():
    """Check if current user has any active subscriptions"""
    if 'user_id' not in session:
        return jsonify({'subscribed': False}), 200
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT COUNT(*) FROM push_subscriptions WHERE user_id = ?', (session['user_id'],))
        count = cursor.fetchone()[0]
        return jsonify({'subscribed': count > 0}), 200
    except Exception:
        return jsonify({'subscribed': False}), 200
    finally:
        conn.close()
