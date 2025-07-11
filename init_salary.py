import sqlite3

conn = sqlite3.connect("hris.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS salary_base (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER UNIQUE,
    monthly_salary REAL NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES employees(id)
)
""")

conn.commit()
conn.close()

print("✅ salary_base table created.")
