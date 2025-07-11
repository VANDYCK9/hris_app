import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from io import BytesIO

def create_connection():
    return sqlite3.connect("hris.db", check_same_thread=False)

def get_employees():
    conn = create_connection()
    df = pd.read_sql_query("""
        SELECT e.id AS employee_id, e.full_name, e.department,
               COALESCE(s.monthly_salary, 0) AS base_salary
        FROM employees e
        LEFT JOIN salary_base s ON e.id = s.employee_id
        ORDER BY e.full_name
    """, conn)
    conn.close()
    return df

def save_payslip(emp_id, base, bonus, deduct, month):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO payroll (employee_id, base_salary, bonus, deduction, pay_month)
        VALUES (?, ?, ?, ?, ?)
    """, (emp_id, base, bonus, deduct, month))
    conn.commit()
    conn.close()

def get_payroll_for_month(month):
    conn = create_connection()
    df = pd.read_sql_query("""
        SELECT e.full_name, e.department,
               p.base_salary, p.bonus, p.deduction,
               (p.base_salary + p.bonus - p.deduction) AS net_pay,
               p.pay_month, p.generated_on
        FROM payroll p
        JOIN employees e ON p.employee_id = e.id
        WHERE p.pay_month = ?
        ORDER BY e.full_name
    """, conn, params=(month,))
    conn.close()
    return df

def to_excel_download(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Payroll")
    return output.getvalue()

def show():
    st.title("🧾 Monthly Payroll Generator")

    emp_df = get_employees()

    if emp_df.empty:
        st.warning("⚠️ No employees with base salary found. Please set salaries in Payroll Manager first.")
        return

    emp_names = emp_df["full_name"].tolist()

    with st.form("payslip_form"):
        st.subheader("➕ Generate Payslip")

        selected_name = st.selectbox("Select Employee", emp_names)
        selected = emp_df[emp_df["full_name"] == selected_name].iloc[0]
        base_salary = float(selected["base_salary"])

        st.write(f"💰 Base Salary: GHS {base_salary:,.2f}")

        bonus = st.number_input("Bonus (optional)", min_value=0.0, step=100.0)
        deduction = st.number_input("Deduction (optional)", min_value=0.0, step=50.0)

        pay_month = st.selectbox("Pay Month", [
            datetime.now().strftime("%B %Y"),
            "January 2025", "February 2025", "March 2025",
            "April 2025", "May 2025", "June 2025", "July 2025",
            "August 2025", "September 2025", "October 2025",
            "November 2025", "December 2025"
        ])

        submitted = st.form_submit_button("✅ Generate Payslip")

        if submitted:
            st.write("🛠 DEBUG: Submit button was clicked.")
            try:
                save_payslip(selected["employee_id"], base_salary, bonus, deduction, pay_month)
                st.success(f"✅ Payslip for {selected_name} added for {pay_month}.")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error while saving payslip: {e}")

    st.markdown("### 📊 View Generated Payroll")
    month_filter = st.selectbox("📅 Select Month to View", [
        datetime.now().strftime("%B %Y"),
        "January 2025", "February 2025", "March 2025",
        "April 2025", "May 2025", "June 2025", "July 2025",
        "August 2025", "September 2025", "October 2025",
        "November 2025", "December 2025"
    ])

    df = get_payroll_for_month(month_filter)
    if df.empty:
        st.warning("No payroll generated for selected month.")
    else:
        st.dataframe(df, use_container_width=True)
        excel = to_excel_download(df)
        st.download_button("📥 Export Payroll to Excel", data=excel, file_name=f"payroll_{month_filter}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
