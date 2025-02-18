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
        df["Start_Date"] = pd.to_datetime(df["Start_Date"]).dt.strftime('%Y-%m-%d')  # Remove hours
        df["End_Date"] = pd.to_datetime(df["End_Date"]).dt.strftime('%Y-%m-%d')  # Remove hours
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
def delete_task(task_ids):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.executemany("DELETE FROM tasks WHERE ID = ?", [(task_id,) for task_id in task_ids])
    conn.commit()
    conn.close()


# Update task field
def update_task(task_id, column, new_value):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(f"UPDATE tasks SET {column} = ? WHERE ID = ?", (new_value, task_id))
    conn.commit()
    conn.close()


# Function to close the app
def close_app():
    st.warning("🔴 Closing app...")
    time.sleep(1)
    os._exit(0)


# Initialize database
init_db()

# 🔹 Background & Styling Fix
st.markdown("""
    <style>
        /* 🌟 Make the app full width */
        .main .block-container {
            max-width: 180% !important;  /* Expands UI width */
        }

        /* 🌟 Increase Task Table & Gantt Chart Width */
        [data-testid="stVerticalBlock"] {
            width: 100% !important;  /* Makes tables and charts take full space */
        }

        /* 🌟 Soft Green Sidebar Background */
        .stSidebar {
            background-color: #A9DFBF !important;  /* Soft pastel green */
            padding: 15px;
            border-right: 3px solid #58D68D;  /* A deeper green accent */
        }

        /* 🌟 Sidebar Font Color (Dark for contrast) */
        .stSidebar .stTextInput, .stSidebar .stSelectbox, .stSidebar .stTextArea {
            color: #1C1C1C !important;  /* Dark Gray for readability */
        }

        /* 🌟 Sidebar Headers */
        .stSidebar h1, .stSidebar h2, .stSidebar h3 {
            color: #145A32 !important;  /* Dark green for nice contrast */
        }

        /* 🌟 Background Color (Soft for Contrast) */
        .stApp {
            background-color: #a452a9 !important;  /* Soft pastel blue */
        }

        /* 🌟 Main Text Color (Readable) */
        .stText, .stButton, .stDownloadButton {
            color: #2C3E50 !important;  /* Dark grayish-blue */
        }

        /* 🌟 Title Styling */
        .title {
            font-size: 30px;
            font-weight: bold;
            color: #2980b9;  /* Blue title */
            text-align: left;
            margin-bottom: 10px;
        }

        /* 🌟 Buttons */
        .stButton>button {
            background-color: #2980b9 !important;  /* Deep blue */
            color: white !important;
            border-radius: 10px;
            font-size: 16px;
            padding: 10px;
        }

        .stButton>button:hover {
            background-color: #1a5276 !important;  /* Darker blue */
        }

        /* 🌟 Table Styling */
        .dataframe {
            font-size: 18px;
            color: #34495e !important;  /* Darker grayish-blue */
        }

        /* 🌟 Exit Button */
        .exit-btn {
            background-color: #d63031;
            color: white;
            font-weight: bold;
            padding: 10px 15px;
            border-radius: 8px;
            text-align: center;
            cursor: pointer;
            display: inline-block;
            font-size: 16px;
            width: 140px;
            margin: auto;
        }

        .exit-btn:hover {
            background-color: #e74c3c;
        }
    </style>
""", unsafe_allow_html=True)



# 🔹 Load logo and title (Use local file OR online URL)
logo_path = "logo.png"  # Change if needed
try:
    st.image(logo_path, width=280)
except:
    st.warning("⚠️ Logo not found, check the file path!")

st.markdown("<h1 class='title'>✨  Arbeitsplaner UPSY-IMIQ</h1>", unsafe_allow_html=True)

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

# 🔹 Task Table with Editable Columns
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

    # Fixed Delete Function
    selected_tasks = st.multiselect("Select Task to Delete", tasks["Task"])

    if st.button("🗑 Delete Selected Task"):
        if selected_tasks:
            task_ids_to_delete = tasks[tasks["Task"].isin(selected_tasks)]["ID"].tolist()
            delete_task(task_ids_to_delete)
            st.success("✅ Task(s) deleted!")
            st.rerun()
        else:
            st.warning("⚠️ Please select at least one task to delete.")

else:
    st.info("No tasks available. Add a task to get started!")

# 🔹 Export Data
st.download_button("📥 Export to CSV", data=tasks.to_csv(index=False), file_name="tasks.csv", mime="text/csv")

# 🔹 Gantt Chart
st.subheader("📊 Gantt Chart - Task Timeline")
if not tasks.empty:
    fig = px.timeline(
        tasks, x_start="Start_Date", x_end="End_Date", y="Task", color="Priority",
        title="Task Timeline", labels={"Priority": "Priority Level"},
        color_discrete_map={"High": "#ff7675", "Medium": "#fdcb6e", "Low": "#00cec9"}
    )
    fig.update_yaxes(categoryorder="total ascending")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No tasks available to display in the Gantt chart.")

# 🔴 Exit Button
st.markdown('<button class="exit-btn" onclick="window.close()">🚪 Exit App</button>', unsafe_allow_html=True)
if st.button("Force Close App"):
    close_app()
