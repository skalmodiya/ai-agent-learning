# Exercise 01 — Simple AI Agent

## What You'll Learn

The **absolute basics** of an AI Agent:

```
User types a message
       ↓
Agent sends it to the AI API (HTTP POST)
       ↓
AI model processes it and responds
       ↓
Agent displays the response
```

---

## Key Concepts

| Concept | What it means |
|---|---|
| **API** | A URL you call to use a service (like the AI brain) |
| **HTTP POST** | Sending data to a server, like submitting a form |
| **JSON** | The data format APIs use to talk to each other |
| **Model** | The specific AI version handling your request |
| **Message role** | `user` = you, `assistant` = AI — used to build conversations |
| **max_tokens** | Limits how long the AI's reply can be |

---

## Project Structure

```
exercise-01-simple-agent/
├── agent.py        ← The agent code (start here)
├── README.md       ← This file
└── requirements.txt
```

---

## How to Run

Always use a virtual environment — this keeps dependencies isolated per exercise
and prevents conflicts with your global Python installation.

```bash
# 1. Create a virtual environment (only needed once)
python -m venv venv

# 2. Activate it
#    Windows:
venv\Scripts\activate
#    Mac / Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the agent
python agent.py
```

The agent will refuse to start if no virtual environment is active —
this is intentional so you never accidentally run it in the wrong environment.

Type any message and press Enter. Type `quit` or press `Ctrl+C` to exit.

---

## What the Request Looks Like (Under the Hood)

When you type a message, the agent sends this JSON to the API:

```json
{
  "model": "claude-sonnet-4-6",
  "max_tokens": 1024,
  "messages": [
    { "role": "user", "content": "Your message here" }
  ]
}
```

And the API responds with:

```json
{
  "content": [
    { "type": "text", "text": "The AI's reply..." }
  ]
}
```

---

## What's Missing (Intentionally)

This exercise is kept minimal on purpose. You will add these in later exercises:

- **Memory** — the agent forgets each message (no conversation history yet)
- **System prompt** — no personality or instructions given to the AI yet
- **Tools** — the agent can't take actions yet (search, calculate, etc.)
- **Error handling** — only basic error handling for now

---

## Next Exercise

**Exercise 02** will add a **system prompt** (give the agent a personality and role)
and **conversation memory** (so it remembers what you said earlier in the chat).
