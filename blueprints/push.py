from flask import Blueprint, request, jsonify, session, current_app
from database import get_db_connection
import json
import logging

push_bp = Blueprint('push', __name__)
logger = logging.getLogger(__name__)

@push_bp.route('/api/push/subscribe', methods=['POST'])
def subscribe():
    """Subscribe a user to push notifications (Web Push or FCM)"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
        
    user_id = session['user_id']
    user_agent = request.headers.get('User-Agent')
    token_type = data.get('token_type', 'webpush')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if token_type == 'fcm':
            fcm_token = data.get('fcm_token')
            if not fcm_token:
                return jsonify({'error': 'Invalid FCM token'}), 400
                
            # Check if this token already exists for this user
            cursor.execute('''
                SELECT id FROM push_subscriptions 
                WHERE user_id = ? AND fcm_token = ? AND token_type = 'fcm'
            ''', (user_id, fcm_token))
            existing = cursor.fetchone()
            
            if not existing:
                cursor.execute('''
                    INSERT INTO push_subscriptions (user_id, fcm_token, token_type, user_agent)
                    VALUES (?, ?, 'fcm', ?)
                ''', (user_id, fcm_token, user_agent))
                conn.commit()
            
            logger.info(f"FCM token saved for user {user_id}")
            return jsonify({'status': 'success', 'message': 'FCM token subscribed successfully'}), 201
            
        else:
            # Web Push subscription (existing logic)
            if 'endpoint' not in data or 'keys' not in data:
                return jsonify({'error': 'Invalid subscription data'}), 400
                
            endpoint = data['endpoint']
            keys = data['keys']
            p256dh = keys.get('p256dh')
            auth = keys.get('auth')
            
            # Check if subscription already exists
            cursor.execute('SELECT id FROM push_subscriptions WHERE endpoint = ?', (endpoint,))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing subscription
                cursor.execute('''
                    UPDATE push_subscriptions 
                    SET user_id = ?, p256dh = ?, auth = ?, user_agent = ?, token_type = 'webpush', created_at = CURRENT_TIMESTAMP
                    WHERE endpoint = ?
                ''', (user_id, p256dh, auth, user_agent, endpoint))
            else:
                # Create new subscription
                cursor.execute('''
                    INSERT INTO push_subscriptions (user_id, endpoint, p256dh, auth, user_agent, token_type)
                    VALUES (?, ?, ?, ?, ?, 'webpush')
                ''', (user_id, endpoint, p256dh, auth, user_agent))
                
            conn.commit()
            logger.info(f"Web Push subscription saved for user {user_id}")
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
    if not data:
        return jsonify({'error': 'Invalid data'}), 400
        
    endpoint = data.get('endpoint')
    fcm_token = data.get('fcm_token')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if endpoint:
            cursor.execute('DELETE FROM push_subscriptions WHERE endpoint = ?', (endpoint,))
        elif fcm_token:
            cursor.execute('DELETE FROM push_subscriptions WHERE fcm_token = ?', (fcm_token,))
            
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
