import streamlit as st
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import pandas as pd
import json
from utils import DEVICES
import os

app = Flask(__name__)
DB_PATH = "network_poc.db"

def load_kpi():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM network_kpi ORDER BY timestamp DESC LIMIT 150", conn)
    conn.close()
    return df

def load_events():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM event_log ORDER BY timestamp DESC LIMIT 30", conn)
    conn.close()
    return df

def load_aiops_actions():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM aiops_actions ORDER BY timestamp DESC LIMIT 30", conn)
    conn.close()
    return df

# Helper to check if anomaly data exists
def has_anomalies(device_id):
    conn = sqlite3.connect(DB_PATH)
    result = conn.execute("SELECT COUNT(*) FROM aiops_actions WHERE device_id=?", (device_id,)).fetchone()[0]
    conn.close()
    return result > 0

# Helper to get anomaly types for a device
def get_anomaly_types(device_id):
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT DISTINCT anomaly_type FROM aiops_actions WHERE device_id=?", (device_id,)).fetchall()
    conn.close()
    return [row[0] for row in rows]

@app.route('/', methods=['GET', 'POST'])
def index():
    selected_device = request.form.get('device') or DEVICES[0]
    show_anomalies = request.form.get('show_anomalies') == 'true'
    reset = request.form.get('reset') == 'true'
    selected_anomaly = request.form.get('anomaly')
    # Show KPI Data button pressed
    if request.form.get('show_kpi'):
        show_anomalies = False
    # Show Anomalies button pressed
    if request.form.get('show_anomalies'):
        show_anomalies = True
    # Reset button pressed
    if reset:
        return render_template('dashboard.html', devices=DEVICES, selected_device=selected_device, kpi_data=json.dumps({}), events=[], show_anomalies=False, reset=True, anomaly_types=[], selected_anomaly=None, anomaly_data=None)
    conn = sqlite3.connect(DB_PATH)
    # Fetch last 50 KPI records for charts
    kpi_rows = conn.execute("SELECT * FROM network_kpi WHERE device_id=? ORDER BY timestamp DESC LIMIT 50", (selected_device,)).fetchall()
    kpi_rows = kpi_rows[::-1]  # Oldest first for chart
    # Prepare data for Chart.js
    timestamps = [row[0] for row in kpi_rows]
    latency = [row[2] for row in kpi_rows]
    throughput = [row[3] for row in kpi_rows]
    packet_loss = [row[4] for row in kpi_rows]
    jitter = [row[5] for row in kpi_rows]
    signal_strength = [row[6] for row in kpi_rows]
    call_drop = [row[7] for row in kpi_rows]
    anomaly_rows = []
    anomaly_timestamps = []
    anomaly_types = get_anomaly_types(selected_device)
    anomaly_data = None
    if show_anomalies:
        anomaly_rows = conn.execute("SELECT timestamp, anomaly_type FROM aiops_actions WHERE device_id=? ORDER BY timestamp DESC LIMIT 50", (selected_device,)).fetchall()
        anomaly_timestamps = [row[0] for row in anomaly_rows]
        # If a specific anomaly is selected, fetch its details
        if selected_anomaly:
            anomaly_data = conn.execute("SELECT * FROM aiops_actions WHERE device_id=? AND anomaly_type=? ORDER BY timestamp DESC LIMIT 10", (selected_device, selected_anomaly)).fetchall()
    kpi_data = {
        'timestamps': timestamps,
        'latency': latency,
        'throughput': throughput,
        'packet_loss': packet_loss,
        'jitter': jitter,
        'signal_strength': signal_strength,
        'call_drop': call_drop,
        'anomaly_timestamps': anomaly_timestamps,
        'anomaly_types': anomaly_types
    }
    events = conn.execute("SELECT * FROM event_log WHERE device_id=? ORDER BY timestamp DESC LIMIT 10", (selected_device,)).fetchall()
    conn.close()
    return render_template('dashboard.html', devices=DEVICES, selected_device=selected_device, kpi_data=json.dumps(kpi_data), events=events, show_anomalies=show_anomalies, reset=False, anomaly_types=anomaly_types, selected_anomaly=selected_anomaly, anomaly_data=anomaly_data)

st.title("Telecom Network AIOps Dashboard")

st.subheader("Recent Network KPIs")
kpi_df = load_kpi()
st.dataframe(kpi_df)

st.subheader("Recent Events")
event_df = load_events()
st.dataframe(event_df)

st.subheader("AI-Driven Actions & Insights")
action_df = load_aiops_actions()
st.dataframe(action_df[["timestamp", "device_id", "root_cause", "recommendation", "operator_feedback"]])

if len(action_df) > 0:
    st.markdown("### Operator Feedback Form")
    idx = st.selectbox("Select an AI action to provide feedback", action_df.index)
    feedback = st.text_area("Your feedback or override:")
    if st.button("Submit Feedback"):
        # Update feedback in DB
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            "UPDATE aiops_actions SET operator_feedback=? WHERE id=?",
            (feedback, int(action_df.loc[idx]['id']))
        )
        conn.commit()
        conn.close()
        st.success("Feedback submitted!")

# Buttons to control data display
col1, col2 = st.columns(2)
with col1:
    if st.button("Collect KPI Data"):
        # If no data, run simulator
        conn = sqlite3.connect(DB_PATH)
        kpi_count = conn.execute("SELECT COUNT(*) FROM network_kpi WHERE device_id=?", (DEVICES[0],)).fetchone()[0]
        conn.close()
        if kpi_count == 0:
            os.system(f"python data_simulator.py")
        st.success("KPI Data collection initiated.")
with col2:
    if st.button("Create Anomalies"):
        # Logic to create anomalies
        conn = sqlite3.connect(DB_PATH)
        # For demonstration, we randomly mark some existing KPI records as anomalous
        kpi_rows = conn.execute("SELECT id, device_id FROM network_kpi ORDER BY RANDOM() LIMIT 5").fetchall()
        for row in kpi_rows:
            conn.execute("INSERT INTO aiops_actions (device_id, timestamp, anomaly_type) VALUES (?, ?, ?)",
                         (row[1], pd.Timestamp.now(), "simulated_anomaly"))
        conn.commit()
        conn.close()
        st.success("Anomalies created.")

# Reset button
if st.button("Reset Dashboard"):
    st.experimental_rerun()

st.markdown("""
---
**How it works:**  
- Synthetic KPIs/events are generated and stored in SQLite.  
- AI pipeline detects anomalies, analyzes root cause, recommends actions.  
- Operator feedback is logged and visible for continuous learning.
""")

if __name__ == "__main__":
    app.run(debug=True)