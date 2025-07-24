import sys
import os
import sqlite3
import threading
import serial
from datetime import datetime
from PyQt5 import QtWidgets, QtCore

# 설정값 기본 경로
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.py")
DB_PATH = "data.db"

# 기본값 설정 (config.py에서 불러옴)
SENDER_PORT = "COM10"
RECEIVER_PORT = "COM11"
BAUDRATE = 9600
TEMP_THRESHOLD = 70.0

receiver_thread = None
stop_event = threading.Event()

def load_ports_from_config():
    global SENDER_PORT, RECEIVER_PORT
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("SENDER_PORT"):
                    SENDER_PORT = line.split("=")[1].split("#")[0].strip().strip('"')
                elif line.startswith("RECEIVER_PORT"):
                    RECEIVER_PORT = line.split("=")[1].split("#")[0].strip().strip('"')
    except Exception as e:
        print(f"[CONFIG LOAD ERROR] {e}")

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

def fetch_latest_logs(limit=10):
    try:
        with sqlite3.connect(DB_PATH, timeout=5.0) as conn:
            c = conn.cursor()
            c.execute('''
                SELECT timestamp, device_id, value, status_flag
                FROM temperature_logs
                ORDER BY id DESC
                LIMIT ?
            ''', (limit,))
            return c.fetchall()[::-1]
    except sqlite3.OperationalError as e:
        print(f"[DB READ ERROR] {e}")
        return []

def receiver_loop():
    global RECEIVER_PORT, BAUDRATE
    try:
        with serial.Serial(RECEIVER_PORT, BAUDRATE, timeout=1) as ser:
            print(f"[RECEIVER] Listening on {RECEIVER_PORT}")
            while not stop_event.is_set():
                try:
                    line = ser.readline().decode("utf-8").strip()
                    if line:
                        print(f"[RECEIVER] Received: {line}")
                        device_id, value_str = line.split(",")
                        value = float(value_str)
                        status = "danger" if value > TEMP_THRESHOLD else "normal"
                        insert_temperature(device_id, value, status)
                except Exception as e:
                    print(f"[RECEIVER ERROR] {e}")
    except Exception as e:
        print(f"[RECEIVER OPEN ERROR] {e}")

class TemperatureMonitorApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Temperature Monitor GUI")
        self.setGeometry(100, 100, 700, 400)

        # UI 구성
        central_widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()

        self.sender_input = QtWidgets.QLineEdit()
        self.receiver_input = QtWidgets.QLineEdit()
        self.sender_input.setPlaceholderText("SENDER_PORT (예: COM10)")
        self.receiver_input.setPlaceholderText("RECEIVER_PORT (예: COM11)")

        layout.addWidget(self.sender_input)
        layout.addWidget(self.receiver_input)

        self.save_button = QtWidgets.QPushButton("포트 설정 저장 및 수신 시작")
        self.save_button.clicked.connect(self.save_ports_and_restart_receiver)
        layout.addWidget(self.save_button)

        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Timestamp", "Device ID", "Value", "Status"])
        layout.addWidget(self.table)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_table)
        self.timer.start(3000)

        load_ports_from_config()
        self.sender_input.setText(SENDER_PORT)
        self.receiver_input.setText(RECEIVER_PORT)
        self.start_receiver_thread()
        self.update_table()

    def save_ports_and_restart_receiver(self):
        global SENDER_PORT, RECEIVER_PORT
        sender = self.sender_input.text().strip()
        receiver = self.receiver_input.text().strip()

        if not sender or not receiver:
            QtWidgets.QMessageBox.warning(self, "입력 오류", "포트를 모두 입력하세요.")
            return

        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                lines = f.readlines()

            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                for line in lines:
                    if line.startswith("SENDER_PORT"):
                        f.write(f'SENDER_PORT = "{sender}"  # mock_sender가 데이터를 보내는 포트\n')
                    elif line.startswith("RECEIVER_PORT"):
                        f.write(f'RECEIVER_PORT = "{receiver}"  # serial_reader가 데이터를 수신하는 포트\n')
                    else:
                        f.write(line)

            SENDER_PORT = sender
            RECEIVER_PORT = receiver
            self.restart_receiver_thread()

            QtWidgets.QMessageBox.information(self, "완료", "포트 설정이 저장되고 수신이 재시작되었습니다.")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "오류", f"설정 저장 중 오류 발생: {e}")

    def update_table(self):
        data = fetch_latest_logs(10)
        self.table.setRowCount(len(data))
        for row_idx, row in enumerate(data):
            for col_idx, value in enumerate(row):
                item = QtWidgets.QTableWidgetItem(str(value))
                if col_idx == 3 and value == "danger":
                    item.setForeground(QtCore.Qt.red)
                self.table.setItem(row_idx, col_idx, item)

    def start_receiver_thread(self):
        global receiver_thread
        stop_event.clear()
        receiver_thread = threading.Thread(target=receiver_loop, daemon=True)
        receiver_thread.start()

    def restart_receiver_thread(self):
        stop_event.set()
        if receiver_thread and receiver_thread.is_alive():
            receiver_thread.join(timeout=2)
        self.start_receiver_thread()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = TemperatureMonitorApp()
    window.show()
    sys.exit(app.exec_())
