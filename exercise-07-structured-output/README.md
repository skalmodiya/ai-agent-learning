# Exercise 07 — Structured Output

## What's New vs Exercise 06

Force the AI to reply with **valid JSON** matching a schema you define.

## Example

Input: `"The laptop is fast but the battery drains quickly"`

Output:
```json
{
  "summary": "Fast laptop, poor battery life",
  "sentiment": "mixed",
  "score": -0.2,
  "keywords": ["fast", "battery", "drains"],
  "pros": ["speed"],
  "cons": ["battery life"]
}
```

## The Tool Trick

We define a fake `save_analysis` tool. The AI **must** call it to respond,
which forces it to produce structured JSON matching our schema.

## Key Concepts

| Term | Meaning |
|---|---|
| **JSON schema** | Specification for the exact shape of output |
| **tool_choice** | Force the model to call a specific tool |
| **Parsing** | Converting JSON string to a Python dict |
| **Structured data** | Machine-readable output you can use in code |

## How to Run

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python agent.py
```

## Try It

- "The new restaurant was incredible, best meal of my life"
- "The product arrived damaged and customer service was unhelpful"
- "The hotel was okay — good location but noisy rooms"

## Next Exercise

**Exercise 08** covers **RAG** — answering from your own documents.
