"""
Exercise 03 - Tool Use
=======================
New concept: the agent can call functions you define.
The agentic loop runs until stop_reason == "end_turn".
"""

import sys, os, textwrap, json, math, requests

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

API_KEY  = "a6eb413e-5c42-4420-87c0-f59b2a4e5a84"
BASE_URL = "http://localhost:6655/anthropic/v1"
MODEL    = "claude-sonnet-4-6"
HEADERS  = {"x-api-key": API_KEY, "content-type": "application/json", "anthropic-version": "2023-06-01"}

try:
    TERM_WIDTH = min(os.get_terminal_size().columns, 80)
except OSError:
    TERM_WIDTH = 80

def print_banner():
    b = "─" * TERM_WIDTH
    print(f"\n{b}")
    print("  Exercise 03 — Tool Use".center(TERM_WIDTH))
    print("  Agent can call: calculator, get_weather".center(TERM_WIDTH))
    print(b + "\n")

def print_user(text):
    print(f"\n  You\n  {'┄'*(TERM_WIDTH-4)}")
    for l in textwrap.wrap(text, TERM_WIDTH-4) or [text]: print(f"  {l}")
    print()

def print_agent(text):
    b = "─" * TERM_WIDTH
    print(b + "\n  Agent\n  " + "┄"*(TERM_WIDTH-4))
    for para in text.strip().split("\n"):
        if not para.strip(): print()
        else:
            for l in textwrap.wrap(para, TERM_WIDTH-4) or [para]: print(f"  {l}")
    print(b + "\n")

def print_tool_call(name, inp, result):
    print(f"  \033[33m⚙  Tool called: {name}({json.dumps(inp)}) → {result}\033[0m")

def print_error(msg): print(f"\n  ✖  {msg}\n")

# ── Tool implementations ──────────────────────
def calculator(expression: str) -> str:
    try:
        result = eval(expression, {"__builtins__": {}, "math": math})
        return str(round(result, 6))
    except Exception as e:
        return f"Error: {e}"

def get_weather(city: str) -> str:
    import hashlib
    seed = int(hashlib.md5(city.lower().encode()).hexdigest(), 16) % 100
    conditions = ["Sunny", "Cloudy", "Rainy", "Partly Cloudy", "Windy"]
    temp_c = 10 + (seed % 25)
    return json.dumps({"city": city, "condition": conditions[seed % 5],
                        "temp_c": temp_c, "temp_f": round(temp_c*9/5+32,1), "note": "(simulated)"})

TOOL_MAP = {"calculator": calculator, "get_weather": get_weather}
TOOL_DEFS = [
    {"name": "calculator", "description": "Evaluate a math expression.",
     "input_schema": {"type": "object", "properties": {"expression": {"type": "string"}}, "required": ["expression"]}},
    {"name": "get_weather", "description": "Get weather for a city (simulated).",
     "input_schema": {"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]}},
]

# ── Agentic loop ──────────────────────────────
def ask_agent(user_message: str, history: list) -> tuple[str, list]:
    """Run the tool-use loop until stop_reason == 'end_turn'."""
    messages = history + [{"role": "user", "content": user_message}]

    while True:
        payload = {"model": MODEL, "max_tokens": 1024, "tools": TOOL_DEFS, "messages": messages}
        response = requests.post(f"{BASE_URL}/messages", headers=HEADERS, json=payload)
        response.raise_for_status()
        data        = response.json()
        stop_reason = data["stop_reason"]
        content     = data["content"]
        messages.append({"role": "assistant", "content": content})

        if stop_reason == "end_turn":
            reply = next((b["text"] for b in content if b.get("type") == "text"), "")
            return reply, messages

        if stop_reason == "tool_use":
            tool_results = []
            for block in content:
                if block.get("type") != "tool_use": continue
                fn     = TOOL_MAP.get(block["name"])
                result = fn(**block["input"]) if fn else "Unknown tool"
                print_tool_call(block["name"], block["input"], result)
                tool_results.append({"type": "tool_result", "tool_use_id": block["id"], "content": result})
            messages.append({"role": "user", "content": tool_results})
        else:
            return f"Unexpected stop: {stop_reason}", messages

def main():
    print_banner()
    history = []
    try:
        while True:
            user_input = input("  › ").strip()
            if not user_input: continue
            if user_input.lower() in ("quit", "exit", "q"):
                print(f"\n{'Goodbye!':^{TERM_WIDTH}}\n"); break
            print_user(user_input)
            try:
                reply, history = ask_agent(user_input, history)
                print_agent(reply)
            except requests.exceptions.ConnectionError:
                print_error("Cannot reach API. Is proxy running on localhost:6655?")
            except requests.exceptions.HTTPError as e:
                print_error(f"API error: {e}")
    except KeyboardInterrupt:
        print("\n\n  Interrupted. Goodbye!\n")

if __name__ == "__main__":
    main()
