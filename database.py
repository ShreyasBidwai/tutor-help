"""Database connection and initialization"""
import sqlite3
import os
import time
from config import Config

def get_db_connection(timeout=20.0):
    """Get database connection with WAL mode and optimizations for better concurrency"""
    conn = sqlite3.connect(Config.DATABASE, timeout=timeout)
    conn.row_factory = sqlite3.Row
    
    # Enable WAL mode for better concurrency (readers don't block writers)
    # This allows multiple concurrent readers and one writer
    try:
        conn.execute('PRAGMA journal_mode=WAL')
    except sqlite3.OperationalError:
        # If WAL mode fails (e.g., on read-only filesystem), continue with default mode
        pass
    
    # Optimize for better performance
    try:
        conn.execute('PRAGMA synchronous=NORMAL')  # Faster than FULL, still safe
        conn.execute('PRAGMA cache_size=-64000')  # 64MB cache (adjust based on available RAM)
        conn.execute('PRAGMA temp_store=MEMORY')  # Store temp tables in memory
        conn.execute('PRAGMA mmap_size=268435456')  # 256MB memory-mapped I/O
        conn.execute('PRAGMA foreign_keys=ON')  # Ensure foreign keys are enabled
    except sqlite3.OperationalError:
        # If any PRAGMA fails, continue (some may not be supported in all SQLite versions)
        pass
    
    return conn

def execute_with_retry(conn, query, params=None, max_retries=3, retry_delay=0.1):
    """
    Execute query with retry logic for database locked errors.
    Useful for write operations that may encounter temporary locks.
    
    Args:
        conn: Database connection
        query: SQL query string
        params: Query parameters (optional)
        max_retries: Maximum number of retry attempts
        retry_delay: Initial delay between retries (increases exponentially)
    
    Returns:
        Cursor object
    """
    cursor = conn.cursor()
    for attempt in range(max_retries):
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e).lower() and attempt < max_retries - 1:
                # Exponential backoff: wait longer with each retry
                wait_time = retry_delay * (2 ** attempt)
                time.sleep(wait_time)
                continue
            # Re-raise if not a lock error or if we've exhausted retries
            raise
    return cursor

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
            onboarding_completed INTEGER DEFAULT 0,
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
            last_attendance_notification TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (batch_id) REFERENCES batches (id),
            FOREIGN KEY (user_id) REFERENCES users (id),
            UNIQUE(user_id, phone)
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
    
    if 'last_attendance_notification' not in columns:
        try:
            cursor.execute('ALTER TABLE students ADD COLUMN last_attendance_notification TIMESTAMP')
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
    
    if 'onboarding_completed' not in user_columns:
        try:
            cursor.execute('ALTER TABLE users ADD COLUMN onboarding_completed INTEGER DEFAULT 0')
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
    
    # Add unique constraint for students (user_id, phone) if migrating
    try:
        # Check if index already exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_students_user_phone'")
        if not cursor.fetchone():
            # Check for existing duplicates before adding constraint
            cursor.execute('''
                SELECT user_id, phone, COUNT(*) as count
                FROM students
                GROUP BY user_id, phone
                HAVING count > 1
            ''')
            duplicates = cursor.fetchall()
            
            if duplicates:
                # Keep first occurrence, delete rest
                for dup in duplicates:
                    cursor.execute('''
                        DELETE FROM students
                        WHERE id NOT IN (
                            SELECT MIN(id) FROM students
                            WHERE user_id = ? AND phone = ?
                        )
                        AND user_id = ? AND phone = ?
                    ''', (dup[0], dup[1], dup[0], dup[1]))
                import logging
                logging.warning(f"Cleaned {len(duplicates)} duplicate phone numbers during migration")
            
            # Create unique index
            cursor.execute('''
                CREATE UNIQUE INDEX IF NOT EXISTS idx_students_user_phone 
                ON students(user_id, phone)
            ''')
    except sqlite3.OperationalError:
        # Index might already exist, ignore
        pass
    
    conn.commit()
    conn.close()

def add_indexes():
    """Add performance indexes to database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    indexes = [
        # Students table indexes
        "CREATE INDEX IF NOT EXISTS idx_students_user_id ON students(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_students_batch_id ON students(batch_id)",
        "CREATE INDEX IF NOT EXISTS idx_students_phone ON students(phone)",
        
        # Attendance table indexes
        "CREATE INDEX IF NOT EXISTS idx_attendance_user_id ON attendance(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_attendance_student_id ON attendance(student_id)",
        "CREATE INDEX IF NOT EXISTS idx_attendance_date ON attendance(date)",
        "CREATE INDEX IF NOT EXISTS idx_attendance_user_date ON attendance(user_id, date)",
        
        # Batches table indexes
        "CREATE INDEX IF NOT EXISTS idx_batches_user_id ON batches(user_id)",
        
        # Homework table indexes
        "CREATE INDEX IF NOT EXISTS idx_homework_user_id ON homework(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_homework_batch_id ON homework(batch_id)",
        "CREATE INDEX IF NOT EXISTS idx_homework_student_id ON homework(student_id)",
        "CREATE INDEX IF NOT EXISTS idx_homework_submission_date ON homework(submission_date)",
        
        # Users table indexes
        "CREATE INDEX IF NOT EXISTS idx_users_mobile ON users(mobile)",
    ]
    
    for index_sql in indexes:
        try:
            cursor.execute(index_sql)
        except sqlite3.OperationalError:
            # Index might already exist, ignore
            pass
    
    conn.commit()
    conn.close()

# Initialize database on import
if not os.path.exists(Config.DATABASE):
    init_db()
    add_indexes()
else:
    migrate_db()
    add_indexes()

