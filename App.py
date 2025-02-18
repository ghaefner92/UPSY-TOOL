import streamlit as st
import pandas as pd
import sqlite3
import datetime
import plotly.express as px
import os
import time

# Database setup
DB_FILE = "tasks_db.sqlite"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Task TEXT NOT NULL,
            Beschreibung TEXT DEFAULT '',
            Prioritaet TEXT CHECK (Prioritaet IN ('High', 'Medium', 'Low')) DEFAULT 'Medium',
            Status TEXT CHECK (Status IN ('Pending', 'In Progress', 'Completed')) DEFAULT 'Pending',
            Start_Date TEXT NOT NULL,
            End_Date TEXT NOT NULL,
            Verantwortlich TEXT DEFAULT ''
        )
    """)
    conn.commit()
    conn.close()

def load_tasks():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM tasks", conn)
    conn.close()
    if not df.empty:
        df["Start_Date"] = pd.to_datetime(df["Start_Date"]).dt.date
        df["End_Date"] = pd.to_datetime(df["End_Date"]).dt.date
    return df

def add_task(task, desc, priority, status, start_date, end_date, responsible):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tasks (Task, Beschreibung, Prioritaet, Status, Start_Date, End_Date, Verantwortlich)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (task, desc, priority, status, start_date, end_date, responsible))
    conn.commit()
    conn.close()

def delete_task(task_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE ID = ?", (task_id,))
    conn.commit()
    conn.close()

def update_task(task_id, column, new_value):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(f"UPDATE tasks SET {column} = ? WHERE ID = ?", (new_value, task_id))
    conn.commit()
    conn.close()

# Initialize database
init_db()

# Set Page Config
st.set_page_config(page_title="UPSY-IMIQ Aufgabenmanager", page_icon="✨", layout="wide")

# Sidebar with Logo and Task Input Form
with st.sidebar:
    st.image("logo.png", use_container_width=True)
    st.markdown("""<h2 style='text-align:center;color:#2980b9;'>📌 Aufgabenmanager</h2>""", unsafe_allow_html=True)
    st.markdown("---")
    
    st.header("➕ Neue Aufgabe hinzufügen")
    task_name = st.text_input("Aufgabenname")
    task_desc = st.text_area("Beschreibung")
    task_priority = st.selectbox("Priorität", ["High", "Medium", "Low"], index=1)
    task_status = st.selectbox("Status", ["Pending", "In Progress", "Completed"], index=0)
    task_responsible = st.text_input("Verantwortlich")
    task_start_date = st.date_input("Startdatum", datetime.date.today())
    task_end_date = st.date_input("Enddatum", datetime.date.today())
    
    if st.button("✅ Aufgabe hinzufügen", use_container_width=True):
        if task_name:
            add_task(task_name, task_desc, task_priority, task_status, task_start_date, task_end_date, task_responsible)
            st.success("Aufgabe erfolgreich hinzugefügt!")
            st.rerun()
        else:
            st.warning("Aufgabenname ist erforderlich!")
    
# Load task data
tasks = load_tasks()

# Aufgabenliste Section
st.markdown("""<h2 style='color:#2980b9;'>📋 Aufgabenliste</h2>""", unsafe_allow_html=True)
if not tasks.empty:
    st.dataframe(tasks.style.set_properties(
        **{
            'background-color': '#f7f9fc', 
            'color': '#2c3e50', 
            'border': '1px solid #bdc3c7', 
            'font-size': '14px', 
            'text-align': 'center',
            'font-weight': 'bold'
        }
    ).set_table_styles([
        {'selector': 'thead th', 'props': [('background-color', '#2980b9'), ('color', 'white'), ('font-size', '16px')]},
        {'selector': 'tbody tr:nth-child(even)', 'props': [('background-color', '#e3e7ec')]}
    ]), use_container_width=True)

    selected_task_id = st.selectbox("🗑 Aufgabe zum Löschen auswählen", options=tasks["ID"].tolist(), format_func=lambda x: tasks[tasks["ID"] == x]["Task"].values[0])
    if st.button("🗑 Aufgabe löschen", use_container_width=True):
        delete_task(selected_task_id)
        st.success("Aufgabe gelöscht!")
        st.rerun()
else:
    st.info("Keine Aufgaben verfügbar. Bitte Aufgaben hinzufügen!")

# Export Button
st.download_button("📥 Exportieren als CSV", data=tasks.to_csv(index=False), file_name="tasks.csv", mime="text/csv")

# Exit Button
if st.button("🚪 App beenden", use_container_width=True):
    st.warning("App wird geschlossen...")
    time.sleep(1)
    os._exit(0)
