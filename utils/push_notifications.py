"""Push notification utilities for TuitionTrack using Firebase Cloud Messaging (FCM)"""
from firebase_admin import messaging
from database import get_db_connection
import logging

logger = logging.getLogger(__name__)

def send_fcm_notification(token, title, body, data=None):
    """
    Send a push notification to a specific FCM token
    
    Args:
        token: FCM registration token
        title: Notification title
        body: Notification body text
        data: Dictionary of data payload (optional)
        
    Returns:
        bool: True if sent successfully, False otherwise
    """
    try:
        # Validate token
        if not token or len(token) < 10:
            return False
            
        # Construct message
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data=data or {},
            token=token,
        )
        
        # Send message
        messaging.send(message)
        logger.info(f"FCM notification sent successfully to token end: ...{token[-5:]}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending FCM notification: {e}")
        # Identify invalid tokens? (e.g. Unregistered)
        return False

def get_user_tokens(user_id):
    """
    Get all FCM tokens for a user
    
    Args:
        user_id: User ID (tutor or student)
    
    Returns:
        list: List of token strings
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # We store FCM token in 'endpoint' column
        cursor.execute('''
            SELECT endpoint
            FROM push_subscriptions
            WHERE user_id = ?
        ''', (user_id,))
        
        tokens = [row['endpoint'] for row in cursor.fetchall() if row['endpoint']]
        return tokens
    finally:
        conn.close()

def send_notification_to_user(user_id, title, body, url=None, notification_type=None, icon=None, badge=None):
    """
    Send push notification to all devices of a user
    
    Args:
        user_id: User ID
        title: Notification title
        body: Notification body
        url: URL to open
        notification_type: Type of notification
        icon: (Optional) Icon URL - Handled by client/FCM mostly, but passed in data
        badge: (Optional) Badge URL
    
    Returns:
        int: Number of successful notifications sent
    """
    tokens = get_user_tokens(user_id)
    success_count = 0
    
    # Prepare data payload
    data_payload = {
        'url': url or '/',
        'type': notification_type or 'notification'
    }
    
    # Add icon/badge to data if needed for custom handling, though FCM Notification object handles main ones
    if icon:
        data_payload['icon'] = icon
    if badge:
        data_payload['badge'] = badge
        
    for token in tokens:
        if send_fcm_notification(token, title, body, data=data_payload):
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
