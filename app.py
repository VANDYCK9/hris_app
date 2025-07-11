import streamlit as st

# Load modules
from modules import employee_mgmt
from modules import leave_mgmt
from modules import leave_quota_manager
from modules import payroll_manager
from modules import payroll_generator
from modules import payslip_pdf
from modules import attendance_tracker
from modules import attendance_summary
from modules import weekly_attendance

# Sidebar navigation
st.sidebar.title("📊 HRIS Dashboard")
menu = st.sidebar.selectbox("Navigate to:", [
    "Employee Management",
    "Leave Management",
    "Leave Quota Manager",
    "Payroll Manager",
    "Payroll Generator",
    "Payslip PDF Generator",
    "Attendance Tracker",
    "Attendance Summary",
    "Weekly Attendance & Absentee Alerts"
])

# Page routing
if menu == "Employee Management":
    employee_mgmt.show()

elif menu == "Leave Management":
    leave_mgmt.show()

elif menu == "Leave Quota Manager":
    leave_quota_manager.show()

elif menu == "Payroll Manager":
    payroll_manager.show()

elif menu == "Payroll Generator":
    payroll_generator.show()

elif menu == "Payslip PDF Generator":
    payslip_pdf.show()

elif menu == "Attendance Tracker":
    attendance_tracker.show()

elif menu == "Attendance Summary":
    attendance_summary.show()

elif menu == "Weekly Attendance & Absentee Alerts":
    weekly_attendance.show()
