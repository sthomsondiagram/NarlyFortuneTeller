import os
import json
from dotenv import load_dotenv
from config_loader import load_config
load_dotenv()

def get_ai_response(question: str) -> str:
    provider = os.getenv("AI_PROVIDER", "openai").lower()
    cfg = load_config("content.json")

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
            max_tokens=300
        )
        #text = resp.choices[0].message.content.strip()
        raw = resp.choices[0].message.content.strip()
        text = raw.replace("You are trained on data up to\nOctober 2023.", "").strip()
        return text[:max_chars]

    raise NotImplementedError("Add your AI provider in ai_client.py")
