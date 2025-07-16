import sqlite3

conn = sqlite3.connect("hris.db")
cursor = conn.cursor()

# ✅ Create leave_quota table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS leave_quota (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    annual_quota INTEGER DEFAULT 20,
    used_days INTEGER DEFAULT 0,
    FOREIGN KEY(employee_id) REFERENCES employees(id)
)
""")

conn.commit()
conn.close()

print("✅ leave_quota table created successfully!")
