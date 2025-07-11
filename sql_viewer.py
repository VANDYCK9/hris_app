import streamlit as st
import sqlite3
import pandas as pd

def show():
    st.title("🛠 SQL Viewer Tool")

    # Connect to DB
    conn = sqlite3.connect("hris.db", check_same_thread=False)
    cursor = conn.cursor()

    # Show available tables
    tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    table_list = [t[0] for t in tables]

    selected_table = st.selectbox("📋 Select a Table to View", table_list)

    if selected_table:
        df = pd.read_sql_query(f"SELECT * FROM {selected_table}", conn)
        st.subheader(f"🔍 Contents of `{selected_table}` ({len(df)} rows)")
        st.dataframe(df, use_container_width=True)

        # Optional: raw SQL query interface
        st.markdown("### 🧠 Run Custom SQL Query (Optional)")
        query = st.text_area("Type your query below:", f"SELECT * FROM {selected_table} LIMIT 10")

        if st.button("▶️ Run Query"):
            try:
                result = pd.read_sql_query(query, conn)
                st.success("✅ Query executed successfully.")
                st.dataframe(result, use_container_width=True)
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

    conn.close()
