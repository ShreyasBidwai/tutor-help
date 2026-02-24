"""CLI script to create an admin user for the TuitionTrack superadmin dashboard"""
import argparse
from werkzeug.security import generate_password_hash
from database import get_db_connection

def create_admin(username, password, name=None):
    """Create a new admin user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if admin already exists
    cursor.execute('SELECT id FROM admins WHERE username = ?', (username,))
    if cursor.fetchone():
        print(f"Admin '{username}' already exists.")
        conn.close()
        return
    
    password_hash = generate_password_hash(password)
    cursor.execute(
        'INSERT INTO admins (username, password_hash, name) VALUES (?, ?, ?)',
        (username, password_hash, name or username)
    )
    conn.commit()
    conn.close()
    print(f"Admin '{username}' created successfully!")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create an admin user')
    parser.add_argument('--username', required=True, help='Admin username')
    parser.add_argument('--password', required=True, help='Admin password')
    parser.add_argument('--name', help='Admin display name (optional)')
    args = parser.parse_args()
    
    create_admin(args.username, args.password, args.name)
