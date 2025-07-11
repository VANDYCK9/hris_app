import streamlit as st
import sqlite3
import pandas as pd
from io import BytesIO

# DB connection
def create_connection():
    return sqlite3.connect("hris.db", check_same_thread=False)

# Get all employees and their salary
def get_employee_salaries():
    conn = create_connection()
    df = pd.read_sql_query("""
        SELECT e.id AS employee_id, e.full_name, e.department,
               s.monthly_salary
        FROM employees e
        LEFT JOIN salary_base s ON e.id = s.employee_id
        ORDER BY e.full_name
    """, conn)
    conn.close()
    return df

# Add or update salary
def update_salary(employee_id, salary):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO salary_base (employee_id, monthly_salary)
        VALUES (?, ?)
        ON CONFLICT(employee_id) DO UPDATE SET monthly_salary = excluded.monthly_salary
    """, (employee_id, salary))
    conn.commit()
    conn.close()

# Export helper
def to_excel_download(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Salaries")
    return output.getvalue()

# Main UI
def show():
    st.title("💰 Payroll Manager - Set Base Salaries")

    df = get_employee_salaries()

    with st.expander("🔍 Filter", expanded=True):
        name_filter = st.text_input("Search by name")
        dept_filter = st.multiselect("Filter by Department", df["department"].unique())

        if name_filter:
            df = df[df["full_name"].str.contains(name_filter, case=False)]
        if dept_filter:
            df = df[df["department"].isin(dept_filter)]

    st.markdown("### ✏️ Edit Monthly Salaries")
    for i, row in df.iterrows():
        with st.expander(f"{row['full_name']} ({row['department']})", expanded=False):
            current = float(row["monthly_salary"]) if pd.notnull(row["monthly_salary"]) else 0.00
            new_salary = st.number_input("Monthly Salary (GHS)", min_value=0.00, max_value=100000.00, value=current, step=100.0, key=f"sal_{i}")
            if st.button("💾 Save", key=f"save_{i}"):
                update_salary(row["employee_id"], new_salary)
                st.success(f"{row['full_name']}'s salary updated to GHS {new_salary:,.2f}")
                st.rerun()

    st.markdown("### 📤 Export Salary Data")
    excel = to_excel_download(df)
    st.download_button(
        label="Download as Excel",
        data=excel,
        file_name="employee_salaries.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
