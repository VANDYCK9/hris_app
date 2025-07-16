import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, date
from io import BytesIO

def create_connection():
    return sqlite3.connect("hris.db", check_same_thread=False)

def get_employees():
    conn = create_connection()
    df = pd.read_sql_query("SELECT id, full_name FROM employees ORDER BY full_name", conn)
    conn.close()
    return df

def log_attendance(emp_id, selected_date, check_in, check_out, remarks):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO attendance (employee_id, date, check_in, check_out, remarks)
        VALUES (?, ?, ?, ?, ?)
    """, (emp_id, selected_date, check_in, check_out, remarks))
    conn.commit()
    conn.close()

def fetch_attendance(emp_id=None, selected_date=None):
    conn = create_connection()
    query = """
        SELECT a.date, e.full_name, a.check_in, a.check_out, a.remarks
        FROM attendance a
        JOIN employees e ON a.employee_id = e.id
    """
    filters = []
    params = []

    if emp_id:
        filters.append("a.employee_id = ?")
        params.append(emp_id)
    if selected_date:
        filters.append("a.date = ?")
        params.append(selected_date)

    if filters:
        query += " WHERE " + " AND ".join(filters)

    query += " ORDER BY a.date DESC"

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Attendance")
    return output.getvalue()

def show():
    st.title("🕒 Attendance Tracker")

    emp_df = get_employees()
    if emp_df.empty:
        st.warning("⚠️ No employees found. Add employees first.")
        return

    emp_names = emp_df["full_name"].tolist()
    emp_dict = dict(zip(emp_names, emp_df["id"]))

    with st.form("log_attendance_form"):
        st.subheader("📌 Log New Attendance Entry")

        selected_name = st.selectbox("Select Employee", emp_names)
        emp_id = emp_dict[selected_name]

        selected_date = st.date_input("Date", value=date.today())
        check_in = st.time_input("Check-In Time (optional)", value=None)
        check_out = st.time_input("Check-Out Time (optional)", value=None)
        remarks = st.text_input("Remarks (optional)")

        submitted = st.form_submit_button("✅ Log Attendance")

        if submitted:
            log_attendance(emp_id, str(selected_date), str(check_in), str(check_out), remarks)
            st.success(f"✅ Attendance logged for {selected_name} on {selected_date}")
            st.rerun()

    st.markdown("### 🔍 View Attendance Logs")

    filter_name = st.selectbox("Filter by Employee", ["All"] + emp_names)
    filter_date = st.date_input("Filter by Date (optional)", value=None)

    emp_id_filter = emp_dict.get(filter_name) if filter_name != "All" else None
    date_filter = str(filter_date) if filter_date else None

    df = fetch_attendance(emp_id_filter, date_filter)

    if df.empty:
        st.info("No attendance records found for the selected filters.")
    else:
        st.dataframe(df, use_container_width=True)
        excel = to_excel(df)
        st.download_button("📥 Export to Excel", data=excel, file_name="attendance_log.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
