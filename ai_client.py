import os
from dotenv import load_dotenv
from config_loader import load_config
load_dotenv()

# Module-level config cache -- set by init_ai() or lazily on first call
_config = None


def init_ai(persona: str = "default"):
    """Pre-load config for a specific persona. Call once at startup."""
    global _config
    _config = load_config(persona)


def get_ai_response(question: str) -> str:
    """Generate a fortune using the AI provider."""
    cfg = _config or load_config()

    provider = os.getenv("AI_PROVIDER", "openai").lower()
    system_prompt = cfg["system_prompt"]
    max_chars = cfg["style_rules"]["max_chars"]

    if provider == "openai":
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        prompt = f"{question}\n\n(Keep it under {max_chars} characters.)"
        resp = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=1500
        )
        raw = resp.choices[0].message.content.strip()
        text = raw.replace("You are trained on data up to October 2023.", "").strip()
        return text[:max_chars]

    raise NotImplementedError("Add your AI provider in ai_client.py")
