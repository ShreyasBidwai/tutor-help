import logging
from datetime import datetime, timedelta
from database import get_db_connection
from firebase_admin import messaging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_fcm_notification(user_id, title, body, data=None):
    """Send FCM notification to a user"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get user's FCM tokens
        cursor.execute('''
            SELECT endpoint FROM push_subscriptions 
            WHERE user_id = ?
        ''', (user_id,))
        tokens = cursor.fetchall()
        
        if not tokens:
            conn.close()
            return
            
        # Send to all devices
        for token_row in tokens:
            token = token_row['endpoint']
            if not token or len(token) < 10: 
                continue
                
            try:
                message = messaging.Message(
                    notification=messaging.Notification(
                        title=title,
                        body=body,
                    ),
                    data=data or {},
                    token=token,
                    fcm_options=messaging.FCMOptions(analytics_label='tuition_track_notification')
                )
                messaging.send(message)
                logger.info(f"Sent notification to user {user_id} with label tuition_track_notification")
            except Exception as e:
                # Log error but continue
                pass
                
        conn.close()
    except Exception as e:
        logger.error(f"Error in send_fcm_notification: {e}")

def check_batch_start_reminders():
    """
    Check for batches starting NOW.
    Runs every 5 minutes, checks for batches starting in the next [0, 5] minute window.
    """
    logger.info("Running check_batch_start_reminders (At Start Time)")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        now = datetime.now()
        current_day = now.strftime('%a').lower()[0:2]
        
        # Monitor window: Now to Now + 5 mins
        start_monitor = now.strftime('%H:%M')
        end_monitor = (now + timedelta(minutes=5)).strftime('%H:%M')
        
        # Select batches starting in this window
        cursor.execute('''
            SELECT b.id, b.name, b.start_time, b.user_id, b.days
            FROM batches b
            WHERE b.notifications_enabled = 1
            AND b.start_time >= ? AND b.start_time < ?
        ''', (start_monitor, end_monitor))
        
        batches = cursor.fetchall()
        
        for batch in batches:
            if batch['days'] and current_day in batch['days'].lower():
                logger.info(f"Sending batch start alert for {batch['name']}")
                send_fcm_notification(
                    batch['user_id'],
                    f"Batch Started: {batch['name']}",
                    f"Your batch '{batch['name']}' has started.",
                    {'type': 'batch_start', 'url': '/batches'}
                )
                
        conn.close()
    except Exception as e:
        logger.error(f"Error in check_batch_start_reminders: {e}")

def check_attendance_reminders():
    """
    Check for batches that started 15 minutes ago.
    Runs every 5 minutes, checks for batches started in the window [15, 20] mins ago.
    """
    logger.info("Running check_attendance_reminders (15m Delay)")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        now = datetime.now()
        current_day = now.strftime('%a').lower()[0:2]
        today_date = now.strftime('%Y-%m-%d')
        
        # We want to notify if attendance isn't marked 15 mins after start.
        # Window: Batches that started between 15 and 20 minutes ago.
        # Logic:
        # Start Time <= (Now - 15 min)  AND  Start Time > (Now - 20 min)
        
        window_start = (now - timedelta(minutes=20)).strftime('%H:%M')
        window_end = (now - timedelta(minutes=15)).strftime('%H:%M')
        
        cursor.execute('''
            SELECT b.id, b.name, b.start_time, b.user_id, b.days
            FROM batches b
            WHERE b.notifications_enabled = 1
            AND b.start_time > ? AND b.start_time <= ?
        ''', (window_start, window_end))
        
        batches = cursor.fetchall()
        
        for batch in batches:
            if batch['days'] and current_day in batch['days'].lower():
                # Check if attendance marked today
                cursor.execute('''
                    SELECT 1 FROM attendance a
                    JOIN students s ON a.student_id = s.id
                    WHERE s.batch_id = ? AND a.date = ?
                    LIMIT 1
                ''', (batch['id'], today_date))
                
                attendance_marked = cursor.fetchone()
                
                if not attendance_marked:
                    logger.info(f"Sending attendance reminder for {batch['name']}")
                    send_fcm_notification(
                        batch['user_id'],
                        "Mark Attendance Reminder",
                        f"Attendance for '{batch['name']}' (Started: {batch['start_time']}) has not been marked yet.",
                        {'type': 'attendance', 'url': f"/batches/{batch['id']}/students"}
                    )
        
        conn.close()
    except Exception as e:
        logger.error(f"Error in check_attendance_reminders: {e}")
