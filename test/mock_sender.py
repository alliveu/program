import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import SENDER_PORT, BAUDRATE
import serial
import time
import random

def mock_sender():
    try:
        with serial.Serial(SENDER_PORT, BAUDRATE, timeout=1) as ser:
            print(f"[MOCK SENDER] Port open: {SENDER_PORT}")
            while True:
                value = round(random.uniform(40.0, 80.0), 2)
                msg = f"device001,{value}\n"
                ser.write(msg.encode("utf-8"))
                print(f"[MOCK SENDER] Sent: {msg.strip()}")
                time.sleep(1)
    except Exception as e:
        print(f"[MOCK SENDER ERROR] {e}")

if __name__ == "__main__":
    mock_sender()
