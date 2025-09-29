import json
import argparse

from ai_client import get_ai_response
from formatters import render_ticket
from print_client import print_ticket

def main():
    parser = argparse.ArgumentParser(description="Narly fortune (hard-coded question).")
    parser.add_argument("--question", help="Override the default hard-coded question.")
    parser.add_argument("--dry-run", action="store_true", help="Show output without printing.")
    args = parser.parse_args()

    with open("content.json", "r", encoding="utf-8") as f:
        cfg = json.load(f)

    question = args.question or cfg.get("default_question", "What is my fortune?")
    ai_text = get_ai_response(question)
    ticket = render_ticket(ai_text)

    if args.dry_run:
        print(ticket)
    else:
        #print_ticket(ticket)
        #print("Printed.")
        print(ticket)

if __name__ == "__main__":
    main()
