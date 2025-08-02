import sqlite3
import numpy as np
from sklearn.ensemble import IsolationForest
from utils import DEVICES, dict_factory
from datetime import datetime, timezone

DB_PATH = "network_poc.db"

def fetch_kpi_for_window(window=100):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = dict_factory
    c = conn.cursor()
    c.execute("SELECT * FROM network_kpi ORDER BY timestamp DESC LIMIT ?", (window,))
    data = c.fetchall()
    conn.close()
    return data

def anomaly_detection(kpi_data):
    feats = np.array([[k['latency'], k['throughput'], k['packet_loss'], k['jitter'], k['signal_strength']] for k in kpi_data])
    model = IsolationForest(contamination=0.06)
    preds = model.fit_predict(feats)
    anomalies = [kpi_data[i] for i in range(len(kpi_data)) if preds[i] == -1]
    return anomalies

def fetch_logs_for_device(device_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = dict_factory
    c = conn.cursor()
    c.execute("SELECT * FROM event_log WHERE device_id=? ORDER BY timestamp DESC LIMIT 10", (device_id,))
    logs = c.fetchall()
    conn.close()
    return logs

def rca(kpi_row, logs):
    cause = []
    if kpi_row["latency"] > 100:
        if any("cpu_high" in log['event_type'] for log in logs):
            cause.append("High CPU")
        if any("link_failure" in log['event_type'] for log in logs):
            cause.append("Link Failure")
    if kpi_row["signal_strength"] < -100:
        cause.append("Signal Degradation")
    if any("auth_fail" in log['event_type'] for log in logs):
        cause.append("Auth Failures")
    return " / ".join(cause) if cause else "Unknown"

def recommend_action(root_cause, device_id):
    if "High CPU" in root_cause:
        return f"Reroute traffic from {device_id}"
    if "Link Failure" in root_cause:
        return f"Switch to backup link for {device_id}"
    if "Signal Degradation" in root_cause:
        return f"Dispatch field team to {device_id}"
    if "Auth Failures" in root_cause:
        return f"Audit authentication logs on {device_id}"
    return "Log anomaly for manual investigation"

def log_aiops_action(device_id, anomaly_type, root_cause, recommendation, operator_feedback=""):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        INSERT INTO aiops_actions (timestamp, device_id, anomaly_type, root_cause, recommendation, operator_feedback)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (datetime.now(timezone.utc).isoformat(), device_id, anomaly_type, root_cause, recommendation, operator_feedback))
    conn.commit()
    conn.close()

def main():
    # Fetch latest KPIs
    kpi_data = fetch_kpi_for_window()
    # Detect anomalies
    anomalies = anomaly_detection(kpi_data)
    for a in anomalies:
        device_id = a["device_id"]
        logs = fetch_logs_for_device(device_id)
        root_cause = rca(a, logs)
        recommendation = recommend_action(root_cause, device_id)
        # Log action (operator feedback empty for now)
        log_aiops_action(device_id, "anomaly", root_cause, recommendation)
        print(f"{device_id}: Anomaly detected | Root Cause: {root_cause} | Recommendation: {recommendation}")

if __name__ == "__main__":
    main()