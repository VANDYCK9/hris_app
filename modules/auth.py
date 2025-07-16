import streamlit as st
import sqlite3
import hashlib
import random
import string
from modules.mailer import send_email

def create_connection():
    return sqlite3.connect("hris.db", check_same_thread=False)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def generate_verification_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def register_user(username, email, password, department, job_role, role="Employee"):
    conn = create_connection()
    cursor = conn.cursor()
    code = generate_verification_code()
    try:
        # Insert into users table (login)
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, role, is_verified, verification_code)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (username, email, hash_password(password), role, 0, code))

        # Auto-insert into employees table
        cursor.execute("""
            INSERT INTO employees (full_name, department, role, email, phone, hire_date)
            VALUES (?, ?, ?, ?, ?, DATE('now'))
        """, (username, department, job_role, email, ''))

        conn.commit()
        return True, code
    except sqlite3.IntegrityError:
        return False, None
    finally:
        conn.close()

def login_user(username, password):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password_hash=?", 
                   (username, hash_password(password)))
    user = cursor.fetchone()
    conn.close()
    return user

def verify_user(username, code):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT verification_code FROM users WHERE username=?", (username,))
    row = cursor.fetchone()
    if row and row[0] == code:
        cursor.execute("UPDATE users SET is_verified=1 WHERE username=?", (username,))
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False

def reset_password(username, new_password):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password_hash=? WHERE username=?",
                   (hash_password(new_password), username))
    conn.commit()
    conn.close()

def show_login():
    st.title("🔐 HRIS Login")

    menu = st.radio("Choose an action", ["Login", "Register", "Forgot Password"])

    # ✅ LOGIN
    if menu == "Login":
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            user = login_user(username, password)
            if user:
                user_role = user[4]        # role column
                is_verified = user[5]      # is_verified column

                if user_role == "Admin":
                    # ✅ Admins can log in without verification
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = user[1]
                    st.session_state["role"] = user_role
                    st.success(f"✅ Logged in as {user[1]} (Admin)")
                    st.rerun()

                elif user_role == "Employee" and is_verified == 0:
                    # Employees must verify before login
                    st.warning("⚠️ Your account is not verified! Please check your email for the verification code.")
                else:
                    # Verified employee login
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = user[1]
                    st.session_state["role"] = user_role
                    st.success(f"✅ Logged in as {user[1]} ({user_role})")
                    st.rerun()
            else:
                st.error("❌ Invalid username or password")

    # ✅ REGISTRATION
    elif menu == "Register":
        st.subheader("📝 Employee Registration")
        username = st.text_input("Full Name")
        email = st.text_input("Work Email")
        department = st.text_input("Department")
        job_role = st.text_input("Job Role")
        password = st.text_input("Choose a Password", type="password")
        confirm = st.text_input("Confirm Password", type="password")

        if st.button("Register"):
            if password != confirm:
                st.error("❌ Passwords do not match!")
            else:
                success, code = register_user(username, email, password, department, job_role)
                if success:
                    st.success("✅ Account created! A verification code has been sent to your email.")
                    send_email(
                        email,
                        "HRIS Verification Code",
                        f"Hi {username},\n\nYour HRIS verification code is: {code}\n\nEnter this in the app to verify your account."
                    )
                else:
                    st.warning("⚠️ Username already exists.")

        # ✅ VERIFICATION STEP
        st.markdown("#### ✅ Verify Your Account")
        v_user = st.text_input("Enter Username to Verify")
        v_code = st.text_input("Enter Verification Code")
        if st.button("Verify Account"):
            if verify_user(v_user, v_code):
                st.success("✅ Account verified! You can now log in.")
            else:
                st.error("❌ Invalid verification code.")

    # ✅ FORGOT PASSWORD
    elif menu == "Forgot Password":
        username = st.text_input("Enter Username for Reset")
        new_pass = st.text_input("New Password", type="password")
        confirm_pass = st.text_input("Confirm New Password", type="password")
        if st.button("Reset Password"):
            if new_pass != confirm_pass:
                st.error("❌ Passwords do not match!")
            else:
                reset_password(username, new_pass)
                st.success("✅ Password reset successfully. You can now log in.")

                # Fetch user email to notify
                conn = create_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT email FROM users WHERE username=?", (username,))
                row = cursor.fetchone()
                conn.close()
                if row and row[0]:
                    send_email(
                        row[0],
                        "HRIS Password Reset Confirmation",
                        f"Hi {username},\n\nYour HRIS password has been reset successfully.\nIf you did not request this, please contact Admin."
                    )
