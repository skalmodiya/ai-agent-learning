"""
Exercise 01 - Simple AI Agent
==============================
Goal: Understand the most basic building block of an AI Agent:
      Send a message → Get a response → Display it.

What is an AI Agent?
--------------------
An AI Agent is a program that:
  1. Perceives input (your message)
  2. Thinks (sends it to an AI model)
  3. Acts (returns a response, or does something based on it)

This exercise covers the absolute basics — one message, one response.
"""

import sys
import os
import textwrap
import requests

# Force UTF-8 output on Windows so box-drawing characters render correctly.
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ─────────────────────────────────────────────
# VENV GUARD
# Refuse to run outside a virtual environment.
# This prevents polluting your global Python installation
# and ensures every exercise is fully isolated.
# ─────────────────────────────────────────────

def _check_venv():
    inside_venv = (
        hasattr(sys, "real_prefix")                        # virtualenv
        or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix)  # venv
    )
    if not inside_venv:
        print()
        print("  ERROR: No virtual environment detected.")
        print()
        print("  Please create and activate one first:")
        print()
        print("    python -m venv venv")
        print()
        print("    # On Windows:")
        print("    venv\\Scripts\\activate")
        print()
        print("    # On Mac/Linux:")
        print("    source venv/bin/activate")
        print()
        print("  Then install dependencies:")
        print("    pip install -r requirements.txt")
        print()
        sys.exit(1)

_check_venv()


# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────

API_KEY  = "a6eb413e-5c42-4420-87c0-f59b2a4e5a84"
BASE_URL = "http://localhost:6655/anthropic/v1"
MODEL    = "claude-sonnet-4-6"

HEADERS = {
    "x-api-key":         API_KEY,
    "content-type":      "application/json",
    "anthropic-version": "2023-06-01",
}

# Terminal width used for wrapping and borders
try:
    TERM_WIDTH = min(os.get_terminal_size().columns, 80)
except OSError:
    TERM_WIDTH = 80


# ─────────────────────────────────────────────
# DISPLAY HELPERS
# These functions handle all the formatting so main() stays clean.
# ─────────────────────────────────────────────

def print_banner():
    """Print the welcome banner."""
    border = "─" * TERM_WIDTH
    print()
    print(border)
    print("  Exercise 01 — Simple AI Agent".center(TERM_WIDTH))
    print("  One message. One response. The foundation of every agent.".center(TERM_WIDTH))
    print(border)
    print(f"  Model : {MODEL}")
    print(f"  Type  : your message and press Enter")
    print(f"  Quit  : type 'quit' or press Ctrl+C")
    print(border)
    print()


def print_user(text: str):
    """Print the user's message with a label."""
    print()
    print("  You")
    print("  " + "┄" * (TERM_WIDTH - 4))
    # Wrap long lines so they stay inside the terminal width
    for line in textwrap.wrap(text, width=TERM_WIDTH - 4) or [text]:
        print(f"  {line}")
    print()


def print_agent(text: str):
    """Print the agent's reply in a clearly distinct box."""
    border = "─" * TERM_WIDTH
    print(border)
    print("  Agent")
    print("  " + "┄" * (TERM_WIDTH - 4))
    # Preserve paragraph breaks while wrapping each paragraph
    paragraphs = text.strip().split("\n")
    for para in paragraphs:
        if para.strip() == "":
            print()
        else:
            for line in textwrap.wrap(para, width=TERM_WIDTH - 4) or [para]:
                print(f"  {line}")
    print(border)
    print()


def print_error(message: str):
    """Print an error in a way that stands out."""
    print()
    print("  ✖  ERROR")
    print(f"  {message}")
    print()


# ─────────────────────────────────────────────
# THE CORE FUNCTION
# This is the heart of every AI Agent: ask → answer
# ─────────────────────────────────────────────

def ask_agent(user_message: str) -> str:
    """
    Send a message to the AI and return its reply.

    The Anthropic API expects:
      POST /messages
      {
        "model": "...",
        "max_tokens": 1024,
        "messages": [{ "role": "user", "content": "..." }]
      }

    It responds with:
      { "content": [{ "type": "text", "text": "..." }] }
    """

    payload = {
        "model":      MODEL,
        "max_tokens": 1024,
        "messages": [
            {"role": "user", "content": user_message}
        ],
    }

    response = requests.post(
        url=f"{BASE_URL}/messages",
        headers=HEADERS,
        json=payload,
    )
    response.raise_for_status()

    data = response.json()
    return data["content"][0]["text"]


# ─────────────────────────────────────────────
# MAIN PROGRAM
# ─────────────────────────────────────────────

def main():
    print_banner()

    try:
        while True:
            user_input = input("  › ").strip()  # › is the input prompt character

            if not user_input:
                continue

            if user_input.lower() in ("quit", "exit", "q"):
                print()
                print("  Goodbye!".center(TERM_WIDTH))
                print()
                break

            print_user(user_input)

            try:
                reply = ask_agent(user_input)
                print_agent(reply)
            except requests.exceptions.ConnectionError:
                print_error("Cannot reach the API. Is the proxy running on localhost:6655?")
            except requests.exceptions.HTTPError as e:
                print_error(f"API returned an error: {e}")

    except KeyboardInterrupt:
        # Ctrl+C exits gracefully instead of showing a traceback
        print()
        print()
        print("  Interrupted. Goodbye!")
        print()


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────

if __name__ == "__main__":
    main()
