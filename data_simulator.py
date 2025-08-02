import random
import sqlite3
from datetime import datetime
from utils import DEVICES

DB_PATH = "network_poc.db"

def simulate_kpi(device_id):
    latency = random.gauss(50, 10)
    if random.random() < 0.07:
        latency += random.uniform(50, 150)
    throughput = random.gauss(100, 20)
    packet_loss = random.gauss(0.5, 0.1)
    jitter = random.gauss(5, 1)
    signal_strength = random.gauss(-85, 5)
    if random.random() < 0.05:
        signal_strength -= random.uniform(15, 40)
    call_drop = random.choice([0, 0, 1])
    return (
        datetime.utcnow().isoformat(),
        device_id,
        latency,
        throughput,
        packet_loss,
        jitter,
        signal_strength,
        call_drop,
    )

def simulate_event(device_id):
    events = [
        ("cpu_high", "CPU usage > 90%"),
        ("link_failure", "Link down detected"),
        ("auth_fail", "Multiple authentication failures"),
        ("config_change", f"{device_id} config updated"),
    ]
    if random.random() < 0.08:
        event = random.choice(events)
        return (
            datetime.utcnow().isoformat(),
            device_id,
            event[0],
            event[1]
        )
    return None

def main(samples=400):
    conn = sqlite3.connect(DB_PATH)
    for _ in range(samples):
        for device in DEVICES:
            kpi = simulate_kpi(device)
            conn.execute(
                "INSERT INTO network_kpi (timestamp, device_id, latency, throughput, packet_loss, jitter, signal_strength, call_drop) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                kpi
            )
            event = simulate_event(device)
            if event:
                conn.execute(
                    "INSERT INTO event_log (timestamp, device_id, event_type, details) VALUES (?, ?, ?, ?)",
                    event
                )
    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()