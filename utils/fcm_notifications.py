"""Firebase Cloud Messaging notification utilities for TuitionTrack"""
import firebase_admin
from firebase_admin import credentials, messaging
from database import get_db_connection
from config import Config
import logging
import os

logger = logging.getLogger(__name__)

# Global flag to track Firebase initialization
_firebase_initialized = False

def init_firebase():
    """Initialize Firebase Admin SDK (call once at startup)"""
    global _firebase_initialized
    
    if _firebase_initialized:
        return True
    
    # Check if service account key is configured
    if not Config.FIREBASE_SERVICE_ACCOUNT_KEY:
        logger.warning("Firebase service account key not configured. FCM notifications disabled.")
        return False
    
    # Check if file exists
    if not os.path.exists(Config.FIREBASE_SERVICE_ACCOUNT_KEY):
        logger.warning(f"Firebase service account key file not found: {Config.FIREBASE_SERVICE_ACCOUNT_KEY}")
        return False
    
    try:
        # Initialize Firebase Admin SDK
        if not firebase_admin._apps:
            cred = credentials.Certificate(Config.FIREBASE_SERVICE_ACCOUNT_KEY)
            firebase_admin.initialize_app(cred)
            logger.info("Firebase Admin SDK initialized successfully")
        
        _firebase_initialized = True
        return True
    except Exception as e:
        logger.error(f"Error initializing Firebase Admin SDK: {e}")
        return False

def send_fcm_notification(fcm_token, title, body, url=None, notification_type=None, icon=None, badge=None):
    """
    Send a push notification via FCM to a single device
    
    Args:
        fcm_token: FCM device token
        title: Notification title
        body: Notification body text
        url: URL to open when notification is clicked
        notification_type: Type of notification (attendance, homework, etc.)
        icon: Icon URL for notification
        badge: Badge URL for notification
    
    Returns:
        bool: True if sent successfully, False otherwise
    """
    if not init_firebase():
        logger.warning("Firebase not initialized, cannot send FCM notification")
        return False
    
    try:
        # Build the notification image/icon absolute URLs
        icon_url = icon
        if icon_url and not icon_url.startswith('http'):
            icon_url = f"https://tutiontrack.onrender.com{icon_url}"
        else:
            icon_url = 'https://tutiontrack.onrender.com/static/TutionTrack_appIcon_192x192.png'

        # Build the notification message
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
                image=icon_url
            ),
            data={
                'url': url or '/',
                'type': notification_type or 'notification',
                'click_action': url or '/'
            },
            android=messaging.AndroidConfig(
                notification=messaging.AndroidNotification(
                    channel_id='default_channel',
                    priority='high',
                    default_sound=True,
                    default_vibrate_timings=True,
                    icon='stock_ticker_update', # Reference to android res icon
                    color='#4F46E5'
                )
            ),
            token=fcm_token,
            webpush=messaging.WebpushConfig(
                notification=messaging.WebpushNotification(
                    title=title,
                    body=body,
                    icon=icon_url,
                    badge='https://tutiontrack.onrender.com/static/TutionTrack_appIcon_96x96.png',
                    tag=notification_type or 'default',
                    require_interaction=False,
                    vibrate=[200, 100, 200]
                ),
                fcm_options=messaging.WebpushFCMOptions(
                    link=url or '/'
                )
            )
        )
        
        # Send the message
        response = messaging.send(message)
        logger.info(f"FCM notification sent successfully: {response}")
        return True
        
    except messaging.UnregisteredError:
        logger.warning(f"FCM token is invalid or unregistered: {fcm_token[:20]}...")
        # Token is invalid, should be removed from database
        return False
    except Exception as e:
        logger.error(f"Error sending FCM notification: {e}")
        return False

def get_user_fcm_tokens(user_id):
    """
    Get all FCM tokens for a user
    
    Args:
        user_id: User ID (tutor or student)
    
    Returns:
        list: List of FCM tokens
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT fcm_token
            FROM push_subscriptions
            WHERE user_id = ? AND token_type = 'fcm' AND fcm_token IS NOT NULL
        ''', (user_id,))
        
        tokens = [row['fcm_token'] for row in cursor.fetchall()]
        return tokens
    finally:
        conn.close()

def send_fcm_to_user(user_id, title, body, url=None, notification_type=None):
    """
    Send FCM notification to all devices of a user
    
    Args:
        user_id: User ID
        title: Notification title
        body: Notification body
        url: URL to open
        notification_type: Type of notification
    
    Returns:
        int: Number of successful notifications sent
    """
    tokens = get_user_fcm_tokens(user_id)
    success_count = 0
    
    for token in tokens:
        if send_fcm_notification(token, title, body, url, notification_type):
            success_count += 1
    
    return success_count

def send_fcm_to_students(student_ids, title, body, url=None, notification_type=None):
    """
    Send FCM notification to multiple students
    
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
        total_sent += send_fcm_to_user(student_id, title, body, url, notification_type)
    
    return total_sent

def send_fcm_multicast(fcm_tokens, title, body, url=None, notification_type=None):
    """
    Send FCM notification to multiple devices at once (more efficient)
    
    Args:
        fcm_tokens: List of FCM device tokens
        title: Notification title
        body: Notification body
        url: URL to open
        notification_type: Type of notification
    
    Returns:
        int: Number of successful notifications sent
    """
    if not init_firebase():
        logger.warning("Firebase not initialized, cannot send FCM notifications")
        return 0
    
    if not fcm_tokens:
        return 0
    
    try:
        # Build the notification image/icon absolute URLs
        icon_url = 'https://tutiontrack.onrender.com/static/TutionTrack_appIcon_192x192.png'

        # Build the multicast message
        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=title,
                body=body,
                image=icon_url
            ),
            data={
                'url': url or '/',
                'type': notification_type or 'notification',
                'click_action': url or '/'
            },
            android=messaging.AndroidConfig(
                notification=messaging.AndroidNotification(
                    channel_id='default_channel',
                    priority='high',
                    default_sound=True,
                    default_vibrate_timings=True,
                    icon='stock_ticker_update',
                    color='#4F46E5'
                )
            ),
            tokens=fcm_tokens,
            webpush=messaging.WebpushConfig(
                notification=messaging.WebpushNotification(
                    title=title,
                    body=body,
                    icon=icon_url,
                    badge='https://tutiontrack.onrender.com/static/TutionTrack_appIcon_96x96.png',
                    tag=notification_type or 'default',
                    require_interaction=False,
                    vibrate=[200, 100, 200]
                ),
                fcm_options=messaging.WebpushFCMOptions(
                    link=url or '/'
                )
            )
        )
        
        # Send to multiple devices
        response = messaging.send_multicast(message)
        logger.info(f"FCM multicast sent: {response.success_count} successful, {response.failure_count} failed")
        return response.success_count
        
    except Exception as e:
        logger.error(f"Error sending FCM multicast: {e}")
        return 0
