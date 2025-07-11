import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from io import BytesIO

def create_connection():
    return sqlite3.connect("hris.db", check_same_thread=False)

def get_weekly_summary(year):
    conn = create_connection()
    df = pd.read_sql_query("""
        SELECT e.full_name, e.department, a.date, a.check_in, a.check_out
        FROM attendance a
        JOIN employees e ON a.employee_id = e.id
        WHERE a.date LIKE ?
    """, conn, params=(f"{year}%",))
    conn.close()

    if df.empty:
        return pd.DataFrame()

    df["date"] = pd.to_datetime(df["date"])
    df["week"] = df["date"].dt.strftime("Week %U (%b %d)")
    df["day"] = df["date"].dt.day_name()

    summary = df.groupby(["full_name", "week"]).agg(
        Department=("department", "first"),
        Days_Present=("date", "nunique"),
        Check_Ins=("check_in", lambda x: x.notna().sum()),
        Check_Outs=("check_out", lambda x: x.notna().sum()),
        Avg_CheckIn=("check_in", lambda x: pd.to_datetime(x).dt.time.mean() if x.notna().sum() > 0 else None),
        Avg_CheckOut=("check_out", lambda x: pd.to_datetime(x).dt.time.mean() if x.notna().sum() > 0 else None)
    ).reset_index()

    return summary

def get_absentees(year, min_days=1):
    summary = get_weekly_summary(year)
    if summary.empty:
        return pd.DataFrame()
    return summary[summary["Days_Present"] < min_days]

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Weekly Summary")
    return output.getvalue()

def show():
    st.title("🔁 Weekly Attendance Summary")

    selected_year = st.selectbox("Select Year", ["2025", "2024"])
    min_days = st.slider("🚦 Alert if Days Present in Week is below:", min_value=0, max_value=7, value=1)

    st.markdown("### 📋 Weekly Summary by Employee")
    summary_df = get_weekly_summary(selected_year)

    if summary_df.empty:
        st.warning("⚠️ No attendance records found for this year.")
    else:
        st.dataframe(summary_df, use_container_width=True)
        excel = to_excel(summary_df)
        st.download_button("📥 Download Weekly Summary", data=excel, file_name=f"weekly_summary_{selected_year}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    st.markdown("### 🚨 Absentee Alerts")

    absentee_df = get_absentees(selected_year, min_days)
    if absentee_df.empty:
        st.success("✅ No employees fall below the threshold. Great attendance!")
    else:
        st.error(f"⚠️ {len(absentee_df)} employee-week records below threshold.")
        st.dataframe(absentee_df, use_container_width=True)
        absentee_excel = to_excel(absentee_df)
        st.download_button("📥 Download Absentee Report", data=absentee_excel, file_name=f"absentees_{selected_year}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
