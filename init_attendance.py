import sqlite3

conn = sqlite3.connect("hris.db")
cursor = conn.cursor()

# ✅ Add check_in column if missing
try:
    cursor.execute("ALTER TABLE attendance ADD COLUMN check_in TEXT")
    print("✅ Added check_in column")
except:
    print("ℹ️ check_in column already exists")

# ✅ Add check_out column if missing
try:
    cursor.execute("ALTER TABLE attendance ADD COLUMN check_out TEXT")
    print("✅ Added check_out column")
except:
    print("ℹ️ check_out column already exists")

conn.commit()
conn.close()

print("✅ attendance table upgraded successfully!")
