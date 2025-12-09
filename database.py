"""Database connection and initialization"""
import sqlite3
import os
from config import Config

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(Config.DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with required tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mobile TEXT UNIQUE NOT NULL,
            tutor_name TEXT,
            tuition_name TEXT,
            address TEXT,
            role TEXT DEFAULT 'tutor',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Batches table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS batches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            start_time TEXT,
            end_time TEXT,
            days TEXT,
            notifications_enabled INTEGER DEFAULT 1,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Students table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            batch_id INTEGER NOT NULL,
            address TEXT,
            school_name TEXT,
            standard TEXT,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (batch_id) REFERENCES batches (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Add new columns to existing students table if they don't exist
    try:
        cursor.execute('ALTER TABLE students ADD COLUMN address TEXT')
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    try:
        cursor.execute('ALTER TABLE students ADD COLUMN school_name TEXT')
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    try:
        cursor.execute('ALTER TABLE students ADD COLUMN standard TEXT')
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    # Attendance table
    # status: 0 = absent, 1 = present, 2 = late
    # Note: For backward compatibility, we support both 'present' and 'status' columns
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            date DATE NOT NULL,
            present INTEGER DEFAULT 1,
            status INTEGER DEFAULT 1,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students (id),
            FOREIGN KEY (user_id) REFERENCES users (id),
            UNIQUE(student_id, date)
        )
    ''')
    
    # Homework table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS homework (
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
            FOREIGN KEY (batch_id) REFERENCES batches (id),
            FOREIGN KEY (student_id) REFERENCES students (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def migrate_db():
    """Migrate existing database to add new columns"""
    if not os.path.exists(Config.DATABASE):
        return
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if columns exist and add them if they don't
    cursor.execute("PRAGMA table_info(students)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'address' not in columns:
        try:
            cursor.execute('ALTER TABLE students ADD COLUMN address TEXT')
        except sqlite3.OperationalError:
            pass
    
    if 'school_name' not in columns:
        try:
            cursor.execute('ALTER TABLE students ADD COLUMN school_name TEXT')
        except sqlite3.OperationalError:
            pass
    
    if 'standard' not in columns:
        try:
            cursor.execute('ALTER TABLE students ADD COLUMN standard TEXT')
        except sqlite3.OperationalError:
            pass
    
    # Migrate users table: add tuition_name and role columns
    cursor.execute("PRAGMA table_info(users)")
    user_columns = [row[1] for row in cursor.fetchall()]
    
    if 'tutor_name' not in user_columns:
        try:
            cursor.execute('ALTER TABLE users ADD COLUMN tutor_name TEXT')
        except sqlite3.OperationalError:
            pass
    
    if 'tuition_name' not in user_columns:
        try:
            cursor.execute('ALTER TABLE users ADD COLUMN tuition_name TEXT')
        except sqlite3.OperationalError:
            pass
    
    if 'address' not in user_columns:
        try:
            cursor.execute('ALTER TABLE users ADD COLUMN address TEXT')
        except sqlite3.OperationalError:
            pass
    
    if 'role' not in user_columns:
        try:
            cursor.execute('ALTER TABLE users ADD COLUMN role TEXT DEFAULT \'tutor\'')
        except sqlite3.OperationalError:
            pass
    
    # Migrate batches table: add start_time, end_time, days columns
    cursor.execute("PRAGMA table_info(batches)")
    batch_columns = [row[1] for row in cursor.fetchall()]
    
    if 'start_time' not in batch_columns:
        try:
            cursor.execute('ALTER TABLE batches ADD COLUMN start_time TEXT')
        except sqlite3.OperationalError:
            pass
    
    if 'end_time' not in batch_columns:
        try:
            cursor.execute('ALTER TABLE batches ADD COLUMN end_time TEXT')
        except sqlite3.OperationalError:
            pass
    
    if 'days' not in batch_columns:
        try:
            cursor.execute('ALTER TABLE batches ADD COLUMN days TEXT')
        except sqlite3.OperationalError:
            pass
    
    if 'notifications_enabled' not in batch_columns:
        try:
            cursor.execute('ALTER TABLE batches ADD COLUMN notifications_enabled INTEGER DEFAULT 1')
        except sqlite3.OperationalError:
            pass
    
    # Migrate homework table: update columns
    cursor.execute("PRAGMA table_info(homework)")
    homework_columns = [row[1] for row in cursor.fetchall()]
    
    if 'content' not in homework_columns:
        try:
            cursor.execute('ALTER TABLE homework ADD COLUMN content TEXT')
        except sqlite3.OperationalError:
            pass
    
    if 'file_path' not in homework_columns:
        try:
            cursor.execute('ALTER TABLE homework ADD COLUMN file_path TEXT')
        except sqlite3.OperationalError:
            pass
    
    if 'youtube_url' not in homework_columns:
        try:
            cursor.execute('ALTER TABLE homework ADD COLUMN youtube_url TEXT')
        except sqlite3.OperationalError:
            pass
    
    if 'submission_date' not in homework_columns:
        try:
            cursor.execute('ALTER TABLE homework ADD COLUMN submission_date DATE')
        except sqlite3.OperationalError:
            pass
    
    # Migrate attendance table: add 'status' column if needed
    cursor.execute("PRAGMA table_info(attendance)")
    attendance_columns = [row[1] for row in cursor.fetchall()]
    
    if 'status' not in attendance_columns:
        try:
            # Add status column and migrate data from present column
            cursor.execute('ALTER TABLE attendance ADD COLUMN status INTEGER DEFAULT 1')
            cursor.execute('UPDATE attendance SET status = COALESCE(present, 1) WHERE status IS NULL')
            # Note: SQLite doesn't support DROP COLUMN, so we'll keep both for backward compatibility
            # In practice, we'll use 'status' going forward
        except sqlite3.OperationalError:
            pass
    
    conn.commit()
    conn.close()

# Initialize database on import
if not os.path.exists(Config.DATABASE):
    init_db()
else:
    migrate_db()

