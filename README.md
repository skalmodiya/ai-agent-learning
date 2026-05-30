# AI Agent Learning Journey

A hands-on, progressive series for learning AI Agents from scratch —
from a single API call all the way to RAG and multi-agent systems.

Each exercise teaches **one concept only**, with every line commented.
Run them from the terminal, or use the **Gradio UI app** to explore all 8 at once.

---

## Quick Start — UI App (Recommended)

```bash
cd app
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux
pip install -r requirements.txt
python app.py
```

Open **http://localhost:7860** — click any exercise tab and start learning.

---

## Learning Path

| # | Exercise | New Concept | Key Idea |
|---|---|---|---|
| [01](./exercise-01-simple-agent/) | Simple Agent | HTTP POST to AI API | One message in, one reply out |
| [02](./exercise-02-memory-persona/) | Memory & Persona | System prompt + history | Agent remembers context |
| [03](./exercise-03-tool-use/) | Tool Use | Function calling | Agent invokes code you write |
| [04](./exercise-04-react-loop/) | ReAct Loop | Thought → Action → Observe | Transparent reasoning chain |
| [05](./exercise-05-multi-agent/) | Multi-Agent | Agent pipeline | Planner + Writer collaborate |
| [06](./exercise-06-streaming/) | Streaming | Server-Sent Events | Tokens arrive in real time |
| [07](./exercise-07-structured-output/) | Structured Output | JSON schema forcing | Machine-readable responses |
| [08](./exercise-08-rag/) | RAG | Retrieval-Augmented Generation | Answer from your own documents |

---

## Project Structure

```
AIAgent/
├── README.md
├── .gitignore
│
├── app/                              ← Gradio UI — explore all 8 exercises here
│   ├── app.py                        ← Launch: python app.py → localhost:7860
│   ├── requirements.txt              ← gradio, requests
│   ├── README.md
│   └── exercises/                    ← Importable logic modules (no venv guard)
│       ├── ex01_simple.py
│       ├── ex02_memory.py
│       ├── ex03_tools.py
│       ├── ex04_react.py
│       ├── ex05_multi_agent.py
│       ├── ex06_streaming.py
│       ├── ex07_structured.py
│       └── ex08_rag.py
│
├── exercise-01-simple-agent/         ← Terminal version of each exercise
├── exercise-02-memory-persona/       ← Each has: agent.py, README.md,
├── exercise-03-tool-use/             ←           requirements.txt
├── exercise-04-react-loop/
├── exercise-05-multi-agent/
├── exercise-06-streaming/
├── exercise-07-structured-output/
└── exercise-08-rag/
```

---

## Running Individual Exercises (Terminal)

Every exercise folder is self-contained:

```bash
cd exercise-02-memory-persona

python -m venv venv
venv\Scripts\activate       # Windows
pip install -r requirements.txt
python agent.py
```

The agent will refuse to start if no virtual environment is active.

---

## Prerequisites

- Python 3.9+
- Access to the AI API on `localhost:6655` (Anthropic proxy)

---

## Philosophy

> One concept per exercise. No magic. Every line explained.

The goal is to understand *why* agents work, not just copy-paste code.
