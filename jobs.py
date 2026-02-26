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
        
        from utils import get_ist_now
        now = get_ist_now()
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
        
        from utils import get_ist_now
        now = get_ist_now()
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


def generate_monthly_fees():
    """
    Idempotent: generate fee records for ALL active students for the current month.
    Run on 1st of every month. Safe to call multiple times — uses INSERT OR IGNORE.
    """
    logger.info("Running generate_monthly_fees")
    try:
        from utils import get_ist_now
        now = get_ist_now()
        month = now.strftime('%Y-%m')

        conn = get_db_connection()
        cursor = conn.cursor()

        # Get all tutors who have a fee config set up
        cursor.execute('''
            SELECT pc.user_id, pc.monthly_fee
            FROM tutor_payment_config pc
            WHERE pc.monthly_fee > 0
        ''')
        configs = cursor.fetchall()

        created = 0
        for cfg in configs:
            cursor.execute(
                'SELECT id FROM students WHERE user_id = ?', (cfg['user_id'],)
            )
            students = cursor.fetchall()
            for s in students:
                try:
                    cursor.execute('''
                        INSERT OR IGNORE INTO student_fee_records
                            (student_id, user_id, month, amount, status)
                        VALUES (?, ?, ?, ?, 'pending')
                    ''', (s['id'], cfg['user_id'], month, cfg['monthly_fee']))
                    if cursor.rowcount:
                        created += 1
                except Exception:
                    pass

        conn.commit()
        conn.close()
        logger.info(f"generate_monthly_fees: created {created} records for {month}")

    except Exception as e:
        logger.error(f"Error in generate_monthly_fees: {e}")


def send_fee_reminders():
    """
    Daily job: send push notifications to students with pending/overdue fees.
    Only fires on a tutor's configured due_day.
    Updates reminder_sent_at to prevent duplicate sends on the same day.
    """
    logger.info("Running send_fee_reminders")
    try:
        from utils import get_ist_now
        now = get_ist_now()
        today_day = now.day
        month = now.strftime('%Y-%m')
        today_str = now.strftime('%Y-%m-%d')

        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch tutors whose due_day matches today
        cursor.execute('''
            SELECT pc.user_id, pc.due_day
            FROM tutor_payment_config pc
            WHERE pc.reminders_enabled = 1 AND pc.due_day = ?
        ''', (today_day,))
        configs = cursor.fetchall()

        for cfg in configs:
            # Find pending students where reminder not yet sent today
            cursor.execute('''
                SELECT sfr.id, sfr.student_id
                FROM student_fee_records sfr
                WHERE sfr.user_id = ? AND sfr.month = ?
                  AND sfr.status IN ('pending', 'overdue')
                  AND (sfr.reminder_sent_at IS NULL
                       OR date(sfr.reminder_sent_at) < ?)
            ''', (cfg['user_id'], month, today_str))
            records = cursor.fetchall()

            for rec in records:
                # Notify the student (student's user session record via push_subscriptions)
                # For now, notify the tutor as well so they can follow up
                send_fcm_notification(
                    cfg['user_id'],
                    "Fee Reminder",
                    f"Some students have unpaid fees for {month}.",
                    {'type': 'fees', 'url': '/payments?tab=pending'}
                )
                cursor.execute('''
                    UPDATE student_fee_records
                    SET reminder_sent_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (rec['id'],))
                break  # One notification per tutor per day is enough

        conn.commit()
        conn.close()

    except Exception as e:
        logger.error(f"Error in send_fee_reminders: {e}")


def mark_overdue_fees():
    """
    Mark fees as overdue if past due_day + 3 days and still pending.
    Run daily.
    """
    logger.info("Running mark_overdue_fees")
    try:
        from utils import get_ist_now
        now = get_ist_now()
        month = now.strftime('%Y-%m')
        year, mon = now.year, now.month

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT user_id, due_day FROM tutor_payment_config WHERE monthly_fee > 0')
        configs = cursor.fetchall()

        for cfg in configs:
            due_date = f"{year}-{mon:02d}-{cfg['due_day']:02d}"
            # Overdue = 3 days after due date
            from datetime import datetime, timedelta
            overdue_from = (datetime.strptime(due_date, '%Y-%m-%d') + timedelta(days=3)).strftime('%Y-%m-%d')
            today_str = now.strftime('%Y-%m-%d')

            if today_str >= overdue_from:
                cursor.execute('''
                    UPDATE student_fee_records
                    SET status = 'overdue', updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ? AND month = ? AND status = 'pending'
                ''', (cfg['user_id'], month))

        conn.commit()
        conn.close()

    except Exception as e:
        logger.error(f"Error in mark_overdue_fees: {e}")

