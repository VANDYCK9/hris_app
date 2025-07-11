import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from io import BytesIO

# Connect to DB
def create_connection():
    return sqlite3.connect("hris.db", check_same_thread=False)

# Get leave summary per employee with quota
def get_leave_summary():
    conn = create_connection()

    # Fetch leave days used (approved only)
    leave_df = pd.read_sql_query("""
        SELECT e.id AS employee_id, e.full_name, e.department,
               lr.leave_type, lr.start_date, lr.end_date
        FROM leave_requests lr
        JOIN employees e ON lr.employee_id = e.id
        WHERE lr.status = 'Approved'
    """, conn)

    # Fetch leave quotas
    quota_df = pd.read_sql_query("SELECT * FROM leave_quota", conn)
    conn.close()

    if leave_df.empty:
        return pd.DataFrame()

    # Calculate days used
    leave_df["start_date"] = pd.to_datetime(leave_df["start_date"])
    leave_df["end_date"] = pd.to_datetime(leave_df["end_date"])
    leave_df["days_used"] = (leave_df["end_date"] - leave_df["start_date"]).dt.days + 1

    # Aggregate leave usage per employee
    summary = leave_df.groupby(["employee_id", "full_name", "department"], as_index=False)["days_used"].sum()

    # Merge with quotas
    summary = pd.merge(summary, quota_df, how="left", on="employee_id")

    # Default quota = 20 where missing
    summary["annual_quota"] = summary["annual_quota"].fillna(20).astype(int)

    # Calculate remaining
    summary["days_remaining"] = summary["annual_quota"] - summary["days_used"]

    return summary

# Excel export helper
def to_excel_download(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Leave Balance')
    return output.getvalue()

# Main view
def show():
    st.title("📊 Leave Balance Summary")

    df = get_leave_summary()

    if df.empty:
        st.info("No approved leave requests or no employees with leave.")
        return

    # Filter
    with st.expander("🔍 Filter", expanded=True):
        employees = st.multiselect("Filter by Employee", df["full_name"].unique())
        departments = st.multiselect("Filter by Department", df["department"].unique())

        if employees:
            df = df[df["full_name"].isin(employees)]
        if departments:
            df = df[df["department"].isin(departments)]

    st.dataframe(df, use_container_width=True)

    # Download button
    excel_file = to_excel_download(df)
    st.download_button(
        label="📥 Export Summary to Excel",
        data=excel_file,
        file_name="leave_balance_summary.xlsx",
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
