from config import Config

def check_firebase_config():
    keys = [
        'FIREBASE_WEB_API_KEY',
        'FIREBASE_WEB_AUTH_DOMAIN',
        'FIREBASE_WEB_PROJECT_ID',
        'FIREBASE_WEB_STORAGE_BUCKET',
        'FIREBASE_WEB_MESSAGING_SENDER_ID',
        'FIREBASE_WEB_APP_ID'
    ]
    
    print("Checking Firebase Configuration...")
    missing = []
    import os
    from dotenv import load_dotenv
    load_dotenv()

    for key in keys:
        value = os.environ.get(key)
        if not value:
            missing.append(key)
        else:
            print(f"{key}: [PRESENT] (Starts with {value[:4]}...)")
            if key == 'FIREBASE_WEB_PROJECT_ID' and value != 'tutiontrack-48c6e':
                print(f"WARNING: FIREBASE_WEB_PROJECT_ID mismatch. Expected 'tutiontrack-48c6e', got '{value}'")
            
    if missing:
        print("\nMISSING KEYS:", missing)
    else:
        print("\nAll keys appear to be present.")
        
    # Check VAPID keys
    if not Config.VAPID_PUBLIC_KEY:
        print("WARNING: VAPID_PUBLIC_KEY is missing")
    if not Config.VAPID_PRIVATE_KEY:
        print("WARNING: VAPID_PRIVATE_KEY is missing")

if __name__ == "__main__":
    check_firebase_config()
