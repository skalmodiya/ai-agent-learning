"""
Exercise 04 - ReAct Loop
=========================
New concept: agent narrates Thought → Action → Observation steps explicitly.
"""

import sys, os, textwrap, requests

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def _check_venv():
    inside = (hasattr(sys, "real_prefix") or
              (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix))
    if not inside:
        print("\n  ERROR: No virtual environment detected.")
        print("  python -m venv venv && venv\\Scripts\\activate\n")
        sys.exit(1)
_check_venv()

import math, json
API_KEY  = "a6eb413e-5c42-4420-87c0-f59b2a4e5a84"
BASE_URL = "http://localhost:6655/anthropic/v1"
MODEL    = "claude-sonnet-4-6"
HEADERS  = {"x-api-key": API_KEY, "content-type": "application/json", "anthropic-version": "2023-06-01"}

try:
    TERM_WIDTH = min(os.get_terminal_size().columns, 80)
except OSError:
    TERM_WIDTH = 80

SYSTEM_PROMPT = """You are a ReAct agent. For every request follow this EXACT format:

Thought: [your reasoning]
Action: tool_name({"key": "value"}) OR Action: None
Observation: [I will fill this in after you act]
... repeat as needed ...
Final Answer: [your complete answer]

Available tools: calculator(expression), lookup_fact(query)
Always show your thinking. Never skip to Final Answer without reasoning."""

def print_banner():
    b = "─" * TERM_WIDTH
    print(f"\n{b}")
    print("  Exercise 04 — ReAct Loop".center(TERM_WIDTH))
    print("  Thought → Action → Observation".center(TERM_WIDTH))
    print(b + "\n")

def print_user(text):
    print(f"\n  You\n  {'┄'*(TERM_WIDTH-4)}")
    for l in textwrap.wrap(text, TERM_WIDTH-4) or [text]: print(f"  {l}")
    print()

def print_trace(text):
    b = "─" * TERM_WIDTH
    print(b + "\n  ReAct Trace\n  " + "┄"*(TERM_WIDTH-4))
    for line in text.strip().split("\n"):
        colour = ""
        if line.startswith("Thought:"): colour = "\033[36m"    # cyan
        elif line.startswith("Action:"): colour = "\033[33m"   # yellow
        elif line.startswith("Observation:"): colour = "\033[32m"  # green
        elif line.startswith("Final Answer:"): colour = "\033[1m"  # bold
        reset = "\033[0m" if colour else ""
        for l in textwrap.wrap(line, TERM_WIDTH-4) or [line]:
            print(f"  {colour}{l}{reset}")
    print(b + "\n")

def print_error(msg): print(f"\n  ✖  {msg}\n")

def calculator(expression):
    try: return str(round(eval(expression, {"__builtins__": {}, "math": math}), 6))
    except Exception as e: return f"Error: {e}"

def lookup_fact(query):
    facts = {"tokyo population": "~13.96M city / 37.4M metro",
             "speed of light": "299,792,458 m/s", "pi": "3.14159265358979",
             "earth radius": "6,371 km", "python release year": "1991"}
    for k,v in facts.items():
        if k in query.lower(): return v
    return f"No specific fact for '{query}'"

TOOL_MAP = {"calculator": calculator, "lookup_fact": lookup_fact}
TOOL_DEFS = [
    {"name": "calculator", "description": "Evaluate math.",
     "input_schema": {"type":"object","properties":{"expression":{"type":"string"}},"required":["expression"]}},
    {"name": "lookup_fact", "description": "Look up a fact.",
     "input_schema": {"type":"object","properties":{"query":{"type":"string"}},"required":["query"]}},
]

def ask_agent(user_message: str) -> str:
    messages = [{"role": "user", "content": user_message}]
    while True:
        payload = {"model": MODEL, "max_tokens": 2048, "system": SYSTEM_PROMPT,
                   "tools": TOOL_DEFS, "messages": messages}
        r = requests.post(f"{BASE_URL}/messages", headers=HEADERS, json=payload)
        r.raise_for_status()
        data = r.json()
        content = data["content"]
        messages.append({"role": "assistant", "content": content})
        if data["stop_reason"] == "end_turn":
            return next((b["text"] for b in content if b.get("type")=="text"), "")
        if data["stop_reason"] == "tool_use":
            results = []
            for block in content:
                if block.get("type") != "tool_use": continue
                fn = TOOL_MAP.get(block["name"])
                result = fn(**block["input"]) if fn else "Unknown tool"
                results.append({"type":"tool_result","tool_use_id":block["id"],"content":result})
            messages.append({"role": "user", "content": results})

def main():
    print_banner()
    try:
        while True:
            user_input = input("  › ").strip()
            if not user_input: continue
            if user_input.lower() in ("quit","exit","q"):
                print(f"\n{'Goodbye!':^{TERM_WIDTH}}\n"); break
            print_user(user_input)
            try:
                reply = ask_agent(user_input)
                print_trace(reply)
            except requests.exceptions.ConnectionError:
                print_error("Cannot reach API.")
            except requests.exceptions.HTTPError as e:
                print_error(f"API error: {e}")
    except KeyboardInterrupt:
        print("\n\n  Interrupted. Goodbye!\n")

if __name__ == "__main__":
    main()
