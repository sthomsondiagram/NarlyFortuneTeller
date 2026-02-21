import textwrap


def sanitize_for_thermal_printer(text: str) -> str:
    """Replace Unicode characters that thermal printers can't handle with ASCII equivalents."""
    replacements = {
        '\u2018': "'",   # Left single quote
        '\u2019': "'",   # Right single quote/apostrophe
        '\u201c': '"',   # Left double quote
        '\u201d': '"',   # Right double quote
        '\u2013': '-',   # En dash
        '\u2014': '-',   # Em dash
        '\u2026': '...', # Ellipsis
        '\u2022': '*',   # Bullet point
    }
    for unicode_char, ascii_char in replacements.items():
        text = text.replace(unicode_char, ascii_char)
    return text


def render_ticket(message: str, config: dict = None) -> str:
    """Format a fortune message as a thermal printer ticket.

    If config is not provided, loads the default persona config.
    """
    if config is None:
        from config_loader import load_config
        config = load_config()

    header = config.get("header", "")
    footer = config.get("footer", "")
    width = 32

    # Sanitize all text for thermal printer
    message = sanitize_for_thermal_printer(message)
    header = sanitize_for_thermal_printer(header)
    footer = sanitize_for_thermal_printer(footer)

    def center(line): return line.center(width)
    body = textwrap.fill(message, width=width)

    # Add extra spacing at top and bottom for tear-off
    parts = ["", "", ""]  # 3 blank lines at top
    if header: parts += [center(header), "-" * width]
    parts += [body]
    if footer:
        parts += ["-" * width, center(footer)]
    parts += ["", "", "", "", ""]  # 5 blank lines at bottom for tear-off
    return "\n".join(parts)
