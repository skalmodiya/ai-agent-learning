# Exercise 05 — Multi-Agent

## What's New vs Exercise 04

Instead of one agent doing everything, two **specialised agents** collaborate:

```
┌──────────────┐        ┌──────────────┐
│   PLANNER    │──────► │   WRITER     │
│              │        │              │
│ Breaks task  │        │ Executes the │
│ into steps   │        │ plan fully   │
└──────────────┘        └──────────────┘
       ▲                       │
       └────── You ◄───────────┘
```

## Key Concepts

| Term | Meaning |
|---|---|
| **Orchestrator** | Code that routes work between agents |
| **Planner agent** | Breaks task into a numbered plan |
| **Writer agent** | Executes each step of the plan |
| **Agent handoff** | One agent's output becomes another's input |
| **Pipeline** | Fixed sequence of agent calls |

## How to Run

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python agent.py
```

## Try It

- "Write a 3-paragraph blog post about AI Agents"
- "Create a weekly study plan for learning Python in 30 days"
- "Explain quantum computing to a 10-year-old"

## Next Exercise

**Exercise 06** covers **Streaming** — tokens appear as the model generates them.
