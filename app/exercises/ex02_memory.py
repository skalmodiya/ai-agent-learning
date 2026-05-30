"""
Exercise 02 — Memory & Persona
New concepts: system prompt (persona) + conversation history (memory).
"""

import requests
import time

API_KEY  = "a6eb413e-5c42-4420-87c0-f59b2a4e5a84"
BASE_URL = "http://localhost:6655/anthropic/v1"
MODEL    = "claude-sonnet-4-6"

HEADERS = {
    "x-api-key":         API_KEY,
    "content-type":      "application/json",
    "anthropic-version": "2023-06-01",
}

DEFAULT_PERSONA = (
    "You are Alex, a friendly AI tutor specializing in explaining technology concepts "
    "simply and clearly. You remember everything said in this conversation and build on it."
)

CONCEPT = """
## Exercise 02 — Memory & Persona

### What's new vs Exercise 01
Two new additions to the API payload:

**1. System Prompt (Persona)**
```json
{ "system": "You are Alex, a friendly AI tutor..." }
```
This is a hidden instruction sent before every message. It defines who the agent *is*.

**2. Conversation History (Memory)**
Instead of sending just one message, we send the *entire conversation so far*:
```json
"messages": [
  {"role": "user",      "content": "Hi, my name is Sam"},
  {"role": "assistant", "content": "Hello Sam! How can I help?"},
  {"role": "user",      "content": "What's my name?"}
]
```
The AI sees all previous turns, so it can answer "Your name is Sam."

### Flow
```
System Prompt ──► [ Every request ]
                         ▲
History list grows ──────┤
each turn                │
                    User message
```

### Key concepts
| Term | Meaning |
|---|---|
| **System prompt** | Hidden instructions that define the agent's role/persona |
| **Conversation history** | Full list of past messages sent with every request |
| **Stateful agent** | Agent that remembers context across turns |
| **Context window** | Max tokens the model can "see" — history has a limit |

### Trade-off
More history = better memory, but costs more tokens and eventually hits the context limit.
"""

FLOW_STEPS = [
    ("idle",    "```\nSystem Prompt\n    +\nHistory [ ]\n    +\nNew Message\n```\n\n_Waiting for input..._"),
    ("input",   "```\n► New message received\n```\n\n**Step 1:** User sends a new message"),
    ("history", "```\n  System Prompt\n      +\n► Append to history list\n  [msg1, msg2, ... new]\n```\n\n**Step 2:** New message appended to conversation history list"),
    ("payload", "```\n► Build payload\n  {\n    system: \"...\",\n    messages: [ALL history]\n  }\n```\n\n**Step 3:** Full history + system prompt packed into every request"),
    ("request", "```\n  Payload\n    │\n► POST /messages ──► AI Model\n```\n\n**Step 4:** Full context sent to AI — it sees everything said so far"),
    ("done",    "```\n  AI sees all context\n       │\n► Reply + save to history\n```\n\n**Done!** Reply saved back into history. Next turn will include it."),
]


def run(user_message: str, history: list, system_prompt: str = DEFAULT_PERSONA) -> dict:
    """
    Send a message with full conversation history.
    history: list of {"role": "user"|"assistant", "content": "..."} dicts
    Returns updated history + reply.
    """
    # Append the new user message to history
    new_history = history + [{"role": "user", "content": user_message}]

    payload = {
        "model":      MODEL,
        "max_tokens": 1024,
        "system":     system_prompt,
        "messages":   new_history,
    }

    t0 = time.time()
    response = requests.post(f"{BASE_URL}/messages", headers=HEADERS, json=payload)
    response.raise_for_status()
    elapsed = round(time.time() - t0, 2)

    data = response.json()
    reply = data["content"][0]["text"]

    # Append assistant reply so the next call includes it
    updated_history = new_history + [{"role": "assistant", "content": reply}]

    return {
        "reply":   reply,
        "history": updated_history,
        "latency": elapsed,
        "request": payload,
        "response": data,
    }
