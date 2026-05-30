"""
Exercise 03 — Tool Use
New concept: giving the agent callable tools (functions it can invoke).
The agent decides when to call a tool; we execute it and feed the result back.
"""

import requests
import time
import json
import math
from . import config

CONCEPT = """
## Exercise 03 — Tool Use

### What's new vs Exercise 02
The agent can now **call functions** you define. This is also called "function calling".

### How it works (3-step dance)
```
1. You ──► Agent: "What is 144 * 7?"
2. Agent ──► You: "Please call calculator({expression: '144*7'})"
3. You execute it ──► Agent: "Result is 1008"
4. Agent ──► You: "144 × 7 = 1008"
```

### Tool definition (sent to API)
```json
{
  "name": "calculator",
  "description": "Evaluate a math expression",
  "input_schema": {
    "type": "object",
    "properties": {
      "expression": {"type": "string"}
    },
    "required": ["expression"]
  }
}
```

### Key concepts
| Term | Meaning |
|---|---|
| **Tool definition** | JSON schema describing a function the agent can call |
| **tool_use block** | Agent's response when it wants to call a tool |
| **tool_result** | Your response after executing the tool |
| **Agentic loop** | Keep calling API until `stop_reason == "end_turn"` |

### Available tools in this exercise
- **calculator** — evaluate math expressions
- **get_weather** — simulated weather for any city
"""

FLOW_STEPS = [
    ("idle",        "```\nUser ──► Agent\n         │\n      [Tools available]\n```\n\n_Waiting for input..._"),
    ("send",        "```\n► Send message + tool definitions\n  to AI model\n```\n\n**Step 1:** Message sent along with the list of available tools"),
    ("check",       "```\n  AI decides:\n► Use a tool?  or  Answer directly?\n```\n\n**Step 2:** AI examines the request and decides if a tool is needed"),
    ("tool_call",   "```\n  AI says:\n► \"Call calculator({expr: '144*7'})\"\n  stop_reason = 'tool_use'\n```\n\n**Step 3:** AI returns a `tool_use` block instead of a text answer"),
    ("execute",     "```\n► We execute the tool locally\n  calculator('144*7') → 1008\n```\n\n**Step 4:** *We* run the function and get the result (AI can't run code itself)"),
    ("feed_back",   "```\n► Send tool result back to AI\n  {role: 'user', type: 'tool_result', content: '1008'}\n```\n\n**Step 5:** Result fed back so AI can incorporate it into its answer"),
    ("done",        "```\n  AI now knows the result\n► Generates final answer\n  stop_reason = 'end_turn'\n```\n\n**Done!** AI synthesizes the tool result into a natural language answer"),
]

# ── Tool implementations (run locally, not by the AI) ──

def calculator(expression: str) -> str:
    """Safely evaluate a math expression."""
    try:
        allowed = set("0123456789+-*/()., eE%")
        if not all(c in allowed for c in expression.replace(" ", "")):
            return "Error: only basic math expressions allowed"
        result = eval(expression, {"__builtins__": {}, "math": math})
        return str(round(result, 6))
    except Exception as e:
        return f"Error: {e}"


def get_weather(city: str) -> str:
    """Simulated weather — returns fake but plausible data."""
    import hashlib
    seed = int(hashlib.md5(city.lower().encode()).hexdigest(), 16) % 100
    conditions = ["Sunny", "Cloudy", "Rainy", "Partly Cloudy", "Windy"]
    condition = conditions[seed % len(conditions)]
    temp_c = 10 + (seed % 25)
    return json.dumps({
        "city": city,
        "condition": condition,
        "temperature_c": temp_c,
        "temperature_f": round(temp_c * 9/5 + 32, 1),
        "humidity_pct": 40 + (seed % 50),
        "note": "(simulated data)",
    })


TOOL_DEFINITIONS = [
    {
        "name": "calculator",
        "description": "Evaluate a mathematical expression and return the numeric result.",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "A math expression like '144 * 7' or '(100 / 4) + 50'",
                }
            },
            "required": ["expression"],
        },
    },
    {
        "name": "get_weather",
        "description": "Get current weather for a city (simulated).",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "City name, e.g. 'London' or 'Tokyo'",
                }
            },
            "required": ["city"],
        },
    },
]

TOOL_MAP = {"calculator": calculator, "get_weather": get_weather}


def run(user_message: str, history: list, cfg: dict = None) -> dict:
    """
    Agentic loop: keep calling the API until stop_reason == 'end_turn'.
    Handles tool_use responses by executing the tool locally.
    """
    cfg      = cfg or {}
    pid      = cfg.get("provider_id", config.DEFAULT_PROVIDER)
    model    = cfg.get("model",       config.get_default_model(pid))
    api_key  = cfg.get("api_key",     "")
    headers  = config.make_headers(pid, api_key)
    url      = config.get_chat_url(pid, model)

    messages       = history + [{"role": "user", "content": user_message}]
    tool_calls_log = []
    all_requests   = []
    t0             = time.time()

    while True:
        payload = config.build_payload(pid, model, messages, tools=TOOL_DEFINITIONS)
        all_requests.append(payload)

        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        stop_reason = data.get("stop_reason")
        content     = data.get("content", [])

        # Add assistant message to history
        messages.append({"role": "assistant", "content": content})

        if stop_reason == "end_turn":
            # Extract final text reply
            reply = next((b["text"] for b in content if b.get("type") == "text"), "")
            break

        if stop_reason == "tool_use":
            # Execute each requested tool and build tool_result message
            tool_results = []
            for block in content:
                if block.get("type") != "tool_use":
                    continue
                tool_name  = block["name"]
                tool_input = block["input"]
                tool_id    = block["id"]

                fn     = TOOL_MAP.get(tool_name)
                result = fn(**tool_input) if fn else f"Unknown tool: {tool_name}"

                tool_calls_log.append({
                    "tool": tool_name, "input": tool_input, "result": result
                })
                tool_results.append({
                    "type":        "tool_result",
                    "tool_use_id": tool_id,
                    "content":     result,
                })

            messages.append({"role": "user", "content": tool_results})
        else:
            # Unexpected stop reason — bail out
            reply = f"Unexpected stop_reason: {stop_reason}"
            break

    elapsed = round(time.time() - t0, 2)
    updated_history = messages

    return {
        "reply":       reply,
        "history":     updated_history,
        "tool_calls":  tool_calls_log,
        "latency":     elapsed,
        "request":     all_requests,
        "response":    data,
    }
