"""
Exercise 07 — Structured Output
New concept: force the AI to reply in a specific JSON schema
so you can parse and use the data programmatically.
"""

import requests
import time
import json
from . import config


CONCEPT = """
## Exercise 07 — Structured Output

### What's new vs Exercise 06
Instead of free-form text, we tell the AI to reply with **valid JSON**
matching a schema we define. This makes AI output machine-readable.

### Two approaches
**1. Prompt engineering** — tell the AI in the system prompt:
```
"Always reply in JSON with keys: summary, sentiment, keywords"
```

**2. Tool trick** — define a "save_result" tool with a strict schema.
   The AI must call it to respond, which forces structured output.

### Example
Input: `"Analyze this review: The laptop is fast but the battery drains quickly"`

Output:
```json
{
  "summary": "Laptop praised for speed, criticized for battery life",
  "sentiment": "mixed",
  "score": 0.4,
  "keywords": ["fast", "battery", "drains"],
  "pros": ["speed"],
  "cons": ["battery life"]
}
```

### Why structured output matters
- Parse AI responses like any API — no regex scraping
- Feed AI output directly into databases, UIs, or other services
- Enables AI-powered data extraction pipelines

### Key concepts
| Term | Meaning |
|---|---|
| **JSON schema** | A specification for the exact shape of JSON output |
| **Tool trick** | Using a fake tool to force structured calling |
| **Parsing** | Converting the JSON string to a Python dict |
| **Validation** | Checking the output matches the expected schema |
"""

FLOW_STEPS = [
    ("idle",    "```\nFree text in ──► JSON out\n```\n\n_Waiting for input..._"),
    ("send",    "```\n► Send message + schema tool\n  system: \"call save_result(...)\"\n```\n\n**Step 1:** Request sent with a schema-enforcing tool definition"),
    ("parse",   "```\n  AI must call save_result({...})\n► Extract tool_use input block\n```\n\n**Step 2:** AI returns a `tool_use` call with structured JSON as the input"),
    ("validate","```\n► Validate JSON matches schema\n  summary: str ✓\n  sentiment: str ✓\n  score: float ✓\n```\n\n**Step 3:** We parse and validate the structured data"),
    ("done",    "```\n► Return parsed Python dict\n  (not a raw string!)\n```\n\n**Done!** Structured data ready for use in any downstream system"),
]

# The schema-enforcing tool — AI must call this to respond
SCHEMA_TOOL = {
    "name": "save_analysis",
    "description": "Save the structured analysis result. You MUST call this tool to respond.",
    "input_schema": {
        "type": "object",
        "properties": {
            "summary":   {"type": "string",  "description": "One-sentence summary"},
            "sentiment": {"type": "string",  "enum": ["positive", "negative", "mixed", "neutral"]},
            "score":     {"type": "number",  "description": "Sentiment score from -1.0 (negative) to 1.0 (positive)"},
            "keywords":  {"type": "array",   "items": {"type": "string"}, "description": "Key words/phrases"},
            "pros":      {"type": "array",   "items": {"type": "string"}},
            "cons":      {"type": "array",   "items": {"type": "string"}},
        },
        "required": ["summary", "sentiment", "score", "keywords"],
    },
}

SYSTEM_PROMPT = (
    "You are a text analysis agent. For every input, you MUST call the "
    "`save_analysis` tool with your structured analysis. Never reply with plain text."
)


def run(user_message: str, cfg: dict = None) -> dict:
    """Analyze text and return structured JSON output."""
    cfg     = cfg or {}
    pid     = cfg.get("provider_id", config.DEFAULT_PROVIDER)
    model   = cfg.get("model",       config.get_default_model(pid))
    api_key = cfg.get("api_key",     "")
    headers = config.make_headers(pid, api_key)
    url     = config.get_chat_url(pid, model)

    payload = config.build_payload(
        pid, model,
        [{"role": "user", "content": user_message}],
        system=SYSTEM_PROMPT,
        tools=[SCHEMA_TOOL],
    )
    # Force the tool call (Anthropic-specific — ignored gracefully by others)
    if pid == "anthropic":
        payload["tool_choice"] = {"type": "tool", "name": "save_analysis"}

    t0 = time.time()
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    elapsed = round(time.time() - t0, 2)

    data    = response.json()
    content = data.get("content", [])

    # Extract the structured data from the tool_use block
    structured = None
    for block in content:
        if block.get("type") == "tool_use" and block.get("name") == "save_analysis":
            structured = block["input"]
            break

    return {
        "structured": structured,
        "reply":      json.dumps(structured, indent=2) if structured else "No structured output",
        "latency":    elapsed,
        "request":    payload,
        "response":   data,
    }
