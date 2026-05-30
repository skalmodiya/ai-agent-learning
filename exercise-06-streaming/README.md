# Exercise 06 — Streaming

## What's New vs Exercise 05

Instead of waiting for the full reply, tokens appear **one by one** as generated:

```
Non-streaming: ─────────────────────► [full reply at once]
Streaming:     ► "Hello" ► " there" ► "!" ► [done]
```

## API Difference

Add `"stream": true` to the payload. The response becomes a Server-Sent Events (SSE) stream:

```
data: {"type": "content_block_delta", "delta": {"text": "Hello"}}
data: {"type": "content_block_delta", "delta": {"text": " there"}}
data: {"type": "message_stop"}
```

## Key Concepts

| Term | Meaning |
|---|---|
| **SSE** | Server-Sent Events — one-way text stream |
| **Token** | A word fragment — the unit models generate |
| **Delta** | Each incremental text chunk |
| **iter_lines()** | Iterates over the SSE stream line by line |

## How to Run

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python agent.py
```

## Next Exercise

**Exercise 07** covers **Structured Output** — force the AI to reply with a specific JSON schema.
