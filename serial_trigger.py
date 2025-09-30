# serial_trigger.py - Orchestrates the full fortune-telling flow
import serial
import sys
import re
import argparse
import json
import speech_recognition as sr
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from ai_client import get_ai_response
from formatters import render_ticket
from print_client import print_ticket
from config_loader import load_config

PORT = "/dev/cu.usbmodem143101"  # Change to your Arduino port, e.g. "COM4" on Windows
BAUD = 115200

# Timeout configuration (in seconds)
TIMEOUT_RECORDING = 15      # Max time to wait for speech input
TIMEOUT_AI = 30             # Max time for AI response
TIMEOUT_PRINT = 10          # Max time for printing

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

def record_and_transcribe():
    """Record audio from microphone and transcribe to text."""
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    print("  🎤 Listening for question...")
    try:
        with mic as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            # Improved settings to capture full questions
            recognizer.pause_threshold = 2.5  # Wait longer for natural pauses (was 1.5)
            recognizer.energy_threshold = 300  # Lower threshold for better detection
            recognizer.dynamic_energy_threshold = True  # Adapt to ambient noise
            # Increase limits to allow longer questions
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=20)

        print("  🧠 Transcribing...")
        text = recognizer.recognize_google(audio)
        print(f"  ✓ Question: {text}")
        return text
    except sr.WaitTimeoutError:
        print("  ⚠ No speech detected (timeout)")
        return None
    except sr.UnknownValueError:
        print("  ⚠ Could not understand audio")
        return None
    except sr.RequestError as e:
        print(f"  ⚠ Speech recognition error: {e}")
        return None
    except Exception as e:
        print(f"  ⚠ Microphone error: {e}")
        return None

def record_and_transcribe_with_timeout():
    """Wrapper to enforce timeout on recording/transcription."""
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(record_and_transcribe)
        try:
            return future.result(timeout=TIMEOUT_RECORDING)
        except TimeoutError:
            print(f"  ⚠ Recording timeout ({TIMEOUT_RECORDING}s exceeded)")
            return None
        except Exception as e:
            print(f"  ⚠ Unexpected error during recording: {e}")
            return None

def generate_fortune(question: str) -> str:
    """Call AI to generate fortune response."""
    print("  🔮 Generating fortune...")
    try:
        fortune = get_ai_response(question)
        print(f"  ✓ Fortune generated ({len(fortune)} chars)")
        return fortune
    except Exception as e:
        print(f"  ⚠ AI error: {e}")
        return None

def generate_fortune_with_timeout(question: str):
    """Wrapper to enforce timeout on AI generation."""
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(generate_fortune, question)
        try:
            return future.result(timeout=TIMEOUT_AI)
        except TimeoutError:
            print(f"  ⚠ AI timeout ({TIMEOUT_AI}s exceeded)")
            return None
        except Exception as e:
            print(f"  ⚠ Unexpected error during AI generation: {e}")
            return None

def print_fortune(fortune: str, dry_run: bool = False):
    """Format and print fortune ticket."""
    print("  🖨️  Printing fortune...")
    try:
        ticket = render_ticket(fortune)
        if dry_run:
            print("\n--- DRY RUN OUTPUT ---")
            print(ticket)
            print("--- END DRY RUN ---\n")
        else:
            print_ticket(ticket)
            print("  ✓ Printed successfully")
    except Exception as e:
        print(f"  ⚠ Print error: {e}")
        raise

def print_fortune_with_timeout(fortune: str, dry_run: bool = False):
    """Wrapper to enforce timeout on printing."""
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(print_fortune, fortune, dry_run)
        try:
            future.result(timeout=TIMEOUT_PRINT)
        except TimeoutError:
            print(f"  ⚠ Print timeout ({TIMEOUT_PRINT}s exceeded)")
            raise
        except Exception as e:
            print(f"  ⚠ Unexpected error during printing: {e}")
            raise

def print_fallback(dry_run: bool = False):
    """Print fallback message when something goes wrong."""
    cfg = load_config("content.json")
    fallback_msg = "Narly drifted off in the currents... try again in a moment."
    ticket = render_ticket(fallback_msg)

    print("  ⚠ Printing fallback message...")
    if dry_run:
        print("\n--- FALLBACK (DRY RUN) ---")
        print(ticket)
        print("--- END FALLBACK ---\n")
    else:
        try:
            # Use timeout for fallback too
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(print_ticket, ticket)
                future.result(timeout=TIMEOUT_PRINT)
            print("  ✓ Fallback printed")
        except TimeoutError:
            print(f"  ✗ Fallback print timeout ({TIMEOUT_PRINT}s) - showing on console:")
            print("\n" + ticket + "\n")
        except Exception as e:
            print(f"  ✗ Could not print fallback: {e}")
            print("  → Showing fallback on console instead:")
            print("\n" + ticket + "\n")

def on_coin_event(pulses: int, dry_run: bool = False):
    """
    Main orchestration: triggered when coin is inserted.
    Flow: coin → record → transcribe → generate → print
    All steps have timeout protection.
    """
    print(f"\n💰 [COIN EVENT] pulses={pulses}")

    try:
        # Step 1: Record and transcribe (with timeout)
        question = record_and_transcribe_with_timeout()
        if not question:
            cfg = load_config("content.json")
            question = cfg.get("default_question", "What is my fortune?")
            print(f"  → Using default question: {question}")

        # Step 2: Generate fortune (with timeout)
        fortune = generate_fortune_with_timeout(question)
        if not fortune:
            print_fallback(dry_run)
            return

        # Step 3: Print (with timeout)
        try:
            print_fortune_with_timeout(fortune, dry_run)
            print("✓ Fortune cycle complete\n")
        except Exception:
            # If printing fortune fails, try fallback
            print_fallback(dry_run)

    except Exception as e:
        print(f"  ✗ Unexpected error in coin event handler: {e}")
        print_fallback(dry_run)

def listen_serial_mode(port: str, dry_run: bool = False):
    """Listen for COIN X messages from Arduino on serial port."""
    print(f"🔌 Hardware mode: Listening on {port} @ {BAUD}...")
    print("   Waiting for coin insertion...\n")

    ser = serial.Serial(port, BAUD, timeout=1)
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
                on_coin_event(pulses, dry_run)
            else:
                # Optionally log other Arduino messages for debugging
                if raw:  # Only log non-empty messages
                    print(f"[arduino] {raw}")
    except KeyboardInterrupt:
        print("\n\n🛑 Exiting serial mode.")
    finally:
        ser.close()

def simulate_mode(dry_run: bool = False, auto: bool = False, interval: int = 10):
    """Simulate coin events for testing without hardware."""
    print("🎮 Simulation mode")
    if auto:
        print(f"   Auto-triggering every {interval} seconds (Ctrl+C to stop)\n")
        import time
        try:
            while True:
                print("[AUTO] Simulating coin insertion...")
                on_coin_event(pulses=1, dry_run=dry_run)
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n\n🛑 Exiting simulation mode.")
    else:
        print("   Press ENTER to simulate coin insertion (Ctrl+C to stop)\n")
        try:
            while True:
                input("Press ENTER for coin → ")
                on_coin_event(pulses=1, dry_run=dry_run)
        except KeyboardInterrupt:
            print("\n\n🛑 Exiting simulation mode.")

def main():
    global PORT

    parser = argparse.ArgumentParser(
        description="Narly Fortune Orchestrator - coordinates coin → mic → AI → print flow"
    )
    parser.add_argument(
        "--mode",
        choices=["hardware", "simulate"],
        default="hardware",
        help="Run mode: 'hardware' for real Arduino, 'simulate' for testing without hardware"
    )
    parser.add_argument(
        "--port",
        default=PORT,
        help=f"Serial port for hardware mode (default: {PORT})"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show output without actually printing to thermal printer"
    )
    parser.add_argument(
        "--auto",
        action="store_true",
        help="In simulate mode, auto-trigger coins at regular intervals"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=10,
        help="Seconds between auto-triggered coins in simulate mode (default: 10)"
    )

    args = parser.parse_args()

    if args.mode == "hardware":
        port = args.port or find_port()
        if not port:
            print("❌ Could not auto-detect serial port.")
            print("   Use --port to specify manually, e.g.: --port /dev/cu.usbmodem143101")
            sys.exit(1)
        listen_serial_mode(port, dry_run=args.dry_run)
    else:
        simulate_mode(dry_run=args.dry_run, auto=args.auto, interval=args.interval)

if __name__ == "__main__":
    main()