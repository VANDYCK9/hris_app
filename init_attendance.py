import sqlite3

# Connect to the HRIS database
conn = sqlite3.connect("hris.db")
cursor = conn.cursor()

# Create attendance table
cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    check_in TEXT,
    check_out TEXT,
    remarks TEXT,
    FOREIGN KEY (employee_id) REFERENCES employees(id)
)
""")

conn.commit()
conn.close()

print("✅ attendance table created.")
