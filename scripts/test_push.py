import sys
import os
import logging

# Add parent directory to path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db_connection
import firebase_admin
from firebase_admin import credentials, messaging
from config import Config

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_firebase():
    """Initialize Firebase Admin SDK manually for this script"""
    try:
        # Check if already initialized
        firebase_admin.get_app()
    except ValueError:
        # Not initialized, do it now
        if not os.path.exists(Config.FIREBASE_SERVICE_ACCOUNT_KEY):
            print(f"Error: Service account file not found at {Config.FIREBASE_SERVICE_ACCOUNT_KEY}")
            return False
            
        cred = credentials.Certificate(Config.FIREBASE_SERVICE_ACCOUNT_KEY)
        firebase_admin.initialize_app(cred)
    return True

def list_users_with_tokens():
    """List users (tutors/students) who have at least one FCM token"""
    conn = get_db_connection()
    
    # We need to query both users and students tables because the push_subscriptions
    # table might contain IDs from both (due to a schema ambiguity where user_id 
    # refers to session['user_id'] which differs by role).
    
    query = '''
        SELECT u.id, u.tutor_name as name, u.mobile as contact, 'tutor' as role
        FROM users u
        JOIN push_subscriptions ps ON u.id = ps.user_id
        WHERE ps.endpoint IS NOT NULL AND length(ps.endpoint) > 10
        GROUP BY u.id
        
        UNION
        
        SELECT s.id, s.name, s.phone as contact, 'student' as role
        FROM students s
        JOIN push_subscriptions ps ON s.id = ps.user_id
        WHERE ps.endpoint IS NOT NULL AND length(ps.endpoint) > 10
        GROUP BY s.id
    '''
    
    users = conn.execute(query).fetchall()
    conn.close()
    return users

def send_test_notification(user_id):
    """Send a test notification to a specific user"""
    conn = get_db_connection()
    tokens = conn.execute('SELECT endpoint FROM push_subscriptions WHERE user_id = ?', (user_id,)).fetchall()
    conn.close()
    
    if not tokens:
        print(f"No tokens found for user {user_id}")
        return

    success_count = 0
    failure_count = 0
    
    print(f"\nAttempting to send to {len(tokens)} device(s)...")
    
    for row in tokens:
        token = row['endpoint']
        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title="Test Notification",
                    body="This is a test message from TuitionTrack server!",
                ),
                data={
                    'type': 'test',
                    'click_action': '/',
                    'body': 'This is a test message from TuitionTrack server!',
                    'title': 'Test Notification'
                },
                token=token,
            )
            response = messaging.send(message)
            print(f"✅ Sent successfully to device ending in ...{token[-5:]}")
            success_count += 1
        except Exception as e:
            print(f"❌ Failed to send to device ending in ...{token[-5:]}: {e}")
            failure_count += 1
            
    print(f"\nSummary: {success_count} sent, {failure_count} failed.")

if __name__ == "__main__":
    print("=== TuitionTrack Notification Tester ===")
    
    if not setup_firebase():
        sys.exit(1)
        
    users = list_users_with_tokens()
    
    if not users:
        print("\nNo users found with registered devices.")
        print("Tip: Log in to the app on a browser and allow notifications first.")
        sys.exit(0)
        
    print(f"\nFound {len(users)} users with registered devices:")
    print("-" * 60)
    print(f"{'ID':<5} | {'Role':<10} | {'Name':<20} | {'Contact'}")
    print("-" * 60)
    
    for u in users:
        u_id = u['id']
        u_role = u['role'] or "Unknown"
        u_name = u['name'] or "No Name"
        u_contact = u['contact'] or "No Contact"
        print(f"{u_id:<5} | {u_role:<10} | {u_name:<20} | {u_contact}")
        
    print("-" * 50)
    
    try:
        selection = input("\nEnter User ID to test (or 'q' to quit): ")
        if selection.lower() == 'q':
            sys.exit(0)
            
        user_id = int(selection)
        send_test_notification(user_id)
        
    except ValueError:
        print("Invalid input. Please enter a valid User ID number.")
