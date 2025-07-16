import streamlit as st
import pandas as pd
import sqlite3
from datetime import date
from io import BytesIO

# DB connection
def create_connection():
    return sqlite3.connect("hris.db", check_same_thread=False)

# Add employee
def add_employee(full_name, department, role, email, phone, status, date_joined):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO employees (full_name, department, role, email, phone, status, date_joined)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (full_name, department, role, email, phone, status, date_joined))
    conn.commit()
    conn.close()

# Get all employees
def get_all_employees():
    conn = create_connection()
    df = pd.read_sql_query("SELECT * FROM employees", conn)
    conn.close()
    return df

# Update employee
def update_employee(emp_id, full_name, department, role, email, phone, status, date_joined):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE employees SET full_name=?, department=?, role=?, email=?, phone=?, status=?, date_joined=?
        WHERE id=?
    """, (full_name, department, role, email, phone, status, date_joined, emp_id))
    conn.commit()
    conn.close()

# Delete employee
def delete_employee(emp_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM employees WHERE id=?", (emp_id,))
    conn.commit()
    conn.close()

# Excel export helper
def to_excel_download(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Employees')
    return output.getvalue()

# Main interface
def show():
    st.title("👥 Employee Management")

    with st.expander("➕ Add New Employee", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            full_name = st.text_input("Full Name")
            department = st.selectbox("Department", ["HR", "Finance", "IT", "Marketing", "Operations"])
            role = st.text_input("Role/Position")
            date_joined = st.date_input("Date Joined", value=date.today())
        with col2:
            email = st.text_input("Email")
            phone = st.text_input("Phone Number")
            status = st.selectbox("Status", ["Active", "Inactive"])

        if st.button("Add Employee"):
            if full_name and email:
                add_employee(full_name, department, role, email, phone, status, date_joined.strftime("%Y-%m-%d"))
                st.success(f"{full_name} added successfully!")
                st.rerun()
            else:
                st.warning("Please provide at least Full Name and Email.")

    df = get_all_employees()

    st.markdown("### 📋 Employee List")
    with st.expander("🔍 Filter & Search", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            dept_filter = st.multiselect("Filter by Department", df["department"].unique())
            status_filter = st.multiselect("Filter by Status", df["status"].unique())
        with col2:
            search_query = st.text_input("Search by Name or Email")

        if dept_filter:
            df = df[df["department"].isin(dept_filter)]
        if status_filter:
            df = df[df["status"].isin(status_filter)]
        if search_query:
            df = df[df["full_name"].str.contains(search_query, case=False) | df["email"].str.contains(search_query, case=False)]

    st.dataframe(df, use_container_width=True)

    for i, row in df.iterrows():
        with st.expander(f"👤 {row['full_name']} ({row['role']})", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                new_name = st.text_input("Full Name", row["full_name"], key=f"name{i}")
                new_dept = st.selectbox("Department", ["HR", "Finance", "IT", "Marketing", "Operations"], index=["HR", "Finance", "IT", "Marketing", "Operations"].index(row["department"]), key=f"dept{i}")
                new_role = st.text_input("Role", row["role"], key=f"role{i}")
                new_date = st.date_input("Date Joined", pd.to_datetime(row["date_joined"]), key=f"date{i}")
            with col2:
                new_email = st.text_input("Email", row["email"], key=f"email{i}")
                new_phone = st.text_input("Phone", row["phone"], key=f"phone{i}")
                new_status = st.selectbox("Status", ["Active", "Inactive"], index=["Active", "Inactive"].index(row["status"]), key=f"status{i}")

            colA, colB = st.columns(2)
            with colA:
                if st.button("💾 Update", key=f"update{i}"):
                    update_employee(row["id"], new_name, new_dept, new_role, new_email, new_phone, new_status, new_date.strftime("%Y-%m-%d"))
                    st.success("Employee updated.")
                    st.rerun()
            with colB:
                if st.button("🗑️ Delete", key=f"delete{i}"):
                    delete_employee(row["id"])
                    st.error("Employee deleted.")
                    st.rerun()

    st.markdown("### 📤 Export Data")
    excel_file = to_excel_download(df)
    st.download_button(
        label="Download as Excel",
        data=excel_file,
        file_name="employee_list.xlsx",
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
