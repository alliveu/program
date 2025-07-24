import serial
import time
from config import RECEIVER_PORT, BAUDRATE
from database_handler import insert_sensor_data

def read_serial_forever():
    try:
        with serial.Serial(RECEIVER_PORT, BAUDRATE, timeout=1) as ser:
            print(f"[RECEIVER] Listening on {RECEIVER_PORT}")
            while True:
                try:
                    line = ser.readline().decode("utf-8").strip()
                    if line:
                        print(f"[RECEIVER] Received: {line}")
                        device_id, temp_str, pres_str = line.split(",")
                        temperature = float(temp_str)
                        pressure = float(pres_str)
                        insert_sensor_data(device_id, temperature, pressure)
                except Exception as e:
                    print(f"[PARSING ERROR] {e}")
    except Exception as e:
        print(f"[SERIAL OPEN ERROR] {e}")
