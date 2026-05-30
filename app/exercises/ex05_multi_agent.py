"""
Exercise 05 — Multi-Agent
New concept: two agents with distinct roles collaborating to solve a problem.
Agent A plans/researches, Agent B writes/executes.
"""

import requests
import time
from . import config

CONCEPT = """
## Exercise 05 — Multi-Agent

### What's new vs Exercise 04
Instead of one agent doing everything, we have **two specialised agents**
that pass work to each other.

### The two agents
```
┌─────────────────┐        ┌─────────────────┐
│   PLANNER       │──────► │   WRITER        │
│                 │        │                 │
│ Breaks problem  │        │ Executes the    │
│ into steps,     │        │ plan, writes    │
│ researches,     │        │ the final       │
│ decides approach│        │ output          │
└─────────────────┘        └─────────────────┘
        ▲                          │
        └──────── You ◄────────────┘
```

### Why multiple agents?
- **Specialisation** — each agent has a focused role and system prompt
- **Quality** — a critic/reviewer agent catches errors a solo agent might miss
- **Parallelism** — in real systems, agents can run concurrently
- **Scalability** — complex pipelines chain many agents

### Key concepts
| Term | Meaning |
|---|---|
| **Orchestrator** | The agent (or code) that routes work between agents |
| **Planner agent** | Breaks the task into a structured plan |
| **Executor/Writer agent** | Carries out the plan step by step |
| **Agent handoff** | Passing one agent's output as another's input |
| **Pipeline** | A fixed sequence of agents |
"""

FLOW_STEPS = [
    ("idle",     "```\nUser ──► Planner ──► Writer ──► User\n```\n\n_Waiting for input..._"),
    ("planner",  "```\n► User request ──► PLANNER agent\n  System: \"Break this into steps\"\n```\n\n**Step 1:** Planner receives the task and creates a structured plan"),
    ("plan_out", "```\n  PLANNER returns:\n► \"Step 1: ... Step 2: ... Step 3: ...\"\n```\n\n**Step 2:** Plan captured — this becomes the Writer's input"),
    ("writer",   "```\n  Plan ──► WRITER agent\n► System: \"Execute this plan fully\"\n```\n\n**Step 3:** Writer receives the plan and executes each step"),
    ("done",     "```\n  WRITER produces final output\n► Delivered to user\n```\n\n**Done!** Two specialised agents collaborated to produce a better result"),
]

PLANNER_SYSTEM = (
    "You are a Planner agent. When given a task, you break it into clear, numbered steps. "
    "Be concise. Output ONLY the plan — no execution, no preamble. "
    "Format: Step 1: ... Step 2: ... etc."
)

WRITER_SYSTEM = (
    "You are a Writer/Executor agent. You receive a plan and execute it fully, "
    "producing polished, complete output. Follow each step in order."
)


def _call(system: str, messages: list, cfg: dict) -> dict:
    """Single API call helper."""
    pid     = cfg.get("provider_id", config.DEFAULT_PROVIDER)
    model   = cfg.get("model",       config.get_default_model(pid))
    api_key = cfg.get("api_key",     "")
    headers = config.make_headers(pid, api_key)
    url     = config.get_chat_url(pid, model)
    payload = config.build_payload(pid, model, messages, system=system)
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()
    return {
        "text":    config.parse_reply(pid, data),
        "payload": payload,
        "raw":     data,
    }


def run(user_message: str, cfg: dict = None) -> dict:
    """
    Run the two-agent pipeline:
    1. Planner breaks the task into steps
    2. Writer executes the plan
    """
    cfg = cfg or {}
    t0  = time.time()

    # ── Agent 1: Planner ──
    planner_result = _call(
        system=PLANNER_SYSTEM,
        messages=[{"role": "user", "content": f"Task: {user_message}"}],
        cfg=cfg,
    )
    plan = planner_result["text"]

    # ── Agent 2: Writer ──
    writer_result = _call(
        system=WRITER_SYSTEM,
        messages=[{
            "role":    "user",
            "content": f"Here is your plan to execute:\n\n{plan}\n\nOriginal request: {user_message}",
        }],
        cfg=cfg,
    )

    elapsed = round(time.time() - t0, 2)
    return {
        "plan":           plan,
        "reply":          writer_result["text"],
        "latency":        elapsed,
        "planner_request": planner_result["payload"],
        "writer_request":  writer_result["payload"],
    }
