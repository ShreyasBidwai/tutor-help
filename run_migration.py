import sqlite3
from config import Config
import os

print(f"Database path: {Config.DATABASE}")
if not os.path.exists(Config.DATABASE):
    print("Database file not found!")
    exit(1)

conn = sqlite3.connect(Config.DATABASE)
cursor = conn.cursor()

try:
    cursor.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f"Columns before: {columns}")

    if 'password' in columns:
        print("Attempting to drop password column...")
        cursor.execute('ALTER TABLE users DROP COLUMN password')
        conn.commit()
        print("Dropped password column.")
    else:
        print("Password column not found.")

    cursor.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f"Columns after: {columns}")

except Exception as e:
    print(f"Error: {e}")
finally:
    conn.close()
