# AI Agent Learning Journey

A hands-on, progressive series of exercises for learning AI Agents from scratch —
from a single API call all the way to complex multi-agent systems.

Each exercise builds on the previous one, adding exactly one new concept at a time.

---

## Learning Path

| # | Exercise | Topic | Key Concept |
|---|---|---|---|
| 01 | [Simple Agent](./exercise-01-simple-agent/) | Your first API call | HTTP POST → AI response |
| 02 | Memory & Persona _(coming soon)_ | System prompt + chat history | Stateful conversation |
| 03 | Tools _(coming soon)_ | Give the agent abilities | Function/tool calling |
| 04 | ReAct Loop _(coming soon)_ | Think → Act → Observe | The agent loop pattern |
| 05 | Multi-Agent _(coming soon)_ | Agents talking to agents | Orchestration |

---

## Prerequisites

- Python 3.9+
- `pip` package manager
- Access to the AI API (configured per exercise)

---

## How to Use This Repo

Each exercise is self-contained. The standard setup for every exercise is:

```bash
# 1. Go into the exercise folder
cd exercise-01-simple-agent

# 2. Create a virtual environment (keeps dependencies isolated)
python -m venv venv

# 3. Activate it
#    Windows:
venv\Scripts\activate
#    Mac / Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the agent
python agent.py
```

> Every agent enforces the virtual environment — it will print a clear error
> and exit if you try to run it without one activated.

Read the `README.md` inside each exercise folder first — it explains the concept
before you look at the code.

---

## Project Structure

```
AIAgent/
├── README.md                        ← You are here
├── .gitignore
└── exercise-01-simple-agent/
    ├── agent.py                     ← Agent code (heavily commented)
    ├── README.md                    ← Concept explanation + how to run
    ├── requirements.txt             ← Dependencies
    └── venv/                        ← Created locally, not committed
```

---

## Philosophy

> One concept per exercise. No magic. Every line explained.

The goal is not just to make things work, but to understand *why* they work
so you can build your own agents from scratch.
