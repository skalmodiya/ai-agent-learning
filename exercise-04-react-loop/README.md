# Exercise 04 — ReAct Loop

## What's New vs Exercise 03

In Exercise 03 the agent used tools silently. ReAct makes the reasoning **visible**:

```
Thought:     "I need the population of Tokyo"
Action:      lookup_fact(query="Tokyo population")
Observation: "~13.96M city / 37.4M metro"
Thought:     "Now I can answer"
Final Answer: "Tokyo has ~14 million people in the city."
```

## Why ReAct Matters

- Reasoning is **transparent and debuggable**
- Agent can **self-correct** based on observations
- Foundation of LangChain, AutoGPT, and most agent frameworks
- Coined by Google Research paper (2022)

## Key Concepts

| Term | Meaning |
|---|---|
| **Thought** | Internal reasoning step (visible) |
| **Action** | A tool call with structured arguments |
| **Observation** | Result returned from the tool |
| **ReAct** | Reasoning + Acting interleaved |

## How to Run

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python agent.py
```

## Try It

- "What is the square root of the Earth's radius in km?"
- "How fast would you travel at the speed of light for 10 seconds? (in km)"
- "What year was Python released, and how many years ago was that?"

## Next Exercise

**Exercise 05** introduces **Multi-Agent** — two specialized agents collaborating on a task.
