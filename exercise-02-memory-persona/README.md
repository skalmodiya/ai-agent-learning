# Exercise 02 — Memory & Persona

## What's New vs Exercise 01

Two additions to the API payload:

**1. System Prompt** — gives the agent a fixed identity sent on every request:
```json
{ "system": "You are Alex, a friendly AI tutor..." }
```

**2. Conversation History** — send ALL past messages so the agent remembers:
```json
"messages": [
  {"role": "user",      "content": "My name is Sam"},
  {"role": "assistant", "content": "Hi Sam!"},
  {"role": "user",      "content": "What's my name?"}
]
```

## Flow

```
System Prompt ──► [ Every single request ]
                         ▲
History grows ───────────┤
each turn           New message
```

## Key Concepts

| Term | Meaning |
|---|---|
| **System prompt** | Hidden instructions defining the agent's role |
| **Conversation history** | Full list of past messages sent every request |
| **Stateful agent** | Agent that remembers context across turns |
| **Context window** | Max tokens the model can see — history has a limit |

## How to Run

```bash
python -m venv venv
venv\Scripts\activate      # Windows
pip install -r requirements.txt
python agent.py
```

## Try It

1. Tell the agent your name
2. Ask something else
3. Ask "What's my name?" — it should remember!

## Next Exercise

**Exercise 03** adds **tool use** — the agent can call functions like a calculator or weather API.
