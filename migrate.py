import sqlite3
import os
import shutil
from datetime import datetime

DATABASE = 'tutor.db'

def migrate():
    if not os.path.exists(DATABASE):
        print(f"Database {DATABASE} does not exist.")
        return

    # Backup the database before migrating
    backup_file = f"tutor_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    shutil.copy2(DATABASE, backup_file)
    print(f"Backed up database to {backup_file}")

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        # Step 1: Batches table migration (add UNIQUE(user_id, name))
        print("Migrating batches table...")
        
        # Check for duplicate batches before creating unique constraint
        cursor.execute('''
            SELECT user_id, name, COUNT(*) as count 
            FROM batches 
            GROUP BY user_id, name 
            HAVING count > 1
        ''')
        duplicates = cursor.fetchall()
        if duplicates:
            print(f"Found {len(duplicates)} duplicate batch names for same users. Cleaning...")
            for dup in duplicates:
                cursor.execute('''
                    DELETE FROM batches 
                    WHERE id NOT IN (
                        SELECT MIN(id) FROM batches 
                        WHERE user_id = ? AND name = ?
                    ) AND user_id = ? AND name = ?
                ''', (dup['user_id'], dup['name'], dup['user_id'], dup['name']))
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS batches_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            start_time TEXT,
            end_time TEXT,
            days TEXT,
            notifications_enabled INTEGER DEFAULT 1,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            UNIQUE(user_id, name)
        )
        ''')
        cursor.execute('INSERT INTO batches_new SELECT * FROM batches')
        cursor.execute('DROP TABLE batches')
        cursor.execute('ALTER TABLE batches_new RENAME TO batches')
        
        # Re-create indexes for batches
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_batches_user_id ON batches(user_id)")


        # Step 2: Students table migration (Global phone uniqueness)
        print("Migrating students table...")
        
        # Cleanup duplicate phones globally
        cursor.execute('''
            SELECT phone, COUNT(*) as count 
            FROM students 
            GROUP BY phone 
            HAVING count > 1
        ''')
        duplicates = cursor.fetchall()
        if duplicates:
            print(f"Found {len(duplicates)} duplicate phone numbers globally. Cleaning...")
            for dup in duplicates:
                cursor.execute('''
                    DELETE FROM students 
                    WHERE id NOT IN (
                        SELECT MIN(id) FROM students 
                        WHERE phone = ?
                    ) AND phone = ?
                ''', (dup['phone'], dup['phone']))
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS students_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL UNIQUE,
            batch_id INTEGER NOT NULL,
            address TEXT,
            school_name TEXT,
            standard TEXT,
            user_id INTEGER NOT NULL,
            last_attendance_notification TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            password TEXT,
            password_hash TEXT,
            FOREIGN KEY (batch_id) REFERENCES batches (id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
        ''')
        cursor.execute('INSERT INTO students_new SELECT * FROM students')
        cursor.execute('DROP TABLE students')
        cursor.execute('ALTER TABLE students_new RENAME TO students')

        # Re-create indexes for students
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_students_user_id ON students(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_students_batch_id ON students(batch_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_students_phone ON students(phone)")

        # Step 3: Attendance table migration (ON DELETE CASCADE, Drop present column)
        print("Migrating attendance table...")
        # Ensure status is populated if present has a value
        cursor.execute('UPDATE attendance SET status = COALESCE(status, present, 1)')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            date DATE NOT NULL,
            status INTEGER DEFAULT 1,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            UNIQUE(student_id, date)
        )
        ''')
        cursor.execute('''
            INSERT INTO attendance_new (id, student_id, date, status, user_id, created_at) 
            SELECT id, student_id, date, status, user_id, created_at FROM attendance
        ''')
        cursor.execute('DROP TABLE attendance')
        cursor.execute('ALTER TABLE attendance_new RENAME TO attendance')
        
        # Re-create indexes for attendance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_attendance_user_id ON attendance(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_attendance_student_id ON attendance(student_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_attendance_date ON attendance(date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_attendance_user_date ON attendance(user_id, date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_attendance_user_date_status ON attendance(user_id, date, status)")

        # Step 4: Homework table migration (ON DELETE CASCADE)
        print("Migrating homework table...")
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS homework_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            content TEXT,
            batch_id INTEGER,
            student_id INTEGER,
            file_path TEXT,
            youtube_url TEXT,
            submission_date DATE,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (batch_id) REFERENCES batches (id) ON DELETE CASCADE,
            FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
        ''')
        cursor.execute('INSERT INTO homework_new SELECT * FROM homework')
        cursor.execute('DROP TABLE homework')
        cursor.execute('ALTER TABLE homework_new RENAME TO homework')
        
        # Re-create indexes for homework
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_homework_user_id ON homework(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_homework_batch_id ON homework(batch_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_homework_student_id ON homework(student_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_homework_submission_date ON homework(submission_date)")

        conn.commit()
        print("Migration completed successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"Migration failed: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
