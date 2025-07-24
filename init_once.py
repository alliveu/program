# init_once.py
from config import DB_PATH
import sqlite3

print("[INIT] Opening DB...")
with sqlite3.connect(DB_PATH) as conn:
    result = conn.execute("PRAGMA journal_mode=WAL;").fetchone()
    print(f"[INIT] WAL mode result: {result[0]}")
