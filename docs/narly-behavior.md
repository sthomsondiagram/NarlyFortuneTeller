Narly: Behavior & Technical Brief
=================================

1\. Behavior-Driven Overview (what users experience)
----------------------------------------------------

**When a festival guest interacts with Narly...**

-   **When** a coin is inserted,\
    **Then** Narly's lights shift from idle shimmer to a glowing "oracle pulse."\
    **And** a short sound effect plays, signaling that Narly is listening.

-   **When** the guest asks a question aloud,\
    **Then** the microphone (MXL AC-404 or system default) records their voice for a short window.

-   **When** Narly has "heard enough" (voice activity ends or timeout),\
    **Then** he quietly ponders (sound effect continues).

-   **Then** a printed fortune emerges from the receipt printer,\
    **And** the lights fade back to idle shimmer.

-   **If** something goes wrong (no mic, printer error, API fails),\
    **Then** Narly still prints a fallback slip inviting the guest to try again.

* * * * *

2\. Hardware & Key Libraries
----------------------------

**Core Hardware**

-   **Coin Acceptor:** HX-916 (pulse output, 9V powered, shared ground with Arduino).

-   **Microcontroller:** Arduino Uno (ATmega328P).

-   **LEDs:** WS2812B (Neopixel strip, powered by external 5V supply).

-   **Microphone:** MXL AC-404 USB Boundary Condenser Mic (app should also run using default system audio input as fallback).

-   **Printer:** Maikrt Embedded 58mm Thermal Receipt Printer (USB, ESC/POS protocol).

-   **Laptop (macOS):** runs orchestration app (`fortune-service` repo).

**Key Software / Libraries**

-   **Arduino side**

    -   `FastLED` (for WS2812B control).

    -   Standard `Arduino.h` (interrupts, millis).

-   **Python side**

    -   `pyserial` (serial comms).

    -   `speech_recognition` (mic capture and transcription via Google Web Speech API).

    -   `openai` (AI responses).

    -   `python-escpos` or system `lpr` (ESC/POS printing).

    -   `argparse` (CLI).

* * * * *

3\. System Roles
----------------

### Arduino Uno (real-time I/O)

-   Detects coin pulses via interrupt on HX-916 signal wire.

-   Debounces and emits **exactly one `COIN X` message per coin** (where X is the pulse count).

-   Drives all **LED animations** locally (idle shimmer + oracle pulse).

-   Sends serial messages to laptop over USB (115200 baud, newline-terminated plain text).

### Laptop (Python app in `fortune-service/NarlyFortuneTeller/`)

-   **Serial listener:** waits for `COIN X` messages (e.g., `COIN 1`).

-   **Audio capture:** starts mic recording on coin event; stops on voice activity end or timeout.

-   **Speech recognition:** transcribes audio via Google Web Speech API (`speech_recognition` library).

-   **Fortune generation:** builds a prompt and calls the OpenAI API.

-   **Printing:** formats the fortune and sends to thermal printer (via USB escpos or system lpr).

-   **Error handling:** if STT/LLM/printer fails, prints a fallback slip.

* * * * *

4\. Event Flow (machine's perspective)
--------------------------------------

1.  **Idle**

    -   Arduino runs idle LED shimmer.

    -   Laptop app waits on serial.

2.  **Coin Inserted**

    -   Arduino detects valid pulse → sends:

        `COIN 1`

    -   LEDs switch to "oracle pulse."

3.  **Laptop on Coin Event**

    -   Plays sound effect (sfx_magic.mp3) signaling mic is ready.

    -   Captures audio from MXL AC-404 (or system input).

4.  **Fortune Generation**

    -   Plays sound effect (sfx_generate.mp3) signaling AI is working.

    -   Audio → Google Web Speech API → transcript.

    -   Transcript + prompt → OpenAI → fortune text.

5.  **Printing**

    -   Fortune text → ESC/POS → USB thermal printer.

6.  **Fallbacks**

    -   If error → print "Narly drifted off in the currents---try again in a moment."

7.  **Reset**

    -   LEDs return to idle shimmer.