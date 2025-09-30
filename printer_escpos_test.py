#!/usr/bin/env python3
import os
import sys
import shlex
import subprocess
from datetime import datetime

DEFAULT_QUEUES = ["Virtual_PRN", "Maikrt58", "Thermal58", "Receipt", "POS_Printer"]

def shell(cmd):
    return subprocess.run(cmd, shell=True, check=False, capture_output=True, text=True)

def find_queue():
    # 1) Respect $PRINTER if set
    env_q = os.environ.get("PRINTER")
    if env_q:
        return env_q

    # 2) Try common names
    out = shell("lpstat -p -d")
    if out.returncode == 0:
        text = out.stdout + out.stderr
        # Collect all 'printer <name>' lines
        lines = [ln.strip() for ln in text.splitlines()]
        queues = []
        for ln in lines:
            if ln.startswith("printer "):
                try:
                    queues.append(ln.split()[1])
                except Exception:
                    pass

        # Prefer default printer if listed
        for ln in lines:
            if ln.startswith("system default destination:"):
                default_q = ln.split(":", 1)[1].strip()
                if default_q:
                    return default_q

        # Try known names first if present
        for guess in DEFAULT_QUEUES:
            if guess in queues:
                return guess

        # Otherwise, fall back to the first discovered queue
        if queues:
            return queues[0]

    # Last resort: first default guess
    return DEFAULT_QUEUES[0]

def print_bytes(queue_name: str, payload: bytes):
    # Write bytes to a temp file so we can use lp -o raw reliably
    tmp_path = f"/tmp/escpos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.bin"
    with open(tmp_path, "wb") as f:
        f.write(payload)

    cmd = f'lp -d {shlex.quote(queue_name)} -o raw {shlex.quote(tmp_path)}'
    run = shell(cmd)
    if run.returncode != 0:
        raise RuntimeError(
            f"Print failed.\nCommand: {cmd}\nSTDOUT:\n{run.stdout}\nSTDERR:\n{run.stderr}"
        )

def main():
    # Build a minimal ESC/POS test
    # ESC @ (initialize), text, newlines, GS V 0 (partial cut if supported)
    fortune_text = "Narly sees your future...\n"
    if len(sys.argv) > 1:
        # Allow override from CLI
        fortune_text = " ".join(sys.argv[1:]) + "\n"

    payload = bytearray()
    payload += b"\x1b\x40"            # Initialize
    payload += fortune_text.encode("utf-8", errors="replace")
    payload += b"\n\n\n"              # Feed a few lines
    payload += b"\x1d\x56\x00"        # Partial cut (some printers: \x1d\x56\x42\x00)

    queue = find_queue()
    try:
        print(f"→ Using CUPS queue: {queue}")
        print_bytes(queue, bytes(payload))
        print("✅ Sent ESC/POS test to printer via CUPS (raw).")
        print("   If no cut: try replacing GS V 0 with GS V 66 0 in the code.")
    except Exception as e:
        print("✗ Printing failed.\n")
        print(e)
        print("\nTroubleshooting:")
        print("  • Confirm the queue name with: lpstat -p -d")
        print("  • Make sure the printer is powered and has paper.")
        print('  • Ensure it was added as a RAW queue in CUPS (http://localhost:631).')
        sys.exit(1)

if __name__ == "__main__":
    main()
