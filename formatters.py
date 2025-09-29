import textwrap
import json

def render_ticket(message: str) -> str:
    with open("content.json", "r", encoding="utf-8") as f:
        cfg = json.load(f)

    header = cfg.get("header", "")
    footer = cfg.get("footer", "")
    width = 32

    def center(line): return line.center(width)
    body = textwrap.fill(message, width=width)

    parts = []
    if header: parts += [center(header), "-" * width]
    parts += [body]
    if footer:
        parts += ["-" * width, center(footer)]
    parts += ["", ""]
    return "\n".join(parts)
