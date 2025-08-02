import streamlit as st
import sqlite3
import pandas as pd

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

st.markdown("""
---
**How it works:**  
- Synthetic KPIs/events are generated and stored in SQLite.  
- AI pipeline detects anomalies, analyzes root cause, recommends actions.  
- Operator feedback is logged and visible for continuous learning.
""")