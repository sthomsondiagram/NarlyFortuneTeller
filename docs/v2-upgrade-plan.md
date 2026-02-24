# Narly V2 Upgrade Plan

## Context

Narly V1 was built for the Umbraco 2025 US Festival in Chicago. The persona, wiring, and deployment are all tailored to that single event (Umbraco references, laptop-based, single persona). For V2, we need to generalize Narly so he can be deployed at any event, add richer LED feedback, improve hardware resilience, and migrate from a laptop to a Raspberry Pi 4.

The work is split into 3 phases. Each phase is independently testable and shippable.

---

## Phase 1: Personas + Code Organization -- COMPLETED

**Goal:** Support multiple personas selectable at startup; reorganize the project.

**Status: DONE** (completed 2026-02-20)

### What was done

- Reorganized file layout: `personas/`, `sfx/`, `arduino/` directories created
- `config_loader.py` rewritten with `load_config(persona)` and `list_personas()`; paths resolve relative to script location
- `ai_client.py` updated with `init_ai(persona)` for startup caching
- `formatters.py` updated — `render_ticket()` accepts a `config` parameter
- `serial_trigger.py` updated — `--persona` and `--list-personas` flags; config loaded once at startup; SFX paths resolve from `_BASE_DIR / "sfx"`
- `app.py` updated — same persona flags; cleaned up commented-out code
- Default persona created (`personas/default/`) — general sea-mystic Narly, no Umbraco/Chicago
- Umbraco persona preserved (`personas/umbraco-2025/`)
- Arduino sketch (`led-test.ino`) copied into `arduino/fortune-controller/fortune-controller.ino`
- Root `content.json` and `prompts.md` deleted (replaced by persona dirs)
- `.gitignore` updated (added `*.wav`, `.DS_Store`)
- Unused Python files removed: `mic_trigger.py`, `serial_trigger-test.py`, `serial_trigger.py.backup`, `test_openai.py`, `printer_escpos_test.py`

### How to verify

```bash
python serial_trigger.py --list-personas
# Should print: default, umbraco-2025

python serial_trigger.py --mode simulate --dry-run
# Uses default persona

python serial_trigger.py --mode simulate --dry-run --persona umbraco-2025
# Uses Umbraco persona

python app.py --persona default --dry-run
# Quick standalone test
```

---

## Phase 2: Arduino + LED + PIR + Toggle Switch (requires hardware)

**Goal:** Add PIR-based presence detection, state-colored LED animations, and a physical mode switch.

**Status: NOT STARTED**

### 2a. Define state machine + serial protocol

| State | LED Command | Animation | Color (HSV) |
|---|---|---|---|
| Idle (no one nearby) | `START IDLE` | Very dim breathe | Ocean blue H=160, V=10-40 |
| Presence detected | `START SHIMMER` | Gentle twinkle | Ocean blue H=160, V=60-180 |
| Listening | `START LISTEN` | Warm solid glow | Amber H=32, V=200 |
| Thinking | `START THINK` | Random sparkle | Purple H=180-220 |
| Printing | `START PRINT` | Chase/sweep | Cyan H=128, V=255 |
| Error | `START ERROR` | 3 red flashes, auto-return | Red H=0 |

New Arduino -> Python messages:
- `PIR ON` / `PIR OFF` — presence sensor state change
- `SWITCH DEMO` / `SWITCH QUIET` / `SWITCH DEBUG` — toggle switch changed

### 2b. Rewrite Arduino sketch (`arduino/fortune-controller/fortune-controller.ino`)

**Note:** The V1 sketch has LED code but LEDs were never working (likely a wiring issue). The sketch will be rewritten from scratch for Phase 2 with fresh LED wiring and tested incrementally. Only the coin detection logic (pin 2, interrupt-based, debounced) is known-good and will be carried forward.

Starting from scratch (keeping coin detection on pin 2, LEDs on pin 6, 60 WS2812B):
- Add PIR sensor on pin 4 (HC-SR501 from Elegoo kit)
- Add two toggle switches on pins 7 & 8 (INPUT_PULLUP, active low)
  - Both off = DEMO, A on = QUIET, B on = DEBUG
- Add LED animation functions for all 7 states
- PIR auto-transitions between IDLE and SHIMMER locally on the Arduino

### 2c. Update `led_client.py`

Add convenience methods: `idle()`, `shimmer()`, `listen()`, `think()`, `printing()`, `error()`. Validate mode names against a whitelist.

### 2d. Update `serial_trigger.py`

- Parse `PIR ON/OFF` and `SWITCH` messages in the serial loop
- Track `operating_mode` from switch messages
- In QUIET mode: skip all `afplay()` calls
- In DEBUG mode: print all serial traffic
- Update `on_coin_event()` to use state-based LED commands throughout the flow

### 2e. Wiring guide

Create `arduino/README.md` with wiring diagrams for:
- PIR sensor (VCC->5V, GND->GND, OUT->pin 4)
- Toggle switches (pin 7/8 to GND, using internal pullups)
- Existing: coin acceptor (pin 2), LED data (pin 6), 5V 20A supply for LEDs

### How to verify
1. Upload sketch, open Serial Monitor — type `START SHIMMER`, `START LISTEN`, etc. and visually confirm each animation
2. Wire PIR — wave hand, confirm `PIR ON`/`PIR OFF` in Serial Monitor
3. Wire switches — flip them, confirm `SWITCH DEMO`/`SWITCH QUIET`/`SWITCH DEBUG`
4. Full integration: `python serial_trigger.py --mode hardware --dry-run` — insert coin, watch LED cycle through amber->purple->cyan->idle

---

## Phase 3: Hardening + Raspberry Pi Deployment

**Goal:** Auto-restart on crash, hardware failure resilience, migrate to Raspberry Pi 4.

**Status: NOT STARTED**

### 3a. Add proper logging (`logger.py`)

Replace all `print()` calls with `logging`. Write to both stdout and a rotating log file. Critical for debugging on a headless Pi.

### 3b. Watchdog wrapper (`watchdog_wrapper.py`)

A simple script that runs `serial_trigger.py` as a subprocess and restarts it on crash. Caps at 10 restarts, resets counter after 5 minutes of stability.

### 3c. Serial port recovery

Wrap the serial listener in a reconnection loop — if the Arduino USB disconnects, log the error, wait 5 seconds, re-detect the port, and reconnect.

### 3d. Cross-platform audio

Replace macOS-only `afplay` with a `play_sound()` function that detects the platform:
- macOS: `afplay`
- Linux/Pi: `mpg123` (mp3) or `aplay` (wav)

### 3e. Fix `requirements.txt`

Add missing dependencies: `SpeechRecognition`, `pyaudio` (needed on Pi for mic access).

### 3f. Raspberry Pi deployment

- `deploy/setup-pi.sh` — installs system packages (`portaudio19-dev`, `mpg123`, `cups`), creates venv, installs Python deps, sets up user permissions (`dialout`, `audio`, `lp` groups)
- `deploy/narly-fortune.service` — systemd unit that runs the watchdog wrapper, auto-starts on boot, logs to journald
- `deploy/README.md` — step-by-step guide: flash Pi OS, clone repo, run setup script, configure .env, connect hardware, test, enable service

### How to verify
1. Kill the main process — watchdog should restart it within 5 seconds
2. Unplug Arduino USB mid-operation — app should log error and reconnect when re-plugged
3. On Pi: `sudo systemctl start narly-fortune` then `journalctl -u narly-fortune -f` to watch logs
4. Reboot Pi — service should auto-start
5. Full end-to-end on Pi with all hardware
