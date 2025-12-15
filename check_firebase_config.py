from config import Config

def check_firebase_config():
    keys = [
        'FIREBASE_API_KEY',
        'FIREBASE_AUTH_DOMAIN',
        'FIREBASE_PROJECT_ID',
        'FIREBASE_STORAGE_BUCKET',
        'FIREBASE_MESSAGING_SENDER_ID',
        'FIREBASE_APP_ID'
    ]
    
    print("Checking Firebase Configuration...")
    missing = []
    for key in keys:
        value = getattr(Config, key, '')
        if not value:
            missing.append(key)
        else:
            print(f"{key}: [PRESENT] (Starts with {value[:4]}...)")
            
    if missing:
        print("\nMISSING KEYS:", missing)
    else:
        print("\nAll keys appear to be present.")

if __name__ == "__main__":
    check_firebase_config()
