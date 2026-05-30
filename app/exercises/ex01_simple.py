"""
Exercise 01 — Simple Agent
Core logic: one message in, one reply out. No history, no persona.
"""

import requests
import time
from . import config

CONCEPT = """
## Exercise 01 — Simple Agent

### What's happening
The most basic AI Agent pattern: **one message in, one reply out**.

```
You ──► [ Build JSON payload ]
             │
             ▼
        [ POST /messages ]
             │
             ▼
        [ Parse response ]
             │
             ▼
        Agent reply ──► You
```

### Key concepts
| Term | Meaning |
|---|---|
| **API** | A URL endpoint you call to use the AI |
| **HTTP POST** | Sending data to a server (like submitting a form) |
| **JSON payload** | The structured data you send: model, max_tokens, messages |
| **Role: user** | Your message |
| **max_tokens** | Hard cap on how long the reply can be |

### What's missing (intentionally)
- No memory — agent forgets each message instantly
- No persona — agent has no role or instructions
- No tools — agent can only talk, not act
"""

FLOW_STEPS = [
    ("idle",     "```\n  You  ──►  Agent\n```\n\n_Waiting for input..._"),
    ("input",    "```\n► You type a message\n  │\n  │\n  Agent\n```\n\n**Step 1:** Capturing your input"),
    ("payload",  "```\n  You typed a message\n  │\n► Build JSON payload\n  │\n  Agent\n```\n\n**Step 2:** Wrapping your text in the API's expected format:\n```json\n{\"model\": \"...\", \"messages\": [{\"role\": \"user\", \"content\": \"...\"}]}\n```"),
    ("request",  "```\n  You typed a message\n  │\n  Build JSON payload\n  │\n► POST /messages  ──►  AI Model\n  │\n  Agent\n```\n\n**Step 3:** Sending HTTP POST to `localhost:6655/anthropic/v1/messages`"),
    ("parse",    "```\n  You typed a message\n  │\n  Build JSON payload\n  │\n  POST /messages  ──►  AI Model\n                           │\n◄──────────────────────────┘\n► Parse response\n```\n\n**Step 4:** Extracting `data[\"content\"][0][\"text\"]` from the JSON response"),
    ("done",     "```\n  You typed a message\n  │\n  Build JSON payload\n  │\n  POST /messages  ──►  AI Model\n                           │\n  Parse response  ◄──────────\n  │\n► Display reply\n```\n\n**Done!** Reply displayed. Agent has no memory of this exchange."),
]


def run(user_message: str, cfg: dict = None) -> dict:
    """Send one message, return reply + metadata."""
    cfg      = cfg or {}
    pid      = cfg.get("provider_id", config.DEFAULT_PROVIDER)
    model    = cfg.get("model",       config.get_default_model(pid))
    api_key  = cfg.get("api_key",     "")
    headers  = config.make_headers(pid, api_key)
    url      = config.get_chat_url(pid, model)
    payload  = config.build_payload(pid, model, [{"role": "user", "content": user_message}])

    t0 = time.time()
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    elapsed = round(time.time() - t0, 2)

    data = response.json()
    return {
        "reply":    config.parse_reply(pid, data),
        "latency":  elapsed,
        "request":  payload,
        "response": data,
    }
