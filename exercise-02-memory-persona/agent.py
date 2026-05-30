"""
Exercise 02 - Memory & Persona
================================
New concepts vs Exercise 01:
  1. System prompt  — give the agent a fixed identity/role
  2. Conversation history — send all past messages so agent remembers context
"""

import sys
import os
import textwrap
import requests

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ── Venv guard ──────────────────────────────
def _check_venv():
    inside = (hasattr(sys, "real_prefix") or
              (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix))
    if not inside:
        print("\n  ERROR: No virtual environment detected.")
        print("\n  python -m venv venv")
        print("  venv\\Scripts\\activate   # Windows")
        print("  pip install -r requirements.txt\n")
        sys.exit(1)
_check_venv()

# ── Config ───────────────────────────────────
API_KEY  = "a6eb413e-5c42-4420-87c0-f59b2a4e5a84"
BASE_URL = "http://localhost:6655/anthropic/v1"
MODEL    = "claude-sonnet-4-6"
HEADERS  = {
    "x-api-key": API_KEY,
    "content-type": "application/json",
    "anthropic-version": "2023-06-01",
}

# NEW: The system prompt gives the agent a persistent identity
SYSTEM_PROMPT = (
    "You are Alex, a friendly AI tutor who explains technology simply and clearly. "
    "You remember everything said in this conversation and refer back to it naturally."
)

try:
    TERM_WIDTH = min(os.get_terminal_size().columns, 80)
except OSError:
    TERM_WIDTH = 80

# ── Display helpers ──────────────────────────
def print_banner():
    b = "─" * TERM_WIDTH
    print(f"\n{b}")
    print("  Exercise 02 — Memory & Persona".center(TERM_WIDTH))
    print("  System prompt + conversation history".center(TERM_WIDTH))
    print(b)
    print(f"  Persona : {SYSTEM_PROMPT[:60]}...")
    print(f"  Model   : {MODEL}")
    print(f"  Quit    : type 'quit' or Ctrl+C")
    print(b + "\n")

def print_user(text):
    print(f"\n  You\n  {'┄' * (TERM_WIDTH-4)}")
    for line in textwrap.wrap(text, TERM_WIDTH-4) or [text]:
        print(f"  {line}")
    print()

def print_agent(text):
    b = "─" * TERM_WIDTH
    print(b + "\n  Agent\n  " + "┄" * (TERM_WIDTH-4))
    for para in text.strip().split("\n"):
        if not para.strip():
            print()
        else:
            for line in textwrap.wrap(para, TERM_WIDTH-4) or [para]:
                print(f"  {line}")
    print(b + "\n")

def print_info(text):
    print(f"  \033[90m{text}\033[0m")  # grey

def print_error(msg):
    print(f"\n  ✖  {msg}\n")

# ── Core function ────────────────────────────
def ask_agent(user_message: str, history: list) -> tuple[str, list]:
    """
    Send user_message along with the full conversation history.
    Returns (reply, updated_history).

    The KEY difference from Exercise 01:
      - We pass `system` (the persona)
      - We pass ALL previous messages in `messages`
    """
    # Add new user message to history
    history = history + [{"role": "user", "content": user_message}]

    payload = {
        "model":      MODEL,
        "max_tokens": 1024,
        "system":     SYSTEM_PROMPT,   # ← NEW: persistent persona
        "messages":   history,         # ← NEW: full history, not just 1 message
    }

    response = requests.post(f"{BASE_URL}/messages", headers=HEADERS, json=payload)
    response.raise_for_status()

    reply = response.json()["content"][0]["text"]

    # Save assistant reply so next turn includes it
    history = history + [{"role": "assistant", "content": reply}]
    return reply, history

# ── Main ─────────────────────────────────────
def main():
    print_banner()
    history = []  # Starts empty; grows with each turn

    try:
        while True:
            user_input = input("  › ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("quit", "exit", "q"):
                print(f"\n{'Goodbye!':^{TERM_WIDTH}}\n")
                break

            print_user(user_input)
            print_info(f"  History length: {len(history)} messages")

            try:
                reply, history = ask_agent(user_input, history)
                print_agent(reply)
            except requests.exceptions.ConnectionError:
                print_error("Cannot reach the API. Is the proxy running on localhost:6655?")
            except requests.exceptions.HTTPError as e:
                print_error(f"API error: {e}")

    except KeyboardInterrupt:
        print("\n\n  Interrupted. Goodbye!\n")

if __name__ == "__main__":
    main()
