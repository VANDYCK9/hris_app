import sqlite3

conn = sqlite3.connect("hris.db")
cursor = conn.cursor()

# ✅ USERS table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'Employee',
    is_verified INTEGER DEFAULT 0,
    verification_code TEXT
)
""")

# ✅ EMPLOYEES table
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

# ✅ LEAVE QUOTA table
cursor.execute("""
CREATE TABLE IF NOT EXISTS leave_quota (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    annual_quota INTEGER DEFAULT 20,
    used_days INTEGER DEFAULT 0,
    FOREIGN KEY(employee_id) REFERENCES employees(id)
)
""")

# ✅ LEAVE REQUESTS table
cursor.execute("""
CREATE TABLE IF NOT EXISTS leave_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    leave_type TEXT,
    start_date TEXT,
    end_date TEXT,
    status TEXT DEFAULT 'Pending',
    FOREIGN KEY(employee_id) REFERENCES employees(id)
)
""")

# ✅ SALARY BASE table
cursor.execute("""
CREATE TABLE IF NOT EXISTS salary_base (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    base_salary REAL NOT NULL,
    FOREIGN KEY(employee_id) REFERENCES employees(id)
)
""")

# ✅ PAYROLL RECORDS (main table)
cursor.execute("""
CREATE TABLE IF NOT EXISTS payroll_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    month TEXT NOT NULL,
    base_salary REAL NOT NULL,
    bonus REAL DEFAULT 0,
    deductions REAL DEFAULT 0,
    net_salary REAL NOT NULL,
    generated_on TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(employee_id) REFERENCES employees(id)
)
""")

# ✅ LEGACY PAYROLL TABLE (for older modules)
cursor.execute("""
CREATE TABLE IF NOT EXISTS payroll (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    month TEXT NOT NULL,
    base_salary REAL NOT NULL,
    bonus REAL DEFAULT 0,
    deductions REAL DEFAULT 0,
    net_salary REAL NOT NULL,
    generated_on TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(employee_id) REFERENCES employees(id)
)
""")

# ✅ ATTENDANCE table
cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    status TEXT DEFAULT 'Present',
    FOREIGN KEY(employee_id) REFERENCES employees(id)
)
""")

# ✅ UPGRADE ATTENDANCE table with check_in/check_out if missing
try:
    cursor.execute("ALTER TABLE attendance ADD COLUMN check_in TEXT")
    print("✅ Added check_in column")
except:
    print("ℹ️ check_in already exists")

try:
    cursor.execute("ALTER TABLE attendance ADD COLUMN check_out TEXT")
    print("✅ Added check_out column")
except:
    print("ℹ️ check_out already exists")

conn.commit()
conn.close()

print("✅ All HRIS tables created/upgraded successfully (with all missing columns)!")
