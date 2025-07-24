# main.py
from serial_reader import read_serial_forever

def main():
    print("[MAIN] Starting temperature monitor")
    # init_db()는 이제 제거
    read_serial_forever()

if __name__ == "__main__":
    main()
