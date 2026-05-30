"""
Exercise 05 - Multi-Agent
==========================
New concept: Planner agent breaks the task, Writer agent executes it.
"""

import sys, os, textwrap, requests

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

PLANNER_SYSTEM = "You are a Planner agent. Break the task into numbered steps ONLY. No execution."
WRITER_SYSTEM  = "You are a Writer agent. Execute the given plan fully and produce polished output."

def _call(system, user_msg):
    payload = {"model": MODEL, "max_tokens": 1024, "system": system,
               "messages": [{"role": "user", "content": user_msg}]}
    r = requests.post(f"{BASE_URL}/messages", headers=HEADERS, json=payload)
    r.raise_for_status()
    return r.json()["content"][0]["text"]

def print_banner():
    b = "─" * TERM_WIDTH
    print(f"\n{b}")
    print("  Exercise 05 — Multi-Agent".center(TERM_WIDTH))
    print("  Planner ──► Writer pipeline".center(TERM_WIDTH))
    print(b + "\n")

def print_section(label, text, colour=""):
    reset = "\033[0m" if colour else ""
    b = "─" * TERM_WIDTH
    print(f"{b}\n  {colour}{label}{reset}\n  {'┄'*(TERM_WIDTH-4)}")
    for para in text.strip().split("\n"):
        if not para.strip(): print()
        else:
            for l in textwrap.wrap(para, TERM_WIDTH-4) or [para]: print(f"  {l}")
    print(b + "\n")

def print_error(msg): print(f"\n  ✖  {msg}\n")

def main():
    print_banner()
    try:
        while True:
            user_input = input("  › ").strip()
            if not user_input: continue
            if user_input.lower() in ("quit","exit","q"):
                print(f"\n{'Goodbye!':^{TERM_WIDTH}}\n"); break
            print(f"\n  \033[90mStep 1/2 — Planner thinking...\033[0m")
            try:
                plan = _call(PLANNER_SYSTEM, f"Task: {user_input}")
                print_section("Planner → Plan", plan, "\033[36m")
                print(f"  \033[90mStep 2/2 — Writer executing...\033[0m")
                result = _call(WRITER_SYSTEM, f"Plan:\n{plan}\n\nOriginal request: {user_input}")
                print_section("Writer → Final Output", result, "\033[32m")
            except requests.exceptions.ConnectionError:
                print_error("Cannot reach API.")
            except requests.exceptions.HTTPError as e:
                print_error(f"API error: {e}")
    except KeyboardInterrupt:
        print("\n\n  Interrupted. Goodbye!\n")

if __name__ == "__main__":
    main()
