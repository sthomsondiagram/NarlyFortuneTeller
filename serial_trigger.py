# serial_trigger.py
import serial
import sys
import re

PORT = "/dev/cu.usbmodem143101"  # Change to your Arduino port, e.g. "COM4" on Windows
BAUD = 115200

def find_port():
    # If you know the exact device, set PORT = "/dev/tty.usbmodemXYZ" or "COM4".
    # Otherwise, do a small probe.
    try:
        import serial.tools.list_ports
        for p in serial.tools.list_ports.comports():
            if "Arduino" in (p.description or "") or "usbmodem" in (p.device or ""):
                return p.device
    except Exception:
        pass
    return None

def on_coin(pulses: int):
    print(f"[coin] pulses={pulses}")
    # ↓ Trigger whatever you need here
    # start_leds()
    # start_recording()
    # enqueue_job("coin_inserted", {"pulses": pulses})
    # etc.

def main():
    global PORT
    if not PORT:
        PORT = find_port()
    if not PORT:
        print("Could not auto-detect serial port. Set PORT variable or pass as argv[1].")
        if len(sys.argv) > 1:
            PORT = sys.argv[1]
        else:
            sys.exit(1)

    print(f"Listening on {PORT} @ {BAUD}…")
    ser = serial.Serial(PORT, BAUD, timeout=1)

    # Read newline-terminated messages from Arduino
    line_re = re.compile(r"^\s*COIN\s+(\d+)\s*$")

    try:
        while True:
            raw = ser.readline().decode("utf-8", errors="ignore")
            if not raw:
                continue
            raw = raw.strip()
            m = line_re.match(raw)
            if m:
                pulses = int(m.group(1))
                on_coin(pulses)
            else:
                # Optionally log any other Arduino messages for debugging
                # print(f"[serial] {raw}")
                pass
    except KeyboardInterrupt:
        print("\nExiting.")
    finally:
        ser.close()

if __name__ == "__main__":
    main()
