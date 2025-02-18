import streamlit as st
import pandas as pd
import sqlite3
import datetime
import plotly.express as px
import os
import time

# Database setup
DB_FILE = "tasks_db.sqlite"

# Initialize SQLite Database
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Task TEXT NOT NULL,
            Description TEXT,
            Priority TEXT CHECK (Priority IN ('High', 'Medium', 'Low')),
            Status TEXT CHECK (Status IN ('Pending', 'In Progress', 'Completed')),
            Start_Date TEXT NOT NULL,
            End_Date TEXT NOT NULL,
            Responsible TEXT
        )
    """)
    conn.commit()
    conn.close()

# Load tasks from DB
def load_tasks():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM tasks", conn)
    conn.close()

    if not df.empty:
        df["Start_Date"] = pd.to_datetime(df["Start_Date"]).dt.strftime('%Y-%m-%d')
        df["End_Date"] = pd.to_datetime(df["End_Date"]).dt.strftime('%Y-%m-%d')
    return df

# Add new task
def add_task(task, desc, priority, status, start_date, end_date, responsible):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tasks (Task, Description, Priority, Status, Start_Date, End_Date, Responsible)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (task, desc, priority, status, start_date, end_date, responsible))
    conn.commit()
    conn.close()

# Delete task by ID
def delete_task(task_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE ID = ?", (task_id,))
    conn.commit()
    conn.close()

# Update task field
def update_task(task_id, column, new_value):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(f"UPDATE tasks SET {column} = ? WHERE ID = ?", (new_value, task_id))
    conn.commit()
    conn.close()

# Initialize database
init_db()

# Load Logo & Title
st.markdown("<h1 style='color:#2980b9; font-size: 30px; font-weight: bold;'>✨ Arbeitsplaner UPSY-IMIQ</h1>", unsafe_allow_html=True)

# Sidebar: Task Input Form
with st.sidebar:
    st.header("➕ Add New Task")
    task_name = st.text_input("Task Name")
    task_desc = st.text_area("Description")
    task_priority = st.selectbox("Priority", ["High", "Medium", "Low"])
    task_status = st.selectbox("Status", ["Pending", "In Progress", "Completed"])
    task_responsible = st.text_input("Responsible")
    task_start_date = st.date_input("Start Date", datetime.date.today())
    task_end_date = st.date_input("End Date", datetime.date.today())

    if st.button("Add Task"):
        if task_name:
            add_task(task_name, task_desc, task_priority, task_status, task_start_date, task_end_date, task_responsible)
            st.success("✅ Task successfully added!")
            st.rerun()
        else:
            st.warning("⚠️ Task name is required.")

# Load task data
tasks = load_tasks()

# Display Task List
st.subheader("📋 Task List")
if not tasks.empty:
    edited_tasks = st.data_editor(
        tasks,
        key="tasks_table",
        column_config={
            "ID": None,
            "Description": st.column_config.TextColumn(),
            "Status": st.column_config.SelectboxColumn(options=["Pending", "In Progress", "Completed"]),
            "Responsible": st.column_config.TextColumn()
        },
        hide_index=True
    )

    # Detect edited fields
    for row_index, row in edited_tasks.iterrows():
        original_row = tasks.iloc[row_index]
        for col in ["Description", "Status", "Responsible"]:
            if row[col] != original_row[col]:
                update_task(row["ID"], col, row[col])
                st.rerun()

    # Task Deletion - Now uses a compact dropdown
    task_list = tasks["Task"].tolist()
    if task_list:
        if not tasks.empty:
            task_options = tasks.set_index("ID")["Task"].to_dict()  # Create a dictionary {ID: Task}
            selected_task_id = st.selectbox("Select Task to Delete", options=list(task_options.keys()),
                                            format_func=lambda x: task_options[x])

            if st.button("🗑 Delete Task"):
                delete_task(selected_task_id)
                st.success(f"✅ Task '{task_options[selected_task_id]}' deleted!")
                st.rerun()

    else:
        st.info("No tasks available to delete.")

else:
    st.info("No tasks available. Add a task to get started!")

# 🔹 Export Data
st.download_button("📥 Export to CSV", data=tasks.to_csv(index=False), file_name="tasks.csv", mime="text/csv")

# 🔹 Gantt Chart - Task Timeline (Fixed to remove hours)
st.subheader("📊 Gantt Chart - Task Timeline")
if not tasks.empty:
    # Convert to proper datetime format
    tasks["Start_Date"] = pd.to_datetime(tasks["Start_Date"])
    tasks["End_Date"] = pd.to_datetime(tasks["End_Date"])

    # Generate Gantt Chart
    fig = px.timeline(
        tasks, x_start="Start_Date", x_end="End_Date", y="Task", color="Priority",
        title="Task Timeline", labels={"Priority": "Priority Level"},
        color_discrete_map={"High": "#ff7675", "Medium": "#fdcb6e", "Low": "#00cec9"}
    )
    fig.update_layout(xaxis=dict(type="date"))  # Ensure only dates appear
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No tasks available to display in the Gantt chart.")

# 🔴 Exit Button
if st.button("🚪 Exit App"):
    st.warning("🔴 Closing app...")
    time.sleep(1)
    os._exit(0)
