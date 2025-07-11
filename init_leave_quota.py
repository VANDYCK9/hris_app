import sqlite3

conn = sqlite3.connect("hris.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS leave_quota (
    employee_id INTEGER PRIMARY KEY,
    annual_quota INTEGER DEFAULT 20,
    FOREIGN KEY (employee_id) REFERENCES employees(id)
)
""")

conn.commit()
conn.close()

print("✅ leave_quota table created.")
