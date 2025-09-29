import serial
import subprocess

def listen_for_coin(port="/dev/tty.usbmodem14101", baudrate=115200):
    ser = serial.Serial(port, baudrate, timeout=1)
    print(f"Listening on {port} at {baudrate} baud...")
    while True:
        try:
            line = ser.readline().decode(errors="ignore").strip()
            if line == "COIN":
                print("Coin detected! Printing fortune...")
                subprocess.run(["python", "app.py"])
        except KeyboardInterrupt:
            print("Stopping listener.")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    listen_for_coin()
