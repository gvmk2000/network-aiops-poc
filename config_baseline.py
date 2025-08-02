# Configuration Baseline & Policy Store
# This module manages configuration baselines and policies for network devices.

import sqlite3

DB_PATH = "network_poc.db"

class ConfigBaseline:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path

    def get_baseline(self, device_id):
        conn = sqlite3.connect(self.db_path)
        row = conn.execute("SELECT baseline FROM config_baseline WHERE device_id=?", (device_id,)).fetchone()
        conn.close()
        return row[0] if row else None

    def set_baseline(self, device_id, baseline):
        conn = sqlite3.connect(self.db_path)
        conn.execute("INSERT OR REPLACE INTO config_baseline (device_id, baseline) VALUES (?, ?)", (device_id, baseline))
        conn.commit()
        conn.close()

    def get_all_policies(self):
        conn = sqlite3.connect(self.db_path)
        rows = conn.execute("SELECT * FROM policy_store").fetchall()
        conn.close()
        return rows
