# AI Agent Learning Platform

A hands-on, progressive series for learning AI Agents from scratch —
from a single API call all the way to RAG and multi-agent systems.

All 8 exercises are available in a **single Gradio UI app** with live chat, animated step-by-step flow diagrams, and raw API request/response inspection. No switching terminals — just click a tab and learn.

---

## What You'll Build

| # | Exercise | New Concept | What It Does |
|---|---|---|---|
| 01 | Simple Agent | HTTP POST | One message in → one reply out |
| 02 | Memory & Persona | System prompt + history | Agent remembers context across turns |
| 03 | Tool Use | Function calling | Agent calls your Python functions |
| 04 | ReAct Loop | Thought → Action → Observe | Transparent multi-step reasoning |
| 05 | Multi-Agent | Agent pipeline | Planner + Writer agents collaborate |
| 06 | Streaming | Server-Sent Events | Tokens arrive word-by-word in real time |
| 07 | Structured Output | JSON schema forcing | Machine-readable responses every time |
| 08 | RAG | Retrieval-Augmented Generation | AI answers from your own documents |

---

## Prerequisites

- **Python 3.9+**
- **An AI API key** — works with:
  - Anthropic (Claude)
  - OpenAI (GPT-4o, etc.)
  - Google Gemini
  - Any LiteLLM-compatible proxy
- **A running proxy on `localhost:6655`** that forwards to your chosen provider  
  *(e.g. [LiteLLM proxy](https://docs.litellm.ai/docs/proxy/quick_start), or a corporate AI gateway)*

> **Note:** If your API endpoint is different, edit `app/exercises/config.py` and update the `base_url` values for each provider.

---

## Quick Start — Gradio UI App

```bash
# 1. Clone the repo
git clone https://github.com/skalmodiya/ai-agent-learning.git
cd ai-agent-learning

# 2. Create and activate a virtual environment
cd app
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch the app
python app.py
```

Open **http://localhost:7860** in your browser.

### First-time setup in the UI

1. Enter your **API key** in the `🔑 Key` field in the top bar  
   *(it is saved automatically — you won't need to enter it again after the first time)*
2. The **Provider** dropdown unlocks automatically — select your provider (Anthropic, OpenAI, Gemini, or LiteLLM)
3. Select your preferred **Model** from the dropdown
4. Click any exercise tab and start chatting

---

## UI Layout

Each tab has three panels side by side:

```
┌─────────────────┬────────────────────────┬─────────────────────┐
│  📖 Learn       │  ▶ Try It Live         │  🔄 How It Works    │
│                 │                        │                     │
│  Concept        │  Chat input + response │  Animated flow      │
│  explanation,   │  Raw JSON viewer       │  diagram — steps    │
│  key terms,     │  Latency timer         │  highlight as the   │
│  what's new     │                        │  agent runs         │
└─────────────────┴────────────────────────┴─────────────────────┘
```

- **📖 Learn** — explains the concept introduced in this exercise and what's new vs the previous one
- **▶ Try It Live** — a live chat interface; send a message and the agent responds in real time
- **🔄 How It Works** — animated step-by-step flow showing exactly what happens inside the agent as it processes your message

---

## Suggested Learning Order

Work through the tabs **left to right** — each exercise adds exactly one new concept on top of the previous:

```
01 Simple  →  02 Memory  →  03 Tools  →  04 ReAct
                                              ↓
08 RAG     ←  07 Structured  ←  06 Streaming  ←  05 Multi-Agent
```

**Tip:** In each tab, send a message and watch the "How It Works" panel animate through the steps. Once it completes, the `🔍 Raw JSON` section shows you the exact API request and response — great for understanding the wire format.

---

## Running Individual Exercises in the Terminal

Each exercise also has a standalone terminal version in its own folder:

```bash
cd exercise-03-tool-use

python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

pip install -r requirements.txt
python agent.py
```

The standalone agents refuse to start unless a virtual environment is active (intentional — keeps dependencies isolated).

---

## Project Structure

```
ai-agent-learning/
│
├── README.md                         ← You are here
├── .gitignore
│
├── app/                              ← Gradio UI app
│   ├── app.py                        ← Main entry point → python app.py
│   ├── requirements.txt              ← gradio==6.15.2, requests
│   ├── settings.db                   ← Auto-created; stores your API key locally
│   └── exercises/                    ← Shared logic modules
│       ├── config.py                 ← Provider/model/URL config (edit base_url here)
│       ├── ex01_simple.py
│       ├── ex02_memory.py
│       ├── ex03_tools.py
│       ├── ex04_react.py
│       ├── ex05_multi_agent.py
│       ├── ex06_streaming.py
│       ├── ex07_structured.py
│       └── ex08_rag.py
│
├── exercise-01-simple-agent/         ← Standalone terminal version
├── exercise-02-memory-persona/       │  Each folder contains:
├── exercise-03-tool-use/             │    agent.py          ← run this
├── exercise-04-react-loop/           │    requirements.txt
├── exercise-05-multi-agent/          │    README.md
├── exercise-06-streaming/            │
├── exercise-07-structured-output/    │
└── exercise-08-rag/                  ┘
```

---

## Changing the API Endpoint

By default all requests go through a local proxy at `localhost:6655`. To point directly at a provider or use a different gateway, edit `app/exercises/config.py`:

```python
PROVIDERS = {
    "anthropic": {
        "base_url": "http://localhost:6655/anthropic/v1",  # ← change this
        ...
    },
    "openai": {
        "base_url": "http://localhost:6655/openai/v1",     # ← and this
        ...
    },
    ...
}
```

For direct Anthropic access use `https://api.anthropic.com/v1`.  
For direct OpenAI access use `https://api.openai.com/v1`.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: gradio` | Make sure you activated the venv and ran `pip install -r requirements.txt` |
| Port 7860 already in use | Kill the old process: `powershell Get-NetTCPConnection -LocalPort 7860 \| Stop-Process` |
| API key not saved after refresh | The key is stored in `app/settings.db` — check the file exists and is not read-only |
| Connection refused / no response | Check your proxy is running on port 6655; verify the API key is correct |
| Provider/Model dropdowns greyed out | Enter a valid API key first — the dropdowns unlock automatically |
| Wrong Python version (Gradio errors) | Use `venv\Scripts\python.exe app.py` explicitly, not the system `python` |

---

## Tech Stack

- **Python 3.9+**
- **Gradio 6.15.2** — UI framework
- **requests** — HTTP calls to AI APIs
- **SQLite** — stores API key locally (never leaves your machine)
- **Anthropic / OpenAI / Gemini APIs** — via a local proxy

---

## Philosophy

> One concept per exercise. No magic. Every line explained.

The goal is to understand *why* agents work, not just copy-paste code.
Each exercise is a minimal, working example — nothing more.
