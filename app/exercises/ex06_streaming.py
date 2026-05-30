"""
Exercise 06 — Streaming
New concept: receive the AI's reply token-by-token as it's generated,
instead of waiting for the full response.
"""

import requests
import time
import json
from . import config

CONCEPT = """
## Exercise 06 — Streaming

### What's new vs Exercise 05
Instead of waiting for the **complete** reply, we receive it **token by token**
as the model generates it — just like ChatGPT's typing effect.

### How streaming works
```
Non-streaming:  ──────────────────────► [full reply arrives at once]
Streaming:      ►"Hello"►" there"►"!"►[done]
```

### API difference
Add `"stream": true` to the payload. The response becomes a
**Server-Sent Events (SSE)** stream instead of a single JSON blob.

Each line looks like:
```
data: {"type": "content_block_delta", "delta": {"text": "Hello"}}
data: {"type": "message_stop"}
```

### Why streaming matters
- **Perceived speed** — users see output immediately
- **Long responses** — no timeout waiting for huge replies
- **Real-time UIs** — enables live typing animations in chat apps

### Key concepts
| Term | Meaning |
|---|---|
| **SSE** | Server-Sent Events — one-way stream of text chunks |
| **Token** | A word fragment — the unit the model generates |
| **Delta** | Each incremental chunk of text |
| **iter_lines()** | Iterates over SSE stream lines one by one |
"""

FLOW_STEPS = [
    ("idle",    "```\nRequest ──► ░░░░░░░░░░ ──► Full reply\n```\n\n_Waiting for input..._"),
    ("send",    "```\n► POST /messages\n  { stream: true }\n```\n\n**Step 1:** Request sent with `stream: true`"),
    ("connect", "```\n  Server opens SSE stream\n► data: {type: message_start}\n```\n\n**Step 2:** Connection established, stream begins"),
    ("tokens",  "```\n► data: {delta: {text: 'Hello'}}\n► data: {delta: {text: ' there'}}\n► data: {delta: {text: '!'}}\n  ...\n```\n\n**Step 3:** Tokens arrive one by one — we print each immediately"),
    ("done",    "```\n  ...\n► data: {type: message_stop}\n  Stream closed\n```\n\n**Done!** `message_stop` event signals the end of the response"),
]


def run_stream(user_message: str, history: list, cfg: dict = None):
    """
    Generator that yields text chunks as they arrive from the stream.
    Usage: for chunk in run_stream(msg, history, cfg): print(chunk, end='')
    """
    cfg     = cfg or {}
    pid     = cfg.get("provider_id", config.DEFAULT_PROVIDER)
    model   = cfg.get("model",       config.get_default_model(pid))
    api_key = cfg.get("api_key",     "")
    headers = config.make_headers(pid, api_key)
    url     = config.get_chat_url(pid, model)

    messages = history + [{"role": "user", "content": user_message}]
    payload  = config.build_payload(pid, model, messages, stream=True)

    with requests.post(url, headers=headers, json=payload, stream=True) as response:
        response.raise_for_status()
        for line in response.iter_lines():
            if not line:
                continue
            line = line.decode("utf-8") if isinstance(line, bytes) else line
            if not line.startswith("data:"):
                continue
            raw = line[len("data:"):].strip()
            if raw == "[DONE]":
                break
            try:
                event = json.loads(raw)
            except json.JSONDecodeError:
                continue

            etype = event.get("type", "")
            if etype == "content_block_delta":
                delta = event.get("delta", {})
                if delta.get("type") == "text_delta":
                    yield delta.get("text", "")
            elif etype == "message_stop":
                break


def run(user_message: str, history: list, cfg: dict = None) -> dict:
    """Non-generator version — collects full streamed reply for app use."""
    cfg    = cfg or {}
    t0     = time.time()
    chunks = []
    for chunk in run_stream(user_message, history, cfg):
        chunks.append(chunk)
    reply   = "".join(chunks)
    elapsed = round(time.time() - t0, 2)

    updated_history = history + [
        {"role": "user",      "content": user_message},
        {"role": "assistant", "content": reply},
    ]
    return {
        "reply":   reply,
        "chunks":  len(chunks),
        "history": updated_history,
        "latency": elapsed,
    }
