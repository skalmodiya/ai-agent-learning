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

import requests  # Used to make HTTP calls to the AI API
import json      # Used to format data as JSON (the language APIs speak)

# ─────────────────────────────────────────────
# CONFIGURATION
# These are the settings your agent needs to talk to the AI.
# ─────────────────────────────────────────────

API_KEY  = "a6eb413e-5c42-4420-87c0-f59b2a4e5a84"  # Your identity to the API
BASE_URL = "http://localhost:6655/anthropic/v1"     # Where to send requests
MODEL    = "claude-sonnet-4-6"                      # Which AI model to use

# HTTP headers tell the server who you are and what format you're sending.
HEADERS = {
    "x-api-key":    API_KEY,         # Authentication
    "content-type": "application/json",  # We're sending JSON data
    "anthropic-version": "2023-06-01",   # Required by Anthropic API
}


# ─────────────────────────────────────────────
# THE CORE FUNCTION
# This is the heart of every AI Agent: ask → answer
# ─────────────────────────────────────────────

def ask_agent(user_message: str) -> str:
    """
    Send a message to the AI and return its reply.

    Parameters:
        user_message: The text the user wants to send to the AI.

    Returns:
        The AI's response as a plain string.
    """

    # ── Step 1: Build the request payload ──
    # The Anthropic API expects a specific JSON structure.
    # "messages" is a list — each item has a "role" and "content".
    # Roles:
    #   "user"      → the human speaking
    #   "assistant" → the AI speaking (used when building conversation history)
    payload = {
        "model":      MODEL,
        "max_tokens": 1024,  # Maximum words the AI can reply with
        "messages": [
            {
                "role":    "user",
                "content": user_message,
            }
        ],
    }

    # ── Step 2: Send the request to the API ──
    # We use HTTP POST because we're sending data (our message) to the server.
    # Think of it like submitting a form on a website.
    response = requests.post(
        url=f"{BASE_URL}/messages",  # The endpoint that handles chat
        headers=HEADERS,
        json=payload,                # requests will serialize this to JSON
    )

    # ── Step 3: Handle errors ──
    # If the server returns an error (4xx/5xx status), raise an exception
    # so we don't silently swallow failures.
    response.raise_for_status()

    # ── Step 4: Extract the AI's reply ──
    # The response is JSON. Parse it and dig out the text content.
    # Response structure:
    #   {
    #     "content": [
    #       { "type": "text", "text": "Hello! ..." }
    #     ],
    #     ...
    #   }
    data = response.json()
    return data["content"][0]["text"]


# ─────────────────────────────────────────────
# MAIN PROGRAM
# This is what runs when you execute: python agent.py
# ─────────────────────────────────────────────

def main():
    print("=" * 50)
    print("  Exercise 01 — Simple AI Agent")
    print("  Type 'quit' to exit")
    print("=" * 50)
    print()

    # A simple loop: keep asking questions until the user types 'quit'
    while True:
        user_input = input("You: ").strip()

        # Guard against empty input
        if not user_input:
            continue

        # Exit condition
        if user_input.lower() == "quit":
            print("Goodbye!")
            break

        # Call the agent and print its reply
        print("Agent: ", end="", flush=True)  # Print on same line, no newline yet
        reply = ask_agent(user_input)
        print(reply)
        print()  # Blank line for readability


# ─────────────────────────────────────────────
# ENTRY POINT
# Python convention: only run main() when this file is executed directly,
# not when it's imported as a module by another file.
# ─────────────────────────────────────────────

if __name__ == "__main__":
    main()
