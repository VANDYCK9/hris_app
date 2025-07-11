import sqlite3

conn = sqlite3.connect("hris.db")
cursor = conn.cursor()

# Create payroll table
cursor.execute("""
CREATE TABLE IF NOT EXISTS payroll (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER,
    base_salary REAL,
    bonus REAL DEFAULT 0,
    deduction REAL DEFAULT 0,
    pay_month TEXT,
    generated_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(id)
)
""")

# Optional: Create base salary table (editable anytime)
cursor.execute("""
CREATE TABLE IF NOT EXISTS salary_base (
    employee_id INTEGER PRIMARY KEY,
    monthly_salary REAL NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES employees(id)
)
""")

conn.commit()
conn.close()

print("✅ Payroll and base salary tables created.")
