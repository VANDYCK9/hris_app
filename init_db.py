import sqlite3

# Connect to SQLite database (creates hris.db if it doesn't exist)
conn = sqlite3.connect('hris.db')
cursor = conn.cursor()

# Create employees table
cursor.execute("""
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    department TEXT,
    role TEXT,
    email TEXT,
    phone TEXT,
    status TEXT CHECK(status IN ('Active', 'Inactive')) DEFAULT 'Active',
    date_joined TEXT
)
""")

conn.commit()
conn.close()

print("✅ Database and employees table created successfully.")
