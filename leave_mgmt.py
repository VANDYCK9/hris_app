import streamlit as st
import sqlite3
import pandas as pd
from datetime import date
import plotly.express as px

# DB connection
def create_connection():
    return sqlite3.connect("hris.db", check_same_thread=False)

# Fetch employee list
def get_employees():
    conn = create_connection()
    df = pd.read_sql_query("SELECT id, full_name FROM employees", conn)
    conn.close()
    return df

# Add leave request
def submit_leave(employee_id, leave_type, start_date, end_date, reason):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO leave_requests (employee_id, leave_type, start_date, end_date, reason)
        VALUES (?, ?, ?, ?, ?)
    """, (employee_id, leave_type, start_date, end_date, reason))
    conn.commit()
    conn.close()

# Get all leave requests with employee names
def get_leave_requests():
    conn = create_connection()
    df = pd.read_sql_query("""
        SELECT lr.id, e.full_name, lr.leave_type, lr.start_date, lr.end_date, lr.reason, lr.status
        FROM leave_requests lr
        JOIN employees e ON lr.employee_id = e.id
        ORDER BY lr.id DESC
    """, conn)
    conn.close()
    return df

# Update leave status
def update_leave_status(leave_id, new_status):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE leave_requests SET status=? WHERE id=?", (new_status, leave_id))
    conn.commit()
    conn.close()

# 📅 Leave calendar view using Plotly
def show_leave_calendar(df):
    if df.empty:
        st.info("No leave records available.")
        return

    gantt_df = df.copy()
    gantt_df["Task"] = gantt_df["full_name"] + " (" + gantt_df["leave_type"] + ")"
    gantt_df["Start"] = pd.to_datetime(gantt_df["start_date"])
    gantt_df["Finish"] = pd.to_datetime(gantt_df["end_date"])
    gantt_df["Status"] = gantt_df["status"]

    st.markdown("### 📅 Leave Calendar View")

    fig = px.timeline(
        gantt_df,
        x_start="Start",
        x_end="Finish",
        y="Task",
        color="Status",
        title="Leave Schedule",
        hover_name="full_name"
    )

    fig.update_yaxes(autorange="reversed")
    fig.update_layout(height=600)
    st.plotly_chart(fig, use_container_width=True)

# Main UI
def show():
    st.title("🗓️ Leave Management")

    # Submit Leave Form
    st.markdown("### 📝 Submit Leave Request")
    employee_df = get_employees()

    if employee_df.empty:
        st.warning("⚠️ No employees found. Please add employees first.")
        return

    with st.form("leave_form"):
        employee = st.selectbox("Select Employee", employee_df["full_name"])
        selected_row = employee_df[employee_df["full_name"] == employee]
        if not selected_row.empty:
            emp_id = int(selected_row.iloc[0]["id"])
        else:
            st.warning("Employee ID not found.")
            return

        leave_type = st.selectbox("Leave Type", ["Annual", "Sick", "Maternity", "Emergency", "Other"])
        start_date = st.date_input("Start Date", value=date.today())
        end_date = st.date_input("End Date", value=date.today())
        reason = st.text_area("Reason")
        submit_btn = st.form_submit_button("Submit Leave Request")

        if submit_btn:
            submit_leave(emp_id, leave_type, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"), reason)
            st.success("✅ Leave request submitted successfully.")
            st.rerun()

    # View and Manage Leave Requests
    st.markdown("### 📋 Leave Requests")
    leave_df = get_leave_requests()

    # Filter
    with st.expander("🔍 Filter", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            emp_filter = st.multiselect("Filter by Employee", leave_df["full_name"].unique())
        with col2:
            status_filter = st.multiselect("Filter by Status", leave_df["status"].unique())

        if emp_filter:
            leave_df = leave_df[leave_df["full_name"].isin(emp_filter)]
        if status_filter:
            leave_df = leave_df[leave_df["status"].isin(status_filter)]

    st.dataframe(leave_df, use_container_width=True)

    # Approve/Reject Section
    for i, row in leave_df.iterrows():
        if row["status"] == "Pending":
            with st.expander(f"🕓 Request by {row['full_name']} | {row['leave_type']} ({row['start_date']} to {row['end_date']})"):
                st.write(f"**Reason:** {row['reason']}")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Approve", key=f"approve{i}"):
                        update_leave_status(row["id"], "Approved")
                        st.success("Leave approved.")
                        st.rerun()
                with col2:
                    if st.button("❌ Reject", key=f"reject{i}"):
                        update_leave_status(row["id"], "Rejected")
                        st.error("Leave rejected.")
                        st.rerun()

    # 📅 Show leave calendar
    with st.expander("📅 Leave Calendar View", expanded=True):
        show_leave_calendar(leave_df)
