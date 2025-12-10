#!/usr/bin/env python3
"""Script to clean all data from the database"""
import sqlite3
from config import Config
from database import get_db_connection

def clean_database():
    """Delete all data from all tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Disable foreign key constraints temporarily
        cursor.execute('PRAGMA foreign_keys = OFF')
        
        # Delete in order to respect foreign key constraints
        # 1. Delete attendance records (references students and users)
        cursor.execute('DELETE FROM attendance')
        attendance_count = cursor.rowcount
        print(f"✓ Deleted {attendance_count} attendance records")
        
        # 2. Delete homework records (references batches, students, users)
        cursor.execute('DELETE FROM homework')
        homework_count = cursor.rowcount
        print(f"✓ Deleted {homework_count} homework records")
        
        # 3. Delete students (references batches and users)
        cursor.execute('DELETE FROM students')
        students_count = cursor.rowcount
        print(f"✓ Deleted {students_count} student records")
        
        # 4. Delete batches (references users)
        cursor.execute('DELETE FROM batches')
        batches_count = cursor.rowcount
        print(f"✓ Deleted {batches_count} batch records")
        
        # 5. Delete users (optional - uncomment if you want to delete users too)
        # cursor.execute('DELETE FROM users')
        # users_count = cursor.rowcount
        # print(f"✓ Deleted {users_count} user records")
        
        # Re-enable foreign key constraints
        cursor.execute('PRAGMA foreign_keys = ON')
        
        # Commit changes
        conn.commit()
        
        print("\n✓ Database cleaned successfully!")
        print(f"  - Attendance: {attendance_count} records")
        print(f"  - Homework: {homework_count} records")
        print(f"  - Students: {students_count} records")
        print(f"  - Batches: {batches_count} records")
        print(f"  - Users: (kept - not deleted)")
        
    except Exception as e:
        conn.rollback()
        print(f"✗ Error cleaning database: {e}")
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    print("Cleaning database...")
    print(f"Database: {Config.DATABASE}\n")
    
    # Ask for confirmation
    response = input("Are you sure you want to delete ALL data? (yes/no): ")
    if response.lower() in ['yes', 'y']:
        clean_database()
    else:
        print("Operation cancelled.")

