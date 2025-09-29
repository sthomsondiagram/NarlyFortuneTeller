# Fortune Service (Narly Prototype)

This is the **AI → Print pipeline** for Narly the Narwhal.  
It takes a question (currently hard-coded), gets a response from an AI model, formats it into a fortune, and prints it to a thermal printer.

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

### 4. Run a test
Preview output without printing:
```bash
python app.py --dry-run
```

Print to your thermal printer:
```bash
python app.py
```

Override the question:
```bash
python app.py --question "Will I meet a dragon today?"
```

---

## Triggers

### A. Serial (Coin Acceptor / Arduino)
When Arduino sends `COIN` over the serial port, the script will run `app.py` automatically.

```bash
python serial_trigger.py
```

Default port is `/dev/tty.usbmodem14101` at `115200` baud.  
Edit inside `serial_trigger.py` if your Arduino uses a different port or baud rate.

### B. Microphone (Speech-to-Text)
Capture spoken question via USB mic → transcribe → print.

```bash
python mic_trigger.py
```

- Uses the `speech_recognition` library with Google STT (free).  
- Requires internet connection.  
- Edit `mic_trigger.py` if you want to swap providers.  

Press **Ctrl+C** to stop listening.

### C. CLI (Hard-Coded or Manual Input)
```bash
python app.py
python app.py --question "What is my fortune for today?"
```

---

## Editing Persona & Style
Non-devs can edit `content.json` to adjust the tone, rules, and header/footer.

---

## Next Steps
- Integrate the **coin acceptor** into Arduino and send "COIN" messages...  
- Decide whether to use mic, coin, or both as triggers.  
- Add sound/LED feedback in Arduino when printing starts.  
- Optional: Wrap `app.py` in a simple HTTP API for remote debugging.

---

## License
MIT
