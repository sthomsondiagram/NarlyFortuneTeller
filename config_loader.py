from pathlib import Path
import json

def load_config(config_path: str = "content.json"):
    """Load config and, if present, replace system_prompt_file with system_prompt text.
    Backward-compatible if system_prompt is still inline.
    """
    p = Path(config_path)
    cfg = json.loads(p.read_text(encoding="utf-8"))

    # If a file reference is provided, load it
    prompt_file = cfg.get("system_prompt_file")
    if prompt_file:
        prompt_path = (p.parent / prompt_file).resolve()
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
        cfg["system_prompt"] = prompt_path.read_text(encoding="utf-8")

    # Basic validation
    if "system_prompt" not in cfg or not cfg["system_prompt"].strip():
        raise ValueError("system_prompt is empty after loading. Check prompts.md or content.json.")

    return cfg
