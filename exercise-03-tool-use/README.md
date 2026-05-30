# Exercise 03 — Tool Use

## What's New vs Exercise 02

The agent can now **call functions** you define. This is the foundation of all real-world agents.

## The 3-Step Tool Dance

```
1. You ──► Agent: "What is 144 * 7?"
2. Agent ──► You: "Please call calculator({expression: '144*7'})"
3. You run it ──► Agent: "Result: 1008"
4. Agent ──► You: "144 × 7 = 1008"
```

## Tool Definition

```json
{
  "name": "calculator",
  "description": "Evaluate a math expression",
  "input_schema": {
    "type": "object",
    "properties": { "expression": {"type": "string"} },
    "required": ["expression"]
  }
}
```

## Key Concepts

| Term | Meaning |
|---|---|
| **Tool definition** | JSON schema describing a callable function |
| **tool_use block** | Agent's signal that it wants to call a tool |
| **tool_result** | Your response after executing the tool |
| **Agentic loop** | Keep calling API until `stop_reason == "end_turn"` |

## Available Tools

- **calculator** — evaluate any math expression
- **get_weather** — simulated weather for any city

## How to Run

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python agent.py
```

## Try It

- "What is 1234 * 5678?"
- "What's the weather in Tokyo?"
- "If the temp in Paris is 22°C, what is that in Fahrenheit?"

## Next Exercise

**Exercise 04** adds the **ReAct loop** — the agent narrates its Thought → Action → Observation reasoning explicitly.
