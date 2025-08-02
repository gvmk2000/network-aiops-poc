import random
import sqlite3
from datetime import datetime, timezone
from utils import DEVICES

DB_PATH = "network_poc.db"
ANOMALY_TYPES = [
    ("latency_spike", "High latency detected"),
    ("packet_loss", "Excessive packet loss"),
    ("signal_drop", "Signal strength degraded"),
    ("call_drop", "Frequent call drops"),
    ("cpu_high", "CPU usage > 90%"),
    ("link_failure", "Link down detected"),
    ("auth_fail", "Multiple authentication failures")
]

RECOMMENDATIONS = [
    "Reroute traffic", "Dispatch field team", "Audit logs", "Restart device", "Check configuration"
]

OPERATOR_FEEDBACK = [
    "Investigating", "Resolved", "Escalated", "No action needed"
]

def generate_anomalies(samples=50):
    conn = sqlite3.connect(DB_PATH)
    for _ in range(samples):
        device_id = random.choice(DEVICES)
        anomaly_type, root_cause = random.choice(ANOMALY_TYPES)
        recommendation = random.choice(RECOMMENDATIONS)
        operator_feedback = random.choice(OPERATOR_FEEDBACK)
        timestamp = datetime.now(timezone.utc).isoformat()
        conn.execute(
            "INSERT INTO aiops_actions (timestamp, device_id, anomaly_type, root_cause, recommendation, operator_feedback) VALUES (?, ?, ?, ?, ?, ?)",
            (timestamp, device_id, anomaly_type, root_cause, recommendation, operator_feedback)
        )
    conn.commit()
    conn.close()

if __name__ == "__main__":
    generate_anomalies()
