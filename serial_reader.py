import serial
import time
from config import RECEIVER_PORT, BAUDRATE, TEMP_THRESHOLD
from database_handler import insert_temperature

def read_serial_forever():
    try:
        with serial.Serial(RECEIVER_PORT, BAUDRATE, timeout=1) as ser:
            print(f"[RECEIVER] Listening on {RECEIVER_PORT}")
            while True:
                try:
                    line = ser.readline().decode("utf-8").strip()
                    if line:
                        print(f"[RECEIVER] Received: {line}")
                        device_id, value_str = line.split(",")
                        value = float(value_str)
                        status = "danger" if value > TEMP_THRESHOLD else "normal"
                        insert_temperature(device_id, value, status)
                except Exception as e:
                    print(f"[PARSING ERROR] {e}")
    except Exception as e:
        print(f"[SERIAL OPEN ERROR] {e}")
