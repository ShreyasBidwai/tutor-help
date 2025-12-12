#!/usr/bin/env python3
"""Script to clean and populate database with test data"""
import sqlite3
from database import get_db_connection
from werkzeug.security import generate_password_hash
from datetime import date, timedelta
import random

def clean_database():
    """Delete all data from all tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Disable foreign key constraints temporarily
        cursor.execute('PRAGMA foreign_keys = OFF')
        
        # Delete in order to respect foreign key constraints
        cursor.execute('DELETE FROM attendance')
        attendance_count = cursor.rowcount
        print(f"✓ Deleted {attendance_count} attendance records")
        
        cursor.execute('DELETE FROM homework')
        homework_count = cursor.rowcount
        print(f"✓ Deleted {homework_count} homework records")
        
        cursor.execute('DELETE FROM students')
        students_count = cursor.rowcount
        print(f"✓ Deleted {students_count} student records")
        
        cursor.execute('DELETE FROM batches')
        batches_count = cursor.rowcount
        print(f"✓ Deleted {batches_count} batch records")
        
        # Keep users but clean their data
        cursor.execute('UPDATE users SET tutor_name = NULL, tuition_name = NULL, address = NULL WHERE mobile = "1111111111"')
        
        # Re-enable foreign key constraints
        cursor.execute('PRAGMA foreign_keys = ON')
        
        # Commit changes
        conn.commit()
        
        print("\n✓ Database cleaned successfully!")
        print(f"  - Attendance: {attendance_count} records")
        print(f"  - Homework: {homework_count} records")
        print(f"  - Students: {students_count} records")
        print(f"  - Batches: {batches_count} records")
        
    except Exception as e:
        print(f"Error cleaning database: {e}")
        conn.rollback()
    finally:
        conn.close()

def populate_database():
    """Populate database with test data"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get or create tutor user
        cursor.execute('SELECT id FROM users WHERE mobile = ?', ('1111111111',))
        tutor_user = cursor.fetchone()
        
        if tutor_user:
            tutor_id = tutor_user['id']
            # Update existing user to ensure all fields are set
            cursor.execute('''
                UPDATE users 
                SET tutor_name = ?, tuition_name = ?, role = ?, onboarding_completed = ?
                WHERE id = ?
            ''', ('Test Tutor', 'Test Tuition Center', 'tutor', 1, tutor_id))
            print(f"✓ Updated existing tutor (ID: {tutor_id})")
        else:
            # Create tutor user
            cursor.execute('''
                INSERT INTO users (mobile, tutor_name, tuition_name, role, onboarding_completed)
                VALUES (?, ?, ?, ?, ?)
            ''', ('1111111111', 'Test Tutor', 'Test Tuition Center', 'tutor', 1))
            tutor_id = cursor.lastrowid
            print(f"✓ Created tutor user (ID: {tutor_id})")
        
        # Create 3 batches
        batches_data = [
            {'name': 'Morning Batch', 'start_time': '09:00', 'end_time': '11:00'},
            {'name': 'Afternoon Batch', 'start_time': '14:00', 'end_time': '16:00'},
            {'name': 'Evening Batch', 'start_time': '18:00', 'end_time': '20:00'},
        ]
        
        batch_ids = []
        for batch_data in batches_data:
            cursor.execute('''
                INSERT INTO batches (name, description, start_time, end_time, user_id)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                batch_data['name'],
                f"{batch_data['name']} - Test batch",
                batch_data['start_time'],
                batch_data['end_time'],
                tutor_id
            ))
            batch_ids.append(cursor.lastrowid)
            print(f"✓ Created batch: {batch_data['name']} (ID: {cursor.lastrowid})")
        
        # Create 35 students distributed across batches
        first_names = ['Aarav', 'Aditi', 'Arjun', 'Ananya', 'Aryan', 'Diya', 'Ishaan', 'Kavya', 'Rohan', 'Saanvi',
                      'Vihaan', 'Zara', 'Advik', 'Anika', 'Dhruv', 'Ira', 'Krish', 'Meera', 'Neel', 'Pari',
                      'Reyansh', 'Sara', 'Ved', 'Yash', 'Aadhya', 'Arnav', 'Ishita', 'Kian', 'Myra', 'Reyan',
                      'Sia', 'Vivaan', 'Aarush', 'Anvi', 'Dev']
        
        last_names = ['Sharma', 'Patel', 'Kumar', 'Singh', 'Gupta', 'Verma', 'Reddy', 'Mehta', 'Joshi', 'Malik',
                     'Chopra', 'Agarwal', 'Nair', 'Rao', 'Iyer', 'Menon', 'Pillai', 'Nair', 'Krishnan', 'Nair']
        
        students_created = 0
        for i in range(35):
            first_name = first_names[i % len(first_names)]
            last_name = last_names[i % len(last_names)]
            name = f"{first_name} {last_name}"
            phone = f"9{100000000 + i:09d}"  # 9100000000, 9100000001, etc.
            batch_id = batch_ids[i % len(batch_ids)]  # Distribute across batches
            
            # Check if password column exists
            cursor.execute("PRAGMA table_info(students)")
            columns = [row[1] for row in cursor.fetchall()]
            has_password = 'password' in columns
            
            if has_password:
                # Generate password from last 4 digits of phone
                password = f"student{phone[-4:]}"
                password_hash = generate_password_hash(password)
                cursor.execute('''
                    INSERT INTO students (name, phone, batch_id, user_id, password, school_name, standard)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (name, phone, batch_id, tutor_id, password_hash, f"School {i % 5 + 1}", f"Class {i % 10 + 1}"))
            else:
                cursor.execute('''
                    INSERT INTO students (name, phone, batch_id, user_id, school_name, standard)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (name, phone, batch_id, tutor_id, f"School {i % 5 + 1}", f"Class {i % 10 + 1}"))
            
            students_created += 1
            if (i + 1) % 10 == 0:
                print(f"✓ Created {students_created} students...")
        
        print(f"✓ Created {students_created} students total")
        
        # Commit all changes
        conn.commit()
        
        print("\n" + "=" * 50)
        print("✅ Database populated successfully!")
        print("=" * 50)
        print(f"\nTest Data Summary:")
        print(f"  - Tutor: Mobile 1111111111")
        print(f"  - Batches: {len(batches_data)}")
        print(f"    • {batches_data[0]['name']}: {sum(1 for i in range(35) if i % 3 == 0)} students")
        print(f"    • {batches_data[1]['name']}: {sum(1 for i in range(35) if i % 3 == 1)} students")
        print(f"    • {batches_data[2]['name']}: {sum(1 for i in range(35) if i % 3 == 2)} students")
        print(f"  - Students: {students_created}")
        print(f"\nLogin Credentials:")
        print(f"  - Tutor: Mobile 1111111111, Password: (your password)")
        print(f"  - Students: Mobile 9100000000-9100000034, Password: studentXXXX (last 4 digits)")
        
    except Exception as e:
        print(f"Error populating database: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        conn.close()

def main():
    print("=" * 50)
    print("Database Clean and Populate Script")
    print("=" * 50)
    
    print("\n1. Cleaning database...")
    clean_database()
    
    print("\n2. Populating database with test data...")
    populate_database()
    
    print("\n" + "=" * 50)
    print("✅ Done!")
    print("=" * 50)

if __name__ == '__main__':
    main()

