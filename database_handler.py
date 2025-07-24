import os
import sqlite3
from datetime import datetime
from config import DB_PATH

def init_db():
    try:
        with sqlite3.connect(DB_PATH, timeout=5.0) as conn:
            # WAL 설정도 커서 없이 실행
            conn.execute("PRAGMA journal_mode=WAL;")
            c = conn.cursor()
            c.execute('''
                CREATE TABLE IF NOT EXISTS temperature_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    device_id TEXT NOT NULL,
                    value REAL NOT NULL,
                    status_flag TEXT NOT NULL
                )
            ''')
            conn.commit()
    except sqlite3.OperationalError as e:
        print(f"[INIT DB ERROR] {e}")


def insert_temperature(device_id: str, value: float, status_flag: str):
    timestamp = datetime.utcnow().isoformat()
    try:
        with sqlite3.connect(DB_PATH, timeout=5.0) as conn:
            conn.execute("PRAGMA journal_mode=WAL;")
            c = conn.cursor()
            c.execute('''
                INSERT INTO temperature_logs (timestamp, device_id, value, status_flag)
                VALUES (?, ?, ?, ?)
            ''', (timestamp, device_id, value, status_flag))
            conn.commit()
    except sqlite3.OperationalError as e:
        print(f"[DB ERROR] {e} at {timestamp} | {device_id}, {value}, {status_flag}")


def get_latest_temperature():
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('''
                SELECT timestamp, device_id, value, status_flag
                FROM temperature_logs
                ORDER BY id DESC
                LIMIT 1
            ''')
            row = c.fetchone()
            if row:
                return {
                    "timestamp": row[0],
                    "device_id": row[1],
                    "value": row[2],
                    "status_flag": row[3]
                }
    except sqlite3.OperationalError as e:
        print(f"[DB READ ERROR] {e}")
    return None
