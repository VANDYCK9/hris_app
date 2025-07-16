import streamlit as st
import sqlite3
import pandas as pd
from io import BytesIO

# DB connection
def create_connection():
    return sqlite3.connect("hris.db", check_same_thread=False)

# Fetch all employee info and quotas
def get_employee_quotas():
    conn = create_connection()
    df = pd.read_sql_query("""
        SELECT e.id AS employee_id, e.full_name, e.department,
               q.annual_quota
        FROM employees e
        LEFT JOIN leave_quota q ON e.id = q.employee_id
        ORDER BY e.full_name
    """, conn)
    conn.close()
    return df

# Set or update quota
def update_quota(employee_id, quota):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO leave_quota (employee_id, annual_quota)
        VALUES (?, ?)
        ON CONFLICT(employee_id) DO UPDATE SET annual_quota=excluded.annual_quota
    """, (employee_id, quota))
    conn.commit()
    conn.close()

# Excel export
def to_excel_download(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Quotas")
    return output.getvalue()

# Main UI
def show():
    st.title("🛠️ Leave Quota Manager")

    df = get_employee_quotas()

    with st.expander("🔍 Filter", expanded=True):
        name_filter = st.text_input("Search by name")
        dept_filter = st.multiselect("Filter by Department", df["department"].unique())

        if name_filter:
            df = df[df["full_name"].str.contains(name_filter, case=False)]
        if dept_filter:
            df = df[df["department"].isin(dept_filter)]

    st.markdown("### ✏️ Edit Quotas")
    for i, row in df.iterrows():
        with st.expander(f"{row['full_name']} ({row['department']})", expanded=False):
            current = int(row["annual_quota"]) if pd.notnull(row["annual_quota"]) else 20
            new_quota = st.number_input("Annual Leave Quota", min_value=0, max_value=100, value=current, key=f"quota_{i}")
            if st.button("💾 Save", key=f"save_{i}"):
                update_quota(row["employee_id"], new_quota)
                st.success(f"{row['full_name']}'s quota updated to {new_quota} days.")
                st.rerun()

    st.markdown("### 📤 Export All Quotas")
    excel = to_excel_download(df)
    st.download_button(
        label="Download as Excel",
        data=excel,
        file_name="employee_leave_quotas.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
