import os
import sqlite3
from datetime import datetime
from config import DB_PATH

def init_db():
    try:
        with sqlite3.connect(DB_PATH, timeout=5.0) as conn:
            conn.execute("PRAGMA journal_mode=WAL;")
            c = conn.cursor()
            c.execute('''
                CREATE TABLE IF NOT EXISTS sensor_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    device_id TEXT NOT NULL,
                    temperature REAL NOT NULL,
                    pressure REAL NOT NULL
                )
            ''')
            conn.commit()
    except sqlite3.OperationalError as e:
        print(f"[INIT DB ERROR] {e}")

def insert_sensor_data(device_id: str, temperature: float, pressure: float):
    timestamp = datetime.utcnow().isoformat()
    try:
        with sqlite3.connect(DB_PATH, timeout=5.0) as conn:
            conn.execute("PRAGMA journal_mode=WAL;")
            c = conn.cursor()
            c.execute('''
                INSERT INTO sensor_logs (timestamp, device_id, temperature, pressure)
                VALUES (?, ?, ?, ?)
            ''', (timestamp, device_id, temperature, pressure))
            conn.commit()
    except sqlite3.OperationalError as e:
        print(f"[DB ERROR] {e} at {timestamp} | {device_id}, {temperature}, {pressure}")

def get_latest_sensor_data():
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('''
                SELECT timestamp, device_id, temperature, pressure
                FROM sensor_logs
                ORDER BY id DESC
                LIMIT 1
            ''')
            row = c.fetchone()
            if row:
                return {
                    "timestamp": row[0],
                    "device_id": row[1],
                    "temperature": row[2],
                    "pressure": row[3]
                }
    except sqlite3.OperationalError as e:
        print(f"[DB READ ERROR] {e}")
    return None
