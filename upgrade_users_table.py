import sqlite3

conn = sqlite3.connect("hris.db")
cursor = conn.cursor()

# Add missing columns safely
try:
    cursor.execute("ALTER TABLE users ADD COLUMN email TEXT")
    print("✅ Added email column")
except:
    print("ℹ️ email column already exists")

try:
    cursor.execute("ALTER TABLE users ADD COLUMN is_verified INTEGER DEFAULT 0")
    print("✅ Added is_verified column")
except:
    print("ℹ️ is_verified column already exists")

try:
    cursor.execute("ALTER TABLE users ADD COLUMN verification_code TEXT")
    print("✅ Added verification_code column")
except:
    print("ℹ️ verification_code column already exists")

conn.commit()
conn.close()
print("✅ users table upgraded successfully!")
