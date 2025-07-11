import streamlit as st
import sqlite3
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime

# DB Connection
def create_connection():
    return sqlite3.connect("hris.db", check_same_thread=False)

# Get employees with payroll history
def get_employees_with_payroll():
    conn = create_connection()
    df = pd.read_sql_query("""
        SELECT DISTINCT e.id, e.full_name
        FROM employees e
        JOIN payroll p ON e.id = p.employee_id
        ORDER BY e.full_name
    """, conn)
    conn.close()
    return df

# Get payslip data
def get_payslip(employee_id, pay_month):
    conn = create_connection()
    df = pd.read_sql_query("""
        SELECT e.full_name, e.department,
               p.base_salary, p.bonus, p.deduction,
               (p.base_salary + p.bonus - p.deduction) AS net_pay,
               p.pay_month, p.generated_on
        FROM payroll p
        JOIN employees e ON p.employee_id = e.id
        WHERE p.employee_id = ? AND p.pay_month = ?
        LIMIT 1
    """, conn, params=(employee_id, pay_month))
    conn.close()
    return df.iloc[0] if not df.empty else None

# Generate PDF in memory
def create_payslip_pdf(data):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Header
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, height - 50, "Payslip")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(50, height - 70, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Employee Info
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, height - 110, f"Employee Name: {data['full_name']}")
    pdf.drawString(50, height - 130, f"Department: {data['department']}")
    pdf.drawString(50, height - 150, f"Pay Month: {data['pay_month']}")

    # Salary Info
    pdf.setFont("Helvetica", 11)
    pdf.drawString(50, height - 190, f"Base Salary: GHS {data['base_salary']:.2f}")
    pdf.drawString(50, height - 210, f"Bonus: GHS {data['bonus']:.2f}")
    pdf.drawString(50, height - 230, f"Deductions: GHS {data['deduction']:.2f}")
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, height - 260, f"Net Pay: GHS {data['net_pay']:.2f}")

    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    return buffer

# UI
def show():
    st.title("🧾 Payslip PDF Generator")

    df_emps = get_employees_with_payroll()
    if df_emps.empty:
        st.warning("No employees with payslips found.")
        return

    emp_name = st.selectbox("Select Employee", df_emps["full_name"].tolist())
    selected_emp = df_emps[df_emps["full_name"] == emp_name].iloc[0]

    # Manually select month
    month = st.text_input("Enter Pay Month (e.g., July 2025)", value="July 2025")

    if st.button("📄 Generate Payslip PDF"):
        payslip = get_payslip(selected_emp["id"], month)
        if payslip is None:
            st.error("No payslip found for this employee and month.")
        else:
            pdf_buffer = create_payslip_pdf(payslip)
            st.success("Payslip generated!")
            st.download_button(
                label="📥 Download Payslip PDF",
                data=pdf_buffer,
                file_name=f"Payslip_{emp_name}_{month.replace(' ', '_')}.pdf",
                mime="application/pdf"
            )
