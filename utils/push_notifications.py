"""Push notification utilities for TuitionTrack"""
from pywebpush import webpush, WebPushException
import json
from database import get_db_connection
from config import Config
import logging

logger = logging.getLogger(__name__)

def send_push_notification(subscription_info, title, body, url=None, notification_type=None, icon=None, badge=None):
    """
    Send a push notification to a subscribed user
    
    Args:
        subscription_info: Push subscription object (dict with keys, auth, endpoint)
        title: Notification title
        body: Notification body text
        url: URL to open when notification is clicked
        notification_type: Type of notification (attendance, homework, etc.)
        icon: Icon URL for notification
        badge: Badge URL for notification
    
    Returns:
        bool: True if sent successfully, False otherwise
    """
    try:
        payload = {
            'title': title,
            'body': body,
            'icon': icon or '/static/TutionTrack_appIcon.png',
            'badge': badge or '/static/TutionTrack_appIcon.png',
            'tag': notification_type or 'default',
            'requireInteraction': False,
            'data': {
                'url': url or '/',
                'type': notification_type or 'notification'
            },
            'vibrate': [200, 100, 200],
            'timestamp': None  # Will be set by browser
        }
        
        webpush(
            subscription_info=subscription_info,
            data=json.dumps(payload),
            vapid_private_key=Config.VAPID_PRIVATE_KEY,
            vapid_claims={
                "sub": f"mailto:{Config.VAPID_CLAIM_EMAIL}"
            }
        )
        
        logger.info(f"Push notification sent successfully: {title}")
        return True
        
    except WebPushException as e:
        logger.error(f"WebPushException sending notification: {e}")
        # If subscription is invalid, we might want to remove it
        if e.response and e.response.status_code == 410:  # Gone
            logger.warning("Subscription expired (410), should be removed from database")
        return False
    except Exception as e:
        logger.error(f"Error sending push notification: {e}")
        return False

def get_user_subscriptions(user_id):
    """
    Get all push subscriptions for a user
    
    Args:
        user_id: User ID (tutor or student)
    
    Returns:
        list: List of subscription dictionaries in format expected by pywebpush
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT endpoint, p256dh, auth
            FROM push_subscriptions
            WHERE user_id = ?
        ''', (user_id,))
        
        subscriptions = []
        for row in cursor.fetchall():
            # pywebpush expects this format
            subscriptions.append({
                'endpoint': row['endpoint'],
                'keys': {
                    'p256dh': row['p256dh'],
                    'auth': row['auth']
                }
            })
        
        return subscriptions
    finally:
        conn.close()

def send_notification_to_user(user_id, title, body, url=None, notification_type=None):
    """
    Send push notification to all subscriptions of a user
    
    Args:
        user_id: User ID
        title: Notification title
        body: Notification body
        url: URL to open
        notification_type: Type of notification
    
    Returns:
        int: Number of successful notifications sent
    """
    subscriptions = get_user_subscriptions(user_id)
    success_count = 0
    
    for subscription in subscriptions:
        if send_push_notification(subscription, title, body, url, notification_type):
            success_count += 1
    
    return success_count

def send_notification_to_students(student_ids, title, body, url=None, notification_type=None):
    """
    Send push notification to multiple students
    
    Args:
        student_ids: List of student IDs
        title: Notification title
        body: Notification body
        url: URL to open
        notification_type: Type of notification
    
    Returns:
        int: Total number of successful notifications sent
    """
    total_sent = 0
    
    for student_id in student_ids:
        total_sent += send_notification_to_user(student_id, title, body, url, notification_type)
    
    return total_sent

