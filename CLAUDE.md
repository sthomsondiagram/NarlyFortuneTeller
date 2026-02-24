# Narly Fortune Teller — AI Context

## What this is
A coin-operated AI fortune teller for festivals. Physical pipeline: Coin → Mic → Speech-to-Text → OpenAI → Thermal Printer. Arduino handles coin detection and LEDs; Python handles everything else.

## Key entry points
- `serial_trigger.py` — main orchestrator. Run with `--mode simulate --dry-run` for testing.
- `app.py` — standalone test, skips coin and mic.
- Both accept `--persona <name>` and `--list-personas`.

## Architecture
- `config_loader.py` — `load_config(persona)` reads `personas/<name>/content.json` and loads its `prompts.md`. Paths resolve relative to the file, not cwd.
- `ai_client.py` — call `init_ai(persona)` at startup, then `get_ai_response(question)`.
- `formatters.py` — `render_ticket(message, config)` formats for 32-char thermal printer.
- `led_client.py` — sends `START <mode>` / `STOP` to Arduino over serial. Degrades gracefully if Arduino not connected.

## Personas
Live in `personas/<name>/content.json` + `prompts.md`. Current personas: `default` (general), `umbraco-2025` (Umbraco festival). Default persona is always the fallback.

## Arduino serial protocol
- Arduino → Python: `COIN X` (coin inserted)
- Python → Arduino: `START <mode>`, `STOP`
- Baud: 115200. Port: `/dev/cu.usbmodem143101` (auto-detected if not specified).

## V2 upgrade status
See `docs/v2-upgrade-plan.md` for the full plan. Current status:
- Phase 1 (personas + code reorg): **COMPLETE**
- Phase 2 (Arduino LEDs, PIR sensor, toggle switch): **NOT STARTED**
- Phase 3 (hardening, Raspberry Pi deployment): **NOT STARTED**

## User notes
- Owner is new to Arduino, Raspberry Pi, and Python — explain clearly.
- Phased approach: complete and verify one phase before starting the next.
- Python venv: `/Users/dkardys/Sites/fortune-service/.venv/`
