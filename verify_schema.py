import sqlite3
from config import Config

def check_schema():
    conn = sqlite3.connect(Config.DATABASE)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f"Users table columns: {columns}")
    
    if 'email' in columns:
        print("SUCCESS: 'email' column found.")
    else:
        print("FAILURE: 'email' column NOT found.")
    conn.close()

if __name__ == "__main__":
    check_schema()
