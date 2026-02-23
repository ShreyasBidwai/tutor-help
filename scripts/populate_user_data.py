import sqlite3
from datetime import date, timedelta
import random
from werkzeug.security import generate_password_hash
import os

# Configuration
DB_NAME = 'tutor_app.db'
TARGET_MOBILE = '8308248985'

def get_db_connection():
    # Go up one level if script is run from scripts/ dir
    db_path = DB_NAME
    if not os.path.exists(db_path) and os.path.exists(os.path.join('..', DB_NAME)):
        db_path = os.path.join('..', DB_NAME)
        
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def populate():
    print(f"Connecting to database...")
    conn = get_db_connection()
    c = conn.cursor()

    # 1. Get User
    print(f"Looking for user {TARGET_MOBILE}...")
    c.execute('SELECT id FROM users WHERE mobile = ?', (TARGET_MOBILE,))
    user = c.fetchone()
    if not user:
        print(f"❌ User {TARGET_MOBILE} not found! Please create the user first.")
        conn.close()
        return
        
    user_id = user['id']
    print(f"✅ Found user {TARGET_MOBILE} with ID {user_id}")

    # 2. Create Batches
    print(f"\nCreating 3 Batches...")
    batch_names = ['Physics Batch 2026', 'Chemistry Batch 2026', 'Maths Batch 2026']
    batch_ids = []
    
    for i, b_name in enumerate(batch_names):
        start_time = f"{10+i*3}:00" # 10:00, 13:00, 16:00
        end_time = f"{11+i*3}:30"   # 11:30, 14:30, 17:30
        
        c.execute('''
            INSERT INTO batches (name, description, start_time, end_time, user_id, days) 
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (b_name, f"Test Batch {i+1}", start_time, end_time, user_id, "Mon,Wed,Fri"))
        
        b_id = c.lastrowid
        batch_ids.append(b_id)
        print(f"  - Created '{b_name}' (ID: {b_id})")

    # 3. Create Students
    print(f"\nCreating 20 Students per Batch (Total 60)...")
    student_ids = []
    
    # Common Indian names for variety
    first_names = ["Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh", "Ayaan", "Krishna", "Ishaan", "Diya", "Saanvi", "Ananya", "Aadhya", "Pari", "Myra", "Riya", "Anvi", "Kiara", "Ira"]
    last_names = ["Sharma", "Verma", "Gupta", "Malik", "Singh", "Reddy", "Nair", "Patel", "Mehta", "Joshi"]
    
    for b_idx, b_id in enumerate(batch_ids):
        print(f"  - Adding students to Batch ID {b_id}...")
        for i in range(1, 21):
            fname = random.choice(first_names)
            lname = random.choice(last_names)
            s_name = f"{fname} {lname}"
            
            # Unique pseudo-random phone number ensuring uniqueness per user
            # Format: 9 + user_id(2) + batch_idx(1) + student_num(2) + random(4) -> 10 digits
            # Actually simple sequential might be safer for collision: 9 + 830 + batch_id(2) + i(2) -> 9830000000 style
            # Let's use: 9000 + batch_id(2) + i(2) -> 90000101
            # But duplicate phones are allowed across different users? Schema says "UNIQUE(user_id, phone)"
            # So as long as unique for THIS user.
            
            # Pattern: 8s bb ii (8 + batch index + student index) - simple strings
            # e.g. "8001"
            s_phone = f"99{b_id:03d}{i:03d}" 
            
            pwd = f"pass{i}" # Simple password
            pwd_hash = generate_password_hash(pwd)
            
            # Handle password column if it exists (legacy)
            try:
                c.execute('''
                    INSERT INTO students (name, phone, batch_id, user_id, password, password_hash, school_name, standard) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (s_name, s_phone, b_id, user_id, pwd, pwd_hash, 'City High School', 'Class 12'))
                student_ids.append(c.lastrowid)
            except sqlite3.IntegrityError:
                # Handle unique constraint violation (if run multiple times)
                print(f"    ! Student {s_name} ({s_phone}) already exists, skipping")
                # Try to fetch existing id?
                continue

    print(f"✅ Created {len(student_ids)} students.")

    # 4. Generate Attendance
    print(f"\nGenerating Attendance (Feb 1, 2026 - Feb 19, 2026)...")
    
    start_date = date(2026, 2, 1)
    end_date = date(2026, 2, 19)
    # end_date = date.today() # User said "till today", assuming system time matches roughly or using fixed date as per prompt
    
    total_days = (end_date - start_date).days + 1
    generated_records = 0
    
    # Iterate through dates
    curr_date = start_date
    while curr_date <= end_date:
        # Skip Sundays? usually tuition is off? 
        # User didn't specify. I'll include all days or maybe skip Sunday (weekday 6)
        if curr_date.weekday() == 6: # Sunday
            curr_date += timedelta(days=1)
            continue
            
        day_records = 0
        for s_id in student_ids:
            # 85% attendance rate
            is_present = 1 if random.random() < 0.85 else 0
            
            try:
                c.execute('''
                    INSERT INTO attendance (student_id, date, present, status, user_id) 
                    VALUES (?, ?, ?, ?, ?)
                ''', (s_id, curr_date, is_present, is_present, user_id))
                day_records += 1
            except sqlite3.IntegrityError:
                pass # Already exists
                
        generated_records += day_records
        # print(f"  - {curr_date}: {day_records} records")
        curr_date += timedelta(days=1)

    print(f"✅ inserted {generated_records} attendance records.")
    
    conn.commit()
    conn.close()
    print("\nPopulation Complete! 🎉")

if __name__ == '__main__':
    populate()
