# Fortune Service (Narly Prototype)

This is the **Coin → Mic → AI → Print pipeline** for Narly the Narwhal.
When a coin is inserted, Narly listens for a spoken question, gets a response from an AI model, formats it into a fortune, and prints it to a thermal printer.

## Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/sthomsondiagram/NarlyFortuneTeller.git
cd fortune-service
```

### 2. Set up Python environment
```bash
python3 -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure environment
Copy `.env.example` → `.env` and edit with your API keys and printer configuration.

### 4. Run the orchestrator

**For developers without hardware (simulation mode):**
```bash
# Test the full flow without Arduino - press ENTER to simulate coin insertion
python serial_trigger.py --mode simulate --dry-run

# Auto-trigger coins every 10 seconds for continuous testing
python serial_trigger.py --mode simulate --auto --interval 10 --dry-run
```

**With hardware (real Arduino + coin acceptor):**
```bash
# Test with dry-run (shows output without printing)
python serial_trigger.py --mode hardware --dry-run

# Production mode (actually prints to thermal printer)
python serial_trigger.py --mode hardware

# Specify custom serial port
python serial_trigger.py --mode hardware --port /dev/cu.usbmodem143101
```

---

## How It Works

The orchestrator (`serial_trigger.py`) coordinates the full fortune-telling flow:

1. **Coin inserted** → Arduino sends `COIN X` message over serial (115200 baud)
2. **Microphone activates** → Records spoken question (15s timeout)
3. **Speech-to-text** → Transcribes audio via Google Web Speech API (`speech_recognition` library)
4. **AI generates fortune** → Calls OpenAI API (30s timeout)
5. **Prints fortune** → Outputs to thermal printer (10s timeout)
6. **Fallback handling** → If any step fails, prints "Narly drifted off..."

### Key Features

- ✅ **Timeout protection** - prevents hanging on mic/AI/printer failures
- ✅ **Error resilience** - fallback printing when things go wrong
- ✅ **Simulation mode** - test without Arduino hardware
- ✅ **Dry-run mode** - preview output without printing
- ✅ **Single-process** - no subprocess complexity, easier debugging

---

## Alternative: Standalone Testing

For quick tests without the full orchestrator:

```bash
# Test with a specific question (no mic, no coin)
python app.py --question "Will I meet a dragon today?" --dry-run

# Use default question from content.json
python app.py --dry-run
```

---

## Editing Persona & Style
Non-devs can edit `prompts.md` to adjust the tone, rules, and header/footer.

---

## Next Steps
- Add sound/LED feedback in Arduino when printing starts.
- Optional: Wrap the orchestrator in a simple HTTP API for remote debugging.

---

## License
MIT
