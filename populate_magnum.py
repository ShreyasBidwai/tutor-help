#!/usr/bin/env python3
"""Script to populate data for Magnum Institute"""
import sqlite3
import random
from database import get_db_connection
from werkzeug.security import generate_password_hash

def populate_magnum_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Find Magnum Institute user
        cursor.execute("SELECT id, mobile FROM users WHERE tuition_name LIKE '%Magnum%' LIMIT 1")
        user = cursor.fetchone()
        
        if not user:
            print("❌ Magnum Institute user not found!")
            return
            
        user_id = user['id']
        print(f"✓ Found Magnum Institute (User ID: {user_id})")
        
        # Create Batches
        batches_data = [
            {'name': 'Class 10 - Science', 'description': 'Science batch for 10th standard', 'start_time': '16:00', 'end_time': '17:30', 'days': 'Mon,Wed,Fri'},
            {'name': 'Class 10 - Maths', 'description': 'Maths batch for 10th standard', 'start_time': '17:30', 'end_time': '19:00', 'days': 'Tue,Thu,Sat'},
            {'name': 'Class 12 - Physics', 'description': 'Physics for JEE/NEET', 'start_time': '19:00', 'end_time': '20:30', 'days': 'Mon,Wed,Fri'},
            {'name': 'Class 12 - Chemistry', 'description': 'Chemistry for JEE/NEET', 'start_time': '07:00', 'end_time': '08:30', 'days': 'Tue,Thu,Sat'}
        ]
        
        batch_ids = []
        for batch in batches_data:
            cursor.execute('''
                INSERT INTO batches (name, description, start_time, end_time, days, user_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (batch['name'], batch['description'], batch['start_time'], batch['end_time'], batch['days'], user_id))
            batch_ids.append(cursor.lastrowid)
            print(f"✓ Created batch: {batch['name']}")
            
        # Create Students
        first_names = ['Aarav', 'Vihaan', 'Aditya', 'Sai', 'Arjun', 'Reyansh', 'Muhammad', 'Avyaan', 'Vivaan', 'Aryan',
                      'Aadhya', 'Diya', 'Saanvi', 'Ananya', 'Kiara', 'Fatima', 'Pari', 'Myra', 'Amaira', 'Ira']
        last_names = ['Sharma', 'Verma', 'Patel', 'Reddy', 'Nair', 'Khan', 'Singh', 'Gupta', 'Kumar', 'Joshi',
                     'Mehta', 'Malik', 'Saxena', 'Iyer', 'Chopra', 'Deshmukh', 'Yadav', 'Rao', 'Das', 'Bhat']
        
        schools = ['Delhi Public School', 'St. Xavier High', 'Kendriya Vidyalaya', 'Ryan International', 'Podar International']
        standards = ['10th', '10th', '12th', '12th'] # To match batches roughly
        
        students_count = 0
        existing_phones = set()
        
        # Get existing phones to avoid duplicates
        cursor.execute('SELECT phone FROM students WHERE user_id = ?', (user_id,))
        for row in cursor.fetchall():
            existing_phones.add(row['phone'])
            
        for i in range(40):
            batch_idx = i % len(batch_ids)
            batch_id = batch_ids[batch_idx]
            standard = '10th' if '10' in batches_data[batch_idx]['name'] else '12th'
            
            first = random.choice(first_names)
            last = random.choice(last_names)
            name = f"{first} {last}"
            
            # Generate unique phone
            while True:
                phone = f"9{random.randint(100000000, 999999999)}"
                if phone not in existing_phones:
                    existing_phones.add(phone)
                    break
            
            school = random.choice(schools)
            address = f"Sector {random.randint(1, 50)}, Noida"
            
            cursor.execute('''
                INSERT INTO students (name, phone, batch_id, address, school_name, standard, user_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, phone, batch_id, address, school, standard, user_id))
            students_count += 1
            
        print(f"✓ Created {students_count} students")
        
        conn.commit()
        print("\n✅ Data population for Magnum Institute completed successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    populate_magnum_data()
