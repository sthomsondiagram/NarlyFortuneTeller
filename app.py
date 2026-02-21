import argparse

from ai_client import get_ai_response, init_ai
from formatters import render_ticket
from print_client import print_ticket
from config_loader import load_config, list_personas

def main():
    parser = argparse.ArgumentParser(description="Narly fortune (standalone test).")
    parser.add_argument("--question", help="Override the default question.")
    parser.add_argument("--dry-run", action="store_true", help="Show output without printing.")
    parser.add_argument(
        "--persona",
        default="default",
        help="Persona to use (directory name under personas/). Default: 'default'"
    )
    parser.add_argument(
        "--list-personas",
        action="store_true",
        help="List available personas and exit"
    )
    args = parser.parse_args()

    if args.list_personas:
        print("Available personas:")
        for name in list_personas():
            print(f"  {name}")
        return

    cfg = load_config(args.persona)
    init_ai(args.persona)
    print(f"Persona: {cfg['_persona_name']}")

    question = args.question or cfg.get("default_question", "What is my fortune?")
    ai_text = get_ai_response(question)
    ticket = render_ticket(ai_text, cfg)

    if args.dry_run:
        print(ticket)
    else:
        print_ticket(ticket)
        print("Printed.")

if __name__ == "__main__":
    main()
