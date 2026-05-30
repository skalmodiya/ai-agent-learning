"""
Exercise 04 — ReAct Loop
New concept: Reasoning + Acting in explicit Thought/Action/Observation steps.
The agent narrates its own thinking before acting.
"""

import requests
import time
import json
import math

API_KEY  = "a6eb413e-5c42-4420-87c0-f59b2a4e5a84"
BASE_URL = "http://localhost:6655/anthropic/v1"
MODEL    = "claude-sonnet-4-6"

HEADERS = {
    "x-api-key":         API_KEY,
    "content-type":      "application/json",
    "anthropic-version": "2023-06-01",
}

CONCEPT = """
## Exercise 04 — ReAct Loop

### What's new vs Exercise 03
In Exercise 03 the agent used tools silently. In ReAct, the agent **narrates its reasoning**
at every step using a structured Thought → Action → Observation pattern.

### The ReAct pattern
```
Thought:     "I need to find the population of Tokyo"
Action:      lookup_fact(query="Tokyo population")
Observation: "Tokyo population: ~14 million"
Thought:     "Now I can answer"
Answer:      "Tokyo has approximately 14 million people."
```

### Why this matters
- Makes agent reasoning **transparent and debuggable**
- The agent can **self-correct** based on observations
- Foundation of most real-world agent frameworks (LangChain, AutoGPT, etc.)

### How we implement it
We give the agent a system prompt instructing it to think step-by-step,
and we capture each Thought/Action/Observation cycle.

### Key concepts
| Term | Meaning |
|---|---|
| **Thought** | The agent's internal reasoning (visible to us) |
| **Action** | A tool call with structured input |
| **Observation** | The result returned from the tool |
| **ReAct** | Reasoning + Acting — coined by Google Research (2022) |
"""

FLOW_STEPS = [
    ("idle",        "```\nThought ──► Action ──► Observation\n    ▲                        │\n    └────────────────────────┘\n```\n\n_Waiting for input..._"),
    ("thought1",    "```\n► Thought: \"What do I need to do?\"\n```\n\n**Step 1 — Think:** Agent reasons about what's needed before acting"),
    ("action",      "```\n  Thought: \"I need to call a tool\"\n► Action: tool_name({...})\n```\n\n**Step 2 — Act:** Agent picks a tool and calls it with structured arguments"),
    ("observation", "```\n  Action executed locally\n► Observation: \"Result: ...\"\n```\n\n**Step 3 — Observe:** Tool result fed back to agent as an observation"),
    ("thought2",    "```\n► Thought: \"Based on the result...\"\n  (loop back if more steps needed)\n```\n\n**Step 4 — Think again:** Agent reasons about the observation, may act again"),
    ("done",        "```\n  Thought: \"I have enough info\"\n► Final Answer given\n```\n\n**Done!** Agent delivers answer after completing its reasoning chain"),
]

SYSTEM_PROMPT = """You are a ReAct agent. For every request, you MUST follow this pattern:

Thought: [your reasoning about what to do next]
Action: [tool name and input if needed, or "None" if no tool needed]
Observation: [result of the action — I will fill this in]
... (repeat Thought/Action/Observation as needed)
Final Answer: [your complete answer to the user]

Available tools:
- calculator(expression: str) → evaluates math
- lookup_fact(query: str) → looks up a fact (simulated)

Always show your thinking. Never skip steps."""


def calculator(expression: str) -> str:
    try:
        allowed = set("0123456789+-*/()., eE%")
        if not all(c in allowed for c in expression.replace(" ", "")):
            return "Error: only basic math allowed"
        result = eval(expression, {"__builtins__": {}, "math": math})
        return str(round(result, 6))
    except Exception as e:
        return f"Error: {e}"


def lookup_fact(query: str) -> str:
    """Simulated fact lookup."""
    facts = {
        "tokyo population":       "Tokyo population: approximately 13.96 million (city), 37.4 million (metro area)",
        "speed of light":         "Speed of light: 299,792,458 metres per second",
        "python release year":    "Python was first released in 1991 by Guido van Rossum",
        "earth radius":           "Earth's mean radius: 6,371 km",
        "pi":                     "Pi (π) ≈ 3.14159265358979",
    }
    q = query.lower()
    for key, val in facts.items():
        if key in q:
            return val
    return f"No specific fact found for '{query}'. Use general knowledge."


TOOL_DEFINITIONS = [
    {
        "name": "calculator",
        "description": "Evaluate a math expression.",
        "input_schema": {
            "type": "object",
            "properties": {"expression": {"type": "string"}},
            "required": ["expression"],
        },
    },
    {
        "name": "lookup_fact",
        "description": "Look up a factual piece of information.",
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
    },
]

TOOL_MAP = {"calculator": calculator, "lookup_fact": lookup_fact}


def run(user_message: str) -> dict:
    """Run a ReAct loop and return the full reasoning trace + final answer."""
    messages = [{"role": "user", "content": user_message}]
    trace    = []
    t0       = time.time()

    while True:
        payload = {
            "model":      MODEL,
            "max_tokens": 2048,
            "system":     SYSTEM_PROMPT,
            "tools":      TOOL_DEFINITIONS,
            "messages":   messages,
        }

        response = requests.post(f"{BASE_URL}/messages", headers=HEADERS, json=payload)
        response.raise_for_status()
        data        = response.json()
        stop_reason = data.get("stop_reason")
        content     = data.get("content", [])

        messages.append({"role": "assistant", "content": content})

        # Collect text blocks (Thought / Final Answer)
        for block in content:
            if block.get("type") == "text":
                trace.append({"type": "thought", "text": block["text"]})

        if stop_reason == "end_turn":
            reply = next((b["text"] for b in content if b.get("type") == "text"), "")
            break

        if stop_reason == "tool_use":
            tool_results = []
            for block in content:
                if block.get("type") != "tool_use":
                    continue
                fn     = TOOL_MAP.get(block["name"])
                result = fn(**block["input"]) if fn else "Unknown tool"
                trace.append({
                    "type":   "action",
                    "tool":   block["name"],
                    "input":  block["input"],
                    "result": result,
                })
                tool_results.append({
                    "type":        "tool_result",
                    "tool_use_id": block["id"],
                    "content":     result,
                })
            messages.append({"role": "user", "content": tool_results})
        else:
            reply = f"Unexpected stop: {stop_reason}"
            break

    elapsed = round(time.time() - t0, 2)
    return {
        "reply":   reply,
        "trace":   trace,
        "latency": elapsed,
        "request": payload,
        "response": data,
    }
