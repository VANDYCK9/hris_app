import sqlite3

conn = sqlite3.connect("hris.db")
cursor = conn.cursor()

# ✅ Create employees table if missing, or ensure correct structure
cursor.execute("""
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    department TEXT,
    role TEXT,
    email TEXT,
    phone TEXT,
    hire_date TEXT
)
""")

conn.commit()
conn.close()
print("✅ employees table created or already correct.")
