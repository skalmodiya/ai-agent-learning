"""
Exercise 07 - Structured Output
=================================
New concept: force the AI to respond with a specific JSON schema.
"""

import sys, os, json, requests

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def _check_venv():
    inside = (hasattr(sys, "real_prefix") or
              (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix))
    if not inside:
        print("\n  ERROR: No virtual environment detected.")
        print("  python -m venv venv && venv\\Scripts\\activate\n"); sys.exit(1)
_check_venv()

API_KEY  = "a6eb413e-5c42-4420-87c0-f59b2a4e5a84"
BASE_URL = "http://localhost:6655/anthropic/v1"
MODEL    = "claude-sonnet-4-6"
HEADERS  = {"x-api-key": API_KEY, "content-type": "application/json", "anthropic-version": "2023-06-01"}

try:
    TERM_WIDTH = min(os.get_terminal_size().columns, 80)
except OSError:
    TERM_WIDTH = 80

SCHEMA_TOOL = {
    "name": "save_analysis",
    "description": "Save structured text analysis. You MUST call this tool.",
    "input_schema": {
        "type": "object",
        "properties": {
            "summary":   {"type": "string"},
            "sentiment": {"type": "string", "enum": ["positive","negative","mixed","neutral"]},
            "score":     {"type": "number", "description": "-1.0 to 1.0"},
            "keywords":  {"type": "array", "items": {"type": "string"}},
            "pros":      {"type": "array", "items": {"type": "string"}},
            "cons":      {"type": "array", "items": {"type": "string"}},
        },
        "required": ["summary","sentiment","score","keywords"],
    },
}

def print_banner():
    b = "─" * TERM_WIDTH
    print(f"\n{b}")
    print("  Exercise 07 — Structured Output".center(TERM_WIDTH))
    print("  Input any text → get structured JSON analysis".center(TERM_WIDTH))
    print(b)
    print("  Try: 'The new phone is amazing but expensive'")
    print(b + "\n")

def print_result(data: dict):
    b = "─" * TERM_WIDTH
    print(b + "\n  Structured Analysis\n  " + "┄"*(TERM_WIDTH-4))
    sentiment_colour = {"positive":"\033[32m","negative":"\033[31m","mixed":"\033[33m","neutral":"\033[37m"}
    sc = sentiment_colour.get(data.get("sentiment",""), "")
    print(f"  Summary   : {data.get('summary','')}")
    print(f"  Sentiment : {sc}{data.get('sentiment','')}\033[0m  (score: {data.get('score',0):.2f})")
    print(f"  Keywords  : {', '.join(data.get('keywords',[]))}")
    if data.get("pros"):  print(f"  Pros      : {', '.join(data['pros'])}")
    if data.get("cons"):  print(f"  Cons      : {', '.join(data['cons'])}")
    print(b + "\n")

def print_error(msg): print(f"\n  ✖  {msg}\n")

def analyze(text: str) -> dict:
    payload = {
        "model": MODEL, "max_tokens": 1024,
        "system": "Analyze the input text. You MUST call save_analysis with structured results.",
        "tools": [SCHEMA_TOOL],
        "tool_choice": {"type": "tool", "name": "save_analysis"},
        "messages": [{"role":"user","content":text}],
    }
    r = requests.post(f"{BASE_URL}/messages", headers=HEADERS, json=payload)
    r.raise_for_status()
    for block in r.json()["content"]:
        if block.get("type") == "tool_use" and block["name"] == "save_analysis":
            return block["input"]
    return {}

def main():
    print_banner()
    try:
        while True:
            user_input = input("  Enter text to analyze › ").strip()
            if not user_input: continue
            if user_input.lower() in ("quit","exit","q"):
                print(f"\n{'Goodbye!':^{TERM_WIDTH}}\n"); break
            try:
                result = analyze(user_input)
                print_result(result)
                show_json = input("  Show raw JSON? (y/n) › ").strip().lower()
                if show_json == "y":
                    print(json.dumps(result, indent=2))
                    print()
            except requests.exceptions.ConnectionError:
                print_error("Cannot reach API.")
            except requests.exceptions.HTTPError as e:
                print_error(f"API error: {e}")
    except KeyboardInterrupt:
        print("\n\n  Interrupted. Goodbye!\n")

if __name__ == "__main__":
    main()
