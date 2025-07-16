import sqlite3
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Connect to the database
conn = sqlite3.connect("hris.db")
cursor = conn.cursor()

# Create users table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'Employee'
)
""")

# Default admin account
default_admin_user = "admin"
default_admin_pass = "admin123"  # You can change this later

cursor.execute("SELECT * FROM users WHERE username=?", (default_admin_user,))
if cursor.fetchone() is None:
    cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                   (default_admin_user, hash_password(default_admin_pass), "Admin"))
    print(f"✅ Default admin created → Username: {default_admin_user} | Password: {default_admin_pass}")
else:
    print("✅ Admin account already exists.")

conn.commit()
conn.close()

print("✅ users table initialized.")
