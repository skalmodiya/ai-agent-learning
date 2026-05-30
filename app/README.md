# AI Agent Learning Platform — App

A Gradio web app that lets you explore all 8 AI Agent exercises in one place.
Click a tab, read the concept, then run the agent live and watch the animated flow.

## How to Run

```bash
cd app

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Launch the app
python app.py
```

Then open your browser at: **http://localhost:7860**

## What's in Each Tab

| Tab | Exercise | What you can do |
|---|---|---|
| 01 · Simple Agent | One message → one reply | Send any message, see raw JSON |
| 02 · Memory & Persona | Stateful conversation | Edit the system prompt live, watch turn counter grow |
| 03 · Tool Use | Agent calls functions | Ask math/weather questions, see tool call log |
| 04 · ReAct Loop | Think → Act → Observe | See full reasoning trace with Thought/Action/Observation |
| 05 · Multi-Agent | Planner + Writer | Watch two agents collaborate, see each agent's output |
| 06 · Streaming | Token-by-token output | Watch reply build character by character |
| 07 · Structured Output | JSON schema responses | Get structured data back, inspect each field |
| 08 · RAG | Answer from your docs | Ask policy questions, see which documents were retrieved |

## Three Panels Per Tab

```
┌──────────────┬────────────────────────┬──────────────────┐
│  📖 LEARN    │  ▶ TRY IT LIVE         │  🔄 HOW IT WORKS │
│              │                        │                  │
│  Concept     │  Live chat / input     │  Animated flow   │
│  explanation │  + metrics             │  diagram         │
│  + key terms │  + raw JSON toggle     │  (steps light up │
│              │                        │   as they run)   │
└──────────────┴────────────────────────┴──────────────────┘
```
