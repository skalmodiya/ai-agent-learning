"""
Exercise 06 - Streaming
========================
New concept: receive tokens one by one as the model generates them.
"""

import sys, os, textwrap, json, requests

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

def print_banner():
    b = "─" * TERM_WIDTH
    print(f"\n{b}")
    print("  Exercise 06 — Streaming".center(TERM_WIDTH))
    print("  Tokens appear as they are generated".center(TERM_WIDTH))
    print(b + "\n")

def print_error(msg): print(f"\n  ✖  {msg}\n")

def stream_reply(user_message: str, history: list):
    """Generator: yields text chunks from the SSE stream."""
    messages = history + [{"role": "user", "content": user_message}]
    payload  = {"model": MODEL, "max_tokens": 1024, "stream": True, "messages": messages}

    with requests.post(f"{BASE_URL}/messages", headers=HEADERS, json=payload, stream=True) as r:
        r.raise_for_status()
        for line in r.iter_lines():
            if not line: continue
            line = line.decode("utf-8") if isinstance(line, bytes) else line
            if not line.startswith("data:"): continue
            raw = line[5:].strip()
            if raw == "[DONE]": break
            try:
                event = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if event.get("type") == "content_block_delta":
                delta = event.get("delta", {})
                if delta.get("type") == "text_delta":
                    yield delta.get("text", "")
            elif event.get("type") == "message_stop":
                break

def main():
    print_banner()
    history = []
    try:
        while True:
            user_input = input("  › ").strip()
            if not user_input: continue
            if user_input.lower() in ("quit","exit","q"):
                print(f"\n{'Goodbye!':^{TERM_WIDTH}}\n"); break

            print(f"\n  You\n  {'┄'*(TERM_WIDTH-4)}")
            for l in textwrap.wrap(user_input, TERM_WIDTH-4) or [user_input]: print(f"  {l}")
            print(f"\n{'─'*TERM_WIDTH}\n  Agent (streaming)\n  {'┄'*(TERM_WIDTH-4)}\n  ", end="", flush=True)

            try:
                full_reply = []
                for chunk in stream_reply(user_input, history):
                    print(chunk, end="", flush=True)
                    full_reply.append(chunk)
                reply = "".join(full_reply)
                print(f"\n{'─'*TERM_WIDTH}\n")
                history += [{"role":"user","content":user_input},
                             {"role":"assistant","content":reply}]
            except requests.exceptions.ConnectionError:
                print_error("Cannot reach API.")
            except requests.exceptions.HTTPError as e:
                print_error(f"API error: {e}")
    except KeyboardInterrupt:
        print("\n\n  Interrupted. Goodbye!\n")

if __name__ == "__main__":
    main()
