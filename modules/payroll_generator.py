import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

def create_connection():
    return sqlite3.connect("hris.db")

def get_employees():
    conn = create_connection()
    df = pd.read_sql_query("""
        SELECT e.id AS employee_id, e.full_name, e.department,
               COALESCE(s.base_salary, 0) AS base_salary
        FROM employees e
        LEFT JOIN salary_base s ON e.id = s.employee_id
        ORDER BY e.full_name
    """, conn)
    conn.close()
    return df

def save_payroll_record(emp_id, month, base_salary, bonus, deductions, net_salary):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO payroll_records (employee_id, month, base_salary, bonus, deductions, net_salary, generated_on)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (emp_id, month, base_salary, bonus, deductions, net_salary, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()

    # Also insert into legacy payroll table for backward compatibility
    cursor.execute("""
        INSERT INTO payroll (employee_id, month, base_salary, bonus, deductions, net_salary, generated_on)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (emp_id, month, base_salary, bonus, deductions, net_salary, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    conn.commit()
    conn.close()

def show():
    st.header("🧾 Payroll Generator")
    st.write("Generate payslips for employees based on base salary, bonuses, and deductions.")

    df = get_employees()

    if df.empty:
        st.warning("⚠️ No employees found! Please add employees first.")
        return

    st.subheader("Select Employee")
    employee_names = df["full_name"].tolist()
    employee_map = dict(zip(df["full_name"], df["employee_id"]))
    selected_employee = st.selectbox("Employee", employee_names)

    emp_row = df[df["full_name"] == selected_employee].iloc[0]
    base_salary = emp_row["base_salary"]

    st.write(f"💼 **Department:** {emp_row['department']}")
    st.write(f"💰 **Base Salary:** {base_salary:.2f}")

    month = st.selectbox("Select Month", [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ])

    bonus = st.number_input("Bonus", value=0.0, step=100.0)
    deductions = st.number_input("Deductions", value=0.0, step=100.0)
    net_salary = base_salary + bonus - deductions

    st.write(f"### ✅ Net Salary: {net_salary:.2f}")

    if st.button("✅ Generate Payslip"):
        emp_id = employee_map[selected_employee]
        save_payroll_record(emp_id, month, base_salary, bonus, deductions, net_salary)
        st.success(f"✅ Payslip generated for {selected_employee} ({month})")
        st.rerun()
