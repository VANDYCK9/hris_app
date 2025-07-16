import streamlit as st
import sqlite3
import pandas as pd

def create_connection():
    return sqlite3.connect("hris.db")

def get_employee_salaries():
    conn = create_connection()
    df = pd.read_sql_query("""
        SELECT e.id AS employee_id, e.full_name, e.department,
               s.base_salary
        FROM employees e
        LEFT JOIN salary_base s ON e.id = s.employee_id
        ORDER BY e.full_name
    """, conn)
    conn.close()
    return df

def save_salary(employee_id, base_salary):
    conn = create_connection()
    cursor = conn.cursor()
    
    # Check if salary already exists for this employee
    cursor.execute("SELECT id FROM salary_base WHERE employee_id=?", (employee_id,))
    exists = cursor.fetchone()
    
    if exists:
        cursor.execute("UPDATE salary_base SET base_salary=? WHERE employee_id=?", 
                       (base_salary, employee_id))
    else:
        cursor.execute("INSERT INTO salary_base (employee_id, base_salary) VALUES (?, ?)", 
                       (employee_id, base_salary))
    
    conn.commit()
    conn.close()

def show():
    st.header("💰 Payroll Manager")
    st.write("Manage and assign base salaries to employees.")

    df = get_employee_salaries()

    if df.empty:
        st.warning("⚠️ No employees found! Please add employees first.")
        return

    # Show salary table
    st.subheader("📄 Current Salary Setup")
    st.dataframe(df)

    # Select employee to update salary
    st.subheader("➕ Add / Update Employee Salary")
    employee_names = df["full_name"].tolist()
    employee_map = dict(zip(df["full_name"], df["employee_id"]))

    selected_employee = st.selectbox("Select Employee", employee_names)
    current_salary = df[df["full_name"] == selected_employee]["base_salary"].values[0]

    new_salary = st.number_input(
        "Enter Base Salary (Monthly)",
        value=float(current_salary) if pd.notna(current_salary) else 0.0,
        step=100.0
    )

    if st.button("✅ Save Salary"):
        emp_id = employee_map[selected_employee]
        save_salary(emp_id, new_salary)
        st.success(f"✅ Salary updated for {selected_employee}")
        st.rerun()  # refresh page to show updated table
