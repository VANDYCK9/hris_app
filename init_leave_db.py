import sqlite3

conn = sqlite3.connect("hris.db")
cursor = conn.cursor()

# Create leave_requests table
cursor.execute("""
CREATE TABLE IF NOT EXISTS leave_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER,
    leave_type TEXT,
    start_date TEXT,
    end_date TEXT,
    reason TEXT,
    status TEXT CHECK(status IN ('Pending', 'Approved', 'Rejected')) DEFAULT 'Pending',
    FOREIGN KEY (employee_id) REFERENCES employees(id)
)
""")

conn.commit()
conn.close()

print("✅ leave_requests table created successfully.")
