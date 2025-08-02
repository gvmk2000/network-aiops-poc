import sqlite3

def setup_database(db_path="network_poc.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS network_kpi (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        device_id TEXT,
        latency REAL,
        throughput REAL,
        packet_loss REAL,
        jitter REAL,
        signal_strength REAL,
        call_drop INTEGER
    )
    """
    )
    c.execute("""
    CREATE TABLE IF NOT EXISTS event_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        device_id TEXT,
        event_type TEXT,
        details TEXT
    )
    """
    )
    c.execute("""
    CREATE TABLE IF NOT EXISTS configurations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_id TEXT,
        config_snapshot TEXT,
        timestamp TEXT
    )
    """
    )
    c.execute("""
    CREATE TABLE IF NOT EXISTS aiops_actions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        device_id TEXT,
        anomaly_type TEXT,
        root_cause TEXT,
        recommendation TEXT,
        operator_feedback TEXT
    )
    """
    )
    conn.commit()
    conn.close()

if __name__ == "__main__":
    setup_database()