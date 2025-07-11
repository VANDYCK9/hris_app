import streamlit as st
import sqlite3
import pandas as pd
from io import BytesIO

def create_connection():
    return sqlite3.connect("hris.db", check_same_thread=False)

def get_summary(month_year):
    conn = create_connection()
    df = pd.read_sql_query("""
        SELECT e.full_name, e.department, a.date, a.check_in, a.check_out
        FROM attendance a
        JOIN employees e ON a.employee_id = e.id
        WHERE a.date LIKE ?
    """, conn, params=(f"{month_year}%",))
    conn.close()
    return df

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Monthly Summary")
    return output.getvalue()

def show():
    st.title("📆 Monthly Attendance Summary")

    selected_month = st.selectbox("Select Month", [
        "2025-01", "2025-02", "2025-03", "2025-04", "2025-05",
        "2025-06", "2025-07", "2025-08", "2025-09", "2025-10",
        "2025-11", "2025-12"
    ])

    df = get_summary(selected_month)
    if df.empty:
        st.warning("No attendance records found for selected month.")
        return

    summary = df.groupby("full_name").agg(
        Department=("department", "first"),
        Days_Present=("date", "nunique"),
        Check_Ins=("check_in", lambda x: x.notna().sum()),
        Check_Outs=("check_out", lambda x: x.notna().sum())
    ).reset_index()

    st.dataframe(summary, use_container_width=True)

    excel_data = to_excel(summary)
    st.download_button("📥 Download Excel Summary", data=excel_data, file_name=f"attendance_summary_{selected_month}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
