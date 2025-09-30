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

    -   `sounddevice` or `pyaudio` (mic capture).

    -   **Google Cloud Speech-to-Text** (speech recognition).

    -   `openai` or `anthropic` (AI responses, depending on provider).

    -   `python-escpos` or similar (ESC/POS printing).

    -   `typer` (CLI), `pydantic` (config), `pytest` (testing).

* * * * *

3\. System Roles
----------------

### Arduino Uno (real-time I/O)

-   Detects coin pulses via interrupt on HX-916 signal wire.

-   Debounces and emits **exactly one JSON event per coin**.

-   Drives all **LED animations** locally (idle shimmer + oracle pulse).

-   Sends serial messages to laptop over USB (9600 baud, newline-terminated JSON).

### Laptop (Python app in `fortune-service/NarlyFortuneTeller/`)

-   **Serial listener:** waits for `{"event":"coin"}` messages.

-   **Audio capture:** starts mic recording on coin event; stops on voice activity end or timeout.

-   **Speech recognition:** sends audio to Google Speech-to-Text for transcription.

-   **Fortune generation:** builds a prompt and calls the LLM API (OpenAI/Anthropic).

-   **Printing:** formats the fortune as ESC/POS commands, sends to USB thermal printer.

-   **Error handling:** if STT/LLM/printer fails, prints a fallback slip.

* * * * *

4\. Event Flow (machine's perspective)
--------------------------------------

1.  **Idle**

    -   Arduino runs idle LED shimmer.

    -   Laptop app waits on serial.

2.  **Coin Inserted**

    -   Arduino detects valid pulse → sends:

        `{"event":"coin","value":1,"ts":1730000000}`

    -   LEDs switch to "oracle pulse."

3.  **Laptop on Coin Event**

    -   Plays "thinking" SFX.

    -   Captures audio from MXL AC-404 (or system input).

4.  **Fortune Generation**

    -   Audio → Google STT → transcript.

    -   Transcript + prompt → AI → fortune text.

5.  **Printing**

    -   Fortune text → ESC/POS → USB thermal printer.

6.  **Fallbacks**

    -   If error → print "Narly drifted off in the currents---try again in a moment."

7.  **Reset**

    -   LEDs return to idle shimmer.