# led_client.py
import time
try:
    import serial
except Exception:
    serial = None

class LedClient:
    def __init__(self, port="/dev/tty.usbmodem143101", baud=115200):
        self._ok = False
        self._ser = None
        if serial is None:
            return
        try:
            self._ser = serial.Serial(port, baudrate=baud, timeout=1)
            time.sleep(2.0)  # Uno resets on open
            self._ok = True
        except Exception:
            self._ok = False

    def start(self, mode="GLOW"):
        if self._ok:
            try:
                self._ser.write((f"START {mode}\n").encode("utf-8"))
            except Exception:
                self._ok = False

    def stop(self):
        if self._ok:
            try:
                self._ser.write(b"STOP\n")
            except Exception:
                self._ok = False

    def close(self):
        try:
            if self._ser:
                self._ser.close()
        except Exception:
            pass
