# config.py

# 시리얼 통신 설정
SENDER_PORT = "COM10"  # mock_sender가 데이터를 보내는 포트
RECEIVER_PORT = "COM11"  # serial_reader가 데이터를 수신하는 포트
BAUDRATE = 9600

# 임계값 설정
TEMP_THRESHOLD = 70.0  # danger 기준 온도

# SQLite DB 설정
DB_PATH = "data.db"
