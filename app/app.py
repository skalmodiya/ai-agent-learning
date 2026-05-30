"""
AI Agent Learning Platform
===========================
A Gradio app with 8 tabs — one per exercise.
Each tab has 3 panels:
  📖 Learn      — concept explanation
  ▶  Try It     — live chat with the agent
  🔄 How It Works — animated step-by-step flow diagram
"""

import sys
import os
import time
import json

# Add parent directory so we can import app/exercises/
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import gradio as gr

from exercises import (
    ex01_simple,
    ex02_memory,
    ex03_tools,
    ex04_react,
    ex05_multi_agent,
    ex06_streaming,
    ex07_structured,
    ex08_rag,
)

# ─────────────────────────────────────────────
# THEME & CSS
# ─────────────────────────────────────────────

CSS = """
/* ── Base ─────────────────────────────────────────── */
body, .gradio-container, .main, footer { background: #0d1117 !important; }
.gradio-container { max-width: 100% !important; padding: 0 24px !important; }

/* ── Header ───────────────────────────────────────── */
.app-header { padding: 24px 0 8px 0; border-bottom: 1px solid #21262d; margin-bottom: 16px; }
.app-header h1 { font-size: 26px !important; font-weight: 700 !important; color: #e6edf3 !important; margin: 0 !important; }
.app-header p  { color: #8b949e !important; font-size: 14px !important; margin: 4px 0 0 0 !important; }

/* ── Tabs ─────────────────────────────────────────── */
.tab-nav { border-bottom: 1px solid #21262d !important; background: transparent !important; }
.tab-nav button {
    font-size: 13px !important; font-weight: 500 !important;
    color: #8b949e !important; background: transparent !important;
    border: none !important; border-bottom: 2px solid transparent !important;
    padding: 10px 18px !important; margin-bottom: -1px !important;
    transition: all 0.2s !important;
}
.tab-nav button:hover  { color: #c9d1d9 !important; }
.tab-nav button.selected {
    color: #58a6ff !important;
    border-bottom: 2px solid #58a6ff !important;
    background: transparent !important;
}

/* ── Panel cards ──────────────────────────────────── */
.panel-card {
    background: #161b22 !important;
    border: 1px solid #21262d !important;
    border-radius: 10px !important;
    padding: 20px !important;
}

/* ── Section labels (LEARN / TRY IT LIVE / HOW IT WORKS) ── */
.section-label .prose p, .section-label p {
    font-size: 11px !important; font-weight: 700 !important;
    letter-spacing: 1.5px !important; text-transform: uppercase !important;
    color: #58a6ff !important; margin: 0 0 12px 0 !important;
}

/* ── Learn panel ──────────────────────────────────── */
.learn-panel .prose { color: #c9d1d9 !important; font-size: 14px !important; line-height: 1.8 !important; }
.learn-panel .prose h2 { color: #58a6ff !important; font-size: 16px !important; margin-top: 0 !important; border-bottom: 1px solid #21262d; padding-bottom: 8px; }
.learn-panel .prose h3 { color: #bc8cff !important; font-size: 14px !important; margin-top: 16px !important; }
.learn-panel .prose p  { color: #8b949e !important; }

/* inline code */
.learn-panel .prose code {
    background: #1f2937 !important; color: #f97316 !important;
    padding: 2px 6px !important; border-radius: 4px !important;
    font-family: 'Fira Code', Consolas, monospace !important; font-size: 12px !important;
}

/* code blocks in Learn */
.learn-panel .prose pre {
    background: #0d1117 !important; border: 1px solid #21262d !important;
    border-radius: 8px !important; padding: 14px !important;
    overflow-x: auto !important;
}
.learn-panel .prose pre code {
    background: transparent !important; color: #7ee787 !important;
    font-size: 12px !important; padding: 0 !important;
}

/* tables */
.learn-panel .prose table { width: 100% !important; border-collapse: collapse !important; font-size: 13px !important; }
.learn-panel .prose thead tr { background: #1f2937 !important; }
.learn-panel .prose th { color: #58a6ff !important; padding: 8px 12px !important; text-align: left !important; font-weight: 600 !important; }
.learn-panel .prose td { color: #8b949e !important; padding: 7px 12px !important; border-top: 1px solid #21262d !important; }
.learn-panel .prose tr:hover td { background: #1f2937 !important; color: #c9d1d9 !important; }

/* ── Chatbot ───────────────────────────────────────── */
.chatbot, .chatbot > div, [data-testid="bot"], [data-testid="chatbot"] {
    background: #0d1117 !important;
    border: 1px solid #21262d !important;
    border-radius: 8px !important;
}
/* user bubble */
.chatbot .message-wrap .user {
    background: #1c3a5e !important; color: #cae8ff !important;
    border-radius: 12px 12px 2px 12px !important;
    border: 1px solid #1f4e8c !important; padding: 10px 14px !important;
}
/* bot bubble */
.chatbot .message-wrap .bot,
.chatbot .message-wrap .assistant {
    background: #1a2332 !important; color: #c9d1d9 !important;
    border-radius: 12px 12px 12px 2px !important;
    border: 1px solid #21262d !important; padding: 10px 14px !important;
}

/* ── Input box ────────────────────────────────────── */
textarea, input[type="text"] {
    background: #161b22 !important; color: #e6edf3 !important;
    border: 1px solid #30363d !important; border-radius: 8px !important;
    font-size: 14px !important;
}
textarea:focus, input[type="text"]:focus {
    border-color: #58a6ff !important; outline: none !important;
    box-shadow: 0 0 0 3px rgba(88,166,255,0.1) !important;
}
textarea::placeholder, input::placeholder { color: #484f58 !important; }

/* ── Buttons ──────────────────────────────────────── */
button.primary, .send-btn {
    background: #1f6feb !important; color: #ffffff !important;
    border: none !important; border-radius: 8px !important;
    font-weight: 600 !important; font-size: 13px !important;
    padding: 8px 20px !important; transition: background 0.2s !important;
}
button.primary:hover, .send-btn:hover { background: #388bfd !important; }
button.secondary {
    background: #21262d !important; color: #8b949e !important;
    border: 1px solid #30363d !important; border-radius: 8px !important;
}
button.secondary:hover { background: #30363d !important; color: #c9d1d9 !important; }

/* ── Flow / How It Works panel ────────────────────── */
.flow-box .prose {
    font-family: 'Fira Code', Consolas, monospace !important;
    font-size: 12.5px !important; line-height: 1.75 !important;
    color: #7ee787 !important;
}
.flow-box .prose code, .flow-box .prose pre {
    background: #0d1117 !important; color: #7ee787 !important;
    border: 1px solid #21262d !important; border-radius: 6px !important;
}
.flow-box .prose strong { color: #ffa657 !important; }
.flow-box .prose em     { color: #bc8cff !important; }
.flow-box .prose p      { color: #8b949e !important; }
.flow-box .prose hr     { border-color: #21262d !important; }

/* ── Latency / info badges ────────────────────────── */
.latency-box textarea, .latency-box input {
    background: #161b22 !important; border: 1px solid #21262d !important;
    color: #3fb950 !important; font-size: 12px !important;
    font-weight: 600 !important; text-align: center !important;
    border-radius: 6px !important;
}

/* ── Accordion ────────────────────────────────────── */
.gr-accordion { background: #161b22 !important; border: 1px solid #21262d !important; border-radius: 8px !important; }
.gr-accordion summary { color: #8b949e !important; font-size: 13px !important; }

/* ── JSON viewer ──────────────────────────────────── */
.json-holder { background: #0d1117 !important; color: #7ee787 !important; border-radius: 8px !important; }

/* ── Scrollbars ───────────────────────────────────── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0d1117; }
::-webkit-scrollbar-thumb { background: #30363d; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #484f58; }
"""

# ─────────────────────────────────────────────
# FLOW ANIMATION HELPER
# ─────────────────────────────────────────────

def animate_flow(steps: list, active_idx: int) -> str:
    """
    Build a markdown string where the active step is highlighted
    and all previous steps are shown as completed (✓).
    steps: list of (key, markdown_text) tuples from each exercise module
    """
    lines = []
    for i, (_, text) in enumerate(steps):
        if i < active_idx:
            # Completed step — show green tick prefix on first line
            first_line = text.split("\n")[0]
            lines.append(f"✅ ~~{first_line}~~\n")
        elif i == active_idx:
            # Active step — show full text
            lines.append(text + "\n")
        # Future steps are hidden until reached
    return "\n---\n".join(lines)


# ─────────────────────────────────────────────
# PER-EXERCISE TAB BUILDERS
# ─────────────────────────────────────────────

def build_ex01_tab():
    state = gr.State({"history": []})

    with gr.Row(equal_height=False):
        # ── Panel 1: Learn ──
        with gr.Column(scale=3, elem_classes="panel-card learn-panel"):
            gr.Markdown("### 📖 Learn", elem_classes="section-label")
            gr.Markdown(ex01_simple.CONCEPT)

        # ── Panel 2: Try It ──
        with gr.Column(scale=4, elem_classes="panel-card"):
            gr.Markdown("### ▶ Try It Live", elem_classes="section-label")
            chatbot   = gr.Chatbot(height=360, label="", show_label=False)
            msg_input = gr.Textbox(placeholder="Type a message...", show_label=False, lines=1)
            with gr.Row():
                send_btn  = gr.Button("Send", variant="primary", elem_classes="send-btn")
                clear_btn = gr.Button("Clear", variant="secondary")
            latency   = gr.Textbox(label="", value="⏱ Latency: —", interactive=False,
                                   elem_classes="latency-box", max_lines=1)
            with gr.Accordion("🔍 Raw JSON (last request/response)", open=False):
                raw_json = gr.JSON(label="")

        # ── Panel 3: How It Works ──
        with gr.Column(scale=3, elem_classes="panel-card"):
            gr.Markdown("### 🔄 How It Works", elem_classes="section-label")
            flow_display = gr.Markdown(
                ex01_simple.FLOW_STEPS[0][1], elem_classes="flow-box"
            )

    def respond(message, history, s):
        if not message.strip():
            return history, s, "⏱ Latency: —", None, animate_flow(ex01_simple.FLOW_STEPS, 0)
        try:
            # Animate: input
            yield history, s, "⏱ Sending...", None, animate_flow(ex01_simple.FLOW_STEPS, 1)
            time.sleep(0.3)
            yield history, s, "⏱ Sending...", None, animate_flow(ex01_simple.FLOW_STEPS, 2)
            time.sleep(0.3)
            yield history, s, "⏱ Waiting for AI...", None, animate_flow(ex01_simple.FLOW_STEPS, 3)

            result = ex01_simple.run(message)

            yield history, s, "⏱ Parsing...", None, animate_flow(ex01_simple.FLOW_STEPS, 4)
            time.sleep(0.2)

            history = history + [[message, result["reply"]]]
            yield (history, s, f"⏱ Latency: {result['latency']}s",
                   {"request": result["request"], "response": result["response"]},
                   animate_flow(ex01_simple.FLOW_STEPS, 5))
        except Exception as e:
            history = history + [[message, f"❌ Error: {e}"]]
            yield history, s, "⏱ Error", None, animate_flow(ex01_simple.FLOW_STEPS, 0)

    send_btn.click(respond, [msg_input, chatbot, state],
                   [chatbot, state, latency, raw_json, flow_display])
    msg_input.submit(respond, [msg_input, chatbot, state],
                     [chatbot, state, latency, raw_json, flow_display])
    clear_btn.click(lambda: ([], {"history": []}, "⏱ Latency: —", None, ex01_simple.FLOW_STEPS[0][1]),
                    outputs=[chatbot, state, latency, raw_json, flow_display])


def build_ex02_tab():
    state = gr.State({"history": []})

    with gr.Row(equal_height=False):
        with gr.Column(scale=3, elem_classes="panel-card learn-panel"):
            gr.Markdown("### 📖 Learn", elem_classes="section-label")
            gr.Markdown(ex02_memory.CONCEPT)

        with gr.Column(scale=4, elem_classes="panel-card"):
            gr.Markdown("### ▶ Try It Live", elem_classes="section-label")
            persona_input = gr.Textbox(
                value=ex02_memory.DEFAULT_PERSONA,
                label="System Prompt (persona) — edit me!",
                lines=2,
            )
            chatbot   = gr.Chatbot(height=300, label="", show_label=False)
            msg_input = gr.Textbox(placeholder="Type a message...", show_label=False, lines=1)
            with gr.Row():
                send_btn  = gr.Button("Send", variant="primary", elem_classes="send-btn")
                clear_btn = gr.Button("Clear Chat", variant="secondary")
            latency = gr.Textbox(label="", value="⏱ Latency: —", interactive=False,
                                 elem_classes="latency-box", max_lines=1)
            turn_count = gr.Textbox(label="", value="💬 Turns: 0", interactive=False,
                                    elem_classes="latency-box", max_lines=1)

        with gr.Column(scale=3, elem_classes="panel-card"):
            gr.Markdown("### 🔄 How It Works", elem_classes="section-label")
            flow_display = gr.Markdown(ex02_memory.FLOW_STEPS[0][1], elem_classes="flow-box")

    def respond(message, history, s, persona):
        if not message.strip():
            return history, s, "⏱ Latency: —", f"💬 Turns: {len(s['history'])//2}", animate_flow(ex02_memory.FLOW_STEPS, 0)
        try:
            yield history, s, "⏱ Sending...", f"💬 Turns: {len(s['history'])//2}", animate_flow(ex02_memory.FLOW_STEPS, 1)
            time.sleep(0.3)
            yield history, s, "⏱ Sending...", f"💬 Turns: {len(s['history'])//2}", animate_flow(ex02_memory.FLOW_STEPS, 2)
            time.sleep(0.2)
            yield history, s, "⏱ Waiting for AI...", f"💬 Turns: {len(s['history'])//2}", animate_flow(ex02_memory.FLOW_STEPS, 3)

            result = ex02_memory.run(message, s["history"], persona)
            s["history"] = result["history"]

            history = history + [[message, result["reply"]]]
            yield (history, s, f"⏱ Latency: {result['latency']}s",
                   f"💬 Turns: {len(s['history'])//2}",
                   animate_flow(ex02_memory.FLOW_STEPS, 5))
        except Exception as e:
            history = history + [[message, f"❌ Error: {e}"]]
            yield history, s, "⏱ Error", f"💬 Turns: {len(s['history'])//2}", animate_flow(ex02_memory.FLOW_STEPS, 0)

    send_btn.click(respond, [msg_input, chatbot, state, persona_input],
                   [chatbot, state, latency, turn_count, flow_display])
    msg_input.submit(respond, [msg_input, chatbot, state, persona_input],
                     [chatbot, state, latency, turn_count, flow_display])
    clear_btn.click(lambda: ([], {"history": []}, "⏱ Latency: —", "💬 Turns: 0", ex02_memory.FLOW_STEPS[0][1]),
                    outputs=[chatbot, state, latency, turn_count, flow_display])


def build_ex03_tab():
    state = gr.State({"history": []})

    with gr.Row(equal_height=False):
        with gr.Column(scale=3, elem_classes="panel-card learn-panel"):
            gr.Markdown("### 📖 Learn", elem_classes="section-label")
            gr.Markdown(ex03_tools.CONCEPT)

        with gr.Column(scale=4, elem_classes="panel-card"):
            gr.Markdown("### ▶ Try It Live", elem_classes="section-label")
            chatbot   = gr.Chatbot(height=320, label="", show_label=False)
            msg_input = gr.Textbox(
                placeholder="Try: 'What is 1234 * 5678?' or 'Weather in Tokyo?'",
                show_label=False, lines=1
            )
            with gr.Row():
                send_btn  = gr.Button("Send", variant="primary", elem_classes="send-btn")
                clear_btn = gr.Button("Clear", variant="secondary")
            latency = gr.Textbox(label="", value="⏱ Latency: —", interactive=False,
                                 elem_classes="latency-box", max_lines=1)
            with gr.Accordion("🔧 Tool Calls Log", open=True):
                tool_log = gr.JSON(label="", value=[])

        with gr.Column(scale=3, elem_classes="panel-card"):
            gr.Markdown("### 🔄 How It Works", elem_classes="section-label")
            flow_display = gr.Markdown(ex03_tools.FLOW_STEPS[0][1], elem_classes="flow-box")

    def respond(message, history, s):
        if not message.strip():
            return history, s, "⏱ Latency: —", [], animate_flow(ex03_tools.FLOW_STEPS, 0)
        try:
            yield history, s, "⏱ Sending...", [], animate_flow(ex03_tools.FLOW_STEPS, 1)
            time.sleep(0.3)
            yield history, s, "⏱ AI deciding...", [], animate_flow(ex03_tools.FLOW_STEPS, 2)

            result = ex03_tools.run(message, s["history"])
            s["history"] = result["history"]

            # Animate through tool call steps if tools were used
            if result["tool_calls"]:
                yield history, s, "⏱ Tool called!", result["tool_calls"], animate_flow(ex03_tools.FLOW_STEPS, 3)
                time.sleep(0.4)
                yield history, s, "⏱ Executing...", result["tool_calls"], animate_flow(ex03_tools.FLOW_STEPS, 4)
                time.sleep(0.3)
                yield history, s, "⏱ Feeding result back...", result["tool_calls"], animate_flow(ex03_tools.FLOW_STEPS, 5)
                time.sleep(0.3)

            history = history + [[message, result["reply"]]]
            yield (history, s, f"⏱ Latency: {result['latency']}s",
                   result["tool_calls"], animate_flow(ex03_tools.FLOW_STEPS, 6))
        except Exception as e:
            history = history + [[message, f"❌ Error: {e}"]]
            yield history, s, "⏱ Error", [], animate_flow(ex03_tools.FLOW_STEPS, 0)

    send_btn.click(respond, [msg_input, chatbot, state],
                   [chatbot, state, latency, tool_log, flow_display])
    msg_input.submit(respond, [msg_input, chatbot, state],
                     [chatbot, state, latency, tool_log, flow_display])
    clear_btn.click(lambda: ([], {"history": []}, "⏱ Latency: —", [], ex03_tools.FLOW_STEPS[0][1]),
                    outputs=[chatbot, state, latency, tool_log, flow_display])


def build_ex04_tab():
    with gr.Row(equal_height=False):
        with gr.Column(scale=3, elem_classes="panel-card learn-panel"):
            gr.Markdown("### 📖 Learn", elem_classes="section-label")
            gr.Markdown(ex04_react.CONCEPT)

        with gr.Column(scale=4, elem_classes="panel-card"):
            gr.Markdown("### ▶ Try It Live", elem_classes="section-label")
            gr.Markdown(
                "_This agent shows its full Thought → Action → Observation chain._",
                elem_classes="section-label"
            )
            trace_box = gr.Markdown("_Run a query to see the ReAct trace here..._")
            msg_input = gr.Textbox(
                placeholder="Try: 'What is the square root of Earth's radius in km?'",
                show_label=False, lines=1
            )
            with gr.Row():
                send_btn = gr.Button("Send", variant="primary", elem_classes="send-btn")
            latency = gr.Textbox(label="", value="⏱ Latency: —", interactive=False,
                                 elem_classes="latency-box", max_lines=1)

        with gr.Column(scale=3, elem_classes="panel-card"):
            gr.Markdown("### 🔄 How It Works", elem_classes="section-label")
            flow_display = gr.Markdown(ex04_react.FLOW_STEPS[0][1], elem_classes="flow-box")

    def respond(message):
        if not message.strip():
            return "_Enter a question..._", "⏱ Latency: —", animate_flow(ex04_react.FLOW_STEPS, 0)
        yield "⏳ _Thinking..._", "⏱ Running ReAct loop...", animate_flow(ex04_react.FLOW_STEPS, 1)
        time.sleep(0.3)
        yield "⏳ _Thinking..._", "⏱ Running ReAct loop...", animate_flow(ex04_react.FLOW_STEPS, 2)
        try:
            result = ex04_react.run(message)
            # Format the trace nicely
            trace_md = "### ReAct Trace\n\n"
            for step in result["trace"]:
                if step["type"] == "thought":
                    trace_md += f"```\n{step['text']}\n```\n\n"
                elif step["type"] == "action":
                    trace_md += f"**🔧 Tool:** `{step['tool']}({json.dumps(step['input'])})`\n\n"
                    trace_md += f"**📋 Result:** `{step['result']}`\n\n"
            trace_md += f"\n---\n**Final Answer:** {result['reply']}"
            yield trace_md, f"⏱ Latency: {result['latency']}s", animate_flow(ex04_react.FLOW_STEPS, 5)
        except Exception as e:
            yield f"❌ Error: {e}", "⏱ Error", animate_flow(ex04_react.FLOW_STEPS, 0)

    send_btn.click(respond, [msg_input], [trace_box, latency, flow_display])
    msg_input.submit(respond, [msg_input], [trace_box, latency, flow_display])


def build_ex05_tab():
    with gr.Row(equal_height=False):
        with gr.Column(scale=3, elem_classes="panel-card learn-panel"):
            gr.Markdown("### 📖 Learn", elem_classes="section-label")
            gr.Markdown(ex05_multi_agent.CONCEPT)

        with gr.Column(scale=4, elem_classes="panel-card"):
            gr.Markdown("### ▶ Try It Live", elem_classes="section-label")
            with gr.Accordion("🧠 Planner Output", open=True):
                planner_box = gr.Markdown("_Run a task to see the plan..._")
            with gr.Accordion("✍️ Writer Output", open=True):
                writer_box  = gr.Markdown("_Run a task to see the result..._")
            msg_input = gr.Textbox(
                placeholder="Try: 'Write a blog post about AI Agents'",
                show_label=False, lines=1
            )
            with gr.Row():
                send_btn = gr.Button("Send", variant="primary", elem_classes="send-btn")
            latency = gr.Textbox(label="", value="⏱ Latency: —", interactive=False,
                                 elem_classes="latency-box", max_lines=1)

        with gr.Column(scale=3, elem_classes="panel-card"):
            gr.Markdown("### 🔄 How It Works", elem_classes="section-label")
            flow_display = gr.Markdown(ex05_multi_agent.FLOW_STEPS[0][1], elem_classes="flow-box")

    def respond(message):
        if not message.strip():
            return "_Enter a task..._", "_..._", "⏱ Latency: —", animate_flow(ex05_multi_agent.FLOW_STEPS, 0)
        yield "_Planner thinking..._", "_Waiting for plan..._", "⏱ Running...", animate_flow(ex05_multi_agent.FLOW_STEPS, 1)
        time.sleep(0.3)
        try:
            result = ex05_multi_agent.run(message)
            yield (f"### Planner's Plan\n\n{result['plan']}",
                   "_Writer executing..._",
                   f"⏱ Running...",
                   animate_flow(ex05_multi_agent.FLOW_STEPS, 3))
            time.sleep(0.3)
            yield (f"### Planner's Plan\n\n{result['plan']}",
                   f"### Writer's Output\n\n{result['reply']}",
                   f"⏱ Latency: {result['latency']}s",
                   animate_flow(ex05_multi_agent.FLOW_STEPS, 4))
        except Exception as e:
            yield f"❌ Error: {e}", "", "⏱ Error", animate_flow(ex05_multi_agent.FLOW_STEPS, 0)

    send_btn.click(respond, [msg_input], [planner_box, writer_box, latency, flow_display])
    msg_input.submit(respond, [msg_input], [planner_box, writer_box, latency, flow_display])


def build_ex06_tab():
    state = gr.State({"history": []})

    with gr.Row(equal_height=False):
        with gr.Column(scale=3, elem_classes="panel-card learn-panel"):
            gr.Markdown("### 📖 Learn", elem_classes="section-label")
            gr.Markdown(ex06_streaming.CONCEPT)

        with gr.Column(scale=4, elem_classes="panel-card"):
            gr.Markdown("### ▶ Try It Live", elem_classes="section-label")
            gr.Markdown("_Watch tokens arrive one by one — the reply builds in real time._",
                        elem_classes="section-label")
            chatbot   = gr.Chatbot(height=320, label="", show_label=False)
            msg_input = gr.Textbox(placeholder="Type a message...", show_label=False, lines=1)
            with gr.Row():
                send_btn  = gr.Button("Send", variant="primary", elem_classes="send-btn")
                clear_btn = gr.Button("Clear", variant="secondary")
            with gr.Row():
                latency    = gr.Textbox(label="", value="⏱ Latency: —", interactive=False,
                                        elem_classes="latency-box", max_lines=1)
                chunk_count = gr.Textbox(label="", value="📦 Chunks: 0", interactive=False,
                                         elem_classes="latency-box", max_lines=1)

        with gr.Column(scale=3, elem_classes="panel-card"):
            gr.Markdown("### 🔄 How It Works", elem_classes="section-label")
            flow_display = gr.Markdown(ex06_streaming.FLOW_STEPS[0][1], elem_classes="flow-box")

    def respond(message, history, s):
        if not message.strip():
            return history, s, "⏱ Latency: —", "📦 Chunks: 0", animate_flow(ex06_streaming.FLOW_STEPS, 0)
        yield history, s, "⏱ Connecting...", "📦 Chunks: 0", animate_flow(ex06_streaming.FLOW_STEPS, 1)
        time.sleep(0.2)
        yield history, s, "⏱ Streaming...", "📦 Chunks: 0", animate_flow(ex06_streaming.FLOW_STEPS, 2)

        try:
            t0 = time.time()
            accumulated = ""
            chunk_n = 0
            # Stream tokens into the chatbot live using [user, partial_bot] tuples
            for chunk in ex06_streaming.run_stream(message, s["history"]):
                accumulated += chunk
                chunk_n += 1
                current_history = history + [[message, accumulated]]
                yield (current_history, s,
                       f"⏱ Streaming... {round(time.time()-t0,1)}s",
                       f"📦 Chunks: {chunk_n}",
                       animate_flow(ex06_streaming.FLOW_STEPS, 3))

            elapsed = round(time.time() - t0, 2)
            s["history"] += [{"role":"user","content":message},
                              {"role":"assistant","content":accumulated}]
            final_history = history + [[message, accumulated]]
            yield (final_history, s,
                   f"⏱ Latency: {elapsed}s",
                   f"📦 Chunks: {chunk_n}",
                   animate_flow(ex06_streaming.FLOW_STEPS, 4))
        except Exception as e:
            err_history = history + [[message, f"❌ Error: {e}"]]
            yield err_history, s, "⏱ Error", "📦 Chunks: 0", animate_flow(ex06_streaming.FLOW_STEPS, 0)

    send_btn.click(respond, [msg_input, chatbot, state],
                   [chatbot, state, latency, chunk_count, flow_display])
    msg_input.submit(respond, [msg_input, chatbot, state],
                     [chatbot, state, latency, chunk_count, flow_display])
    clear_btn.click(lambda: ([], {"history": []}, "⏱ Latency: —", "📦 Chunks: 0", ex06_streaming.FLOW_STEPS[0][1]),
                    outputs=[chatbot, state, latency, chunk_count, flow_display])


def build_ex07_tab():
    with gr.Row(equal_height=False):
        with gr.Column(scale=3, elem_classes="panel-card learn-panel"):
            gr.Markdown("### 📖 Learn", elem_classes="section-label")
            gr.Markdown(ex07_structured.CONCEPT)

        with gr.Column(scale=4, elem_classes="panel-card"):
            gr.Markdown("### ▶ Try It Live", elem_classes="section-label")
            gr.Markdown("_Enter any text to analyze — get back structured JSON._",
                        elem_classes="section-label")
            msg_input = gr.Textbox(
                placeholder="Try: 'The new phone is amazing but the battery drains too fast'",
                show_label=False, lines=2
            )
            send_btn = gr.Button("Analyze", variant="primary", elem_classes="send-btn")
            latency  = gr.Textbox(label="", value="⏱ Latency: —", interactive=False,
                                  elem_classes="latency-box", max_lines=1)

            with gr.Row():
                with gr.Column():
                    gr.Markdown("**Summary & Sentiment**")
                    summary_box   = gr.Textbox(label="Summary",   interactive=False, lines=2)
                    sentiment_box = gr.Textbox(label="Sentiment", interactive=False)
                    score_box     = gr.Textbox(label="Score (-1 to +1)", interactive=False)
                with gr.Column():
                    gr.Markdown("**Keywords & Details**")
                    keywords_box = gr.Textbox(label="Keywords", interactive=False)
                    pros_box     = gr.Textbox(label="Pros",     interactive=False)
                    cons_box     = gr.Textbox(label="Cons",     interactive=False)

            with gr.Accordion("🔍 Raw JSON", open=False):
                raw_json = gr.JSON(label="")

        with gr.Column(scale=3, elem_classes="panel-card"):
            gr.Markdown("### 🔄 How It Works", elem_classes="section-label")
            flow_display = gr.Markdown(ex07_structured.FLOW_STEPS[0][1], elem_classes="flow-box")

    def respond(message):
        if not message.strip():
            return ("⏱ Latency: —", "", "", "", "", "", "", None,
                    animate_flow(ex07_structured.FLOW_STEPS, 0))
        yield ("⏱ Sending...", "", "", "", "", "", "", None,
               animate_flow(ex07_structured.FLOW_STEPS, 1))
        time.sleep(0.3)
        yield ("⏱ AI analyzing...", "", "", "", "", "", "", None,
               animate_flow(ex07_structured.FLOW_STEPS, 2))
        try:
            result = ex07_structured.run(message)
            s = result["structured"] or {}
            yield ("⏱ Validating...", "", "", "", "", "", "", None,
                   animate_flow(ex07_structured.FLOW_STEPS, 3))
            time.sleep(0.2)
            yield (
                f"⏱ Latency: {result['latency']}s",
                s.get("summary", ""),
                s.get("sentiment", ""),
                str(s.get("score", "")),
                ", ".join(s.get("keywords", [])),
                ", ".join(s.get("pros", [])),
                ", ".join(s.get("cons", [])),
                s,
                animate_flow(ex07_structured.FLOW_STEPS, 4),
            )
        except Exception as e:
            yield (f"⏱ Error", str(e), "", "", "", "", "", None,
                   animate_flow(ex07_structured.FLOW_STEPS, 0))

    send_btn.click(respond, [msg_input],
                   [latency, summary_box, sentiment_box, score_box,
                    keywords_box, pros_box, cons_box, raw_json, flow_display])
    msg_input.submit(respond, [msg_input],
                     [latency, summary_box, sentiment_box, score_box,
                      keywords_box, pros_box, cons_box, raw_json, flow_display])


def build_ex08_tab():
    with gr.Row(equal_height=False):
        with gr.Column(scale=3, elem_classes="panel-card learn-panel"):
            gr.Markdown("### 📖 Learn", elem_classes="section-label")
            gr.Markdown(ex08_rag.CONCEPT)
            gr.Markdown("### 📄 Document Store")
            for doc in ex08_rag.DOCUMENTS:
                with gr.Accordion(f"📄 {doc['title']}", open=False):
                    gr.Markdown(doc["content"])

        with gr.Column(scale=4, elem_classes="panel-card"):
            gr.Markdown("### ▶ Try It Live", elem_classes="section-label")
            chatbot   = gr.Chatbot(height=300, label="", show_label=False)
            msg_input = gr.Textbox(
                placeholder="Try: 'How many leave days do I get?'",
                show_label=False, lines=1
            )
            with gr.Row():
                send_btn  = gr.Button("Ask", variant="primary", elem_classes="send-btn")
                clear_btn = gr.Button("Clear", variant="secondary")
            latency = gr.Textbox(label="", value="⏱ Latency: —", interactive=False,
                                 elem_classes="latency-box", max_lines=1)
            with gr.Accordion("📚 Retrieved Documents", open=True):
                sources_box = gr.Markdown("_Ask a question to see which docs were retrieved._")

        with gr.Column(scale=3, elem_classes="panel-card"):
            gr.Markdown("### 🔄 How It Works", elem_classes="section-label")
            flow_display = gr.Markdown(ex08_rag.FLOW_STEPS[0][1], elem_classes="flow-box")

    def respond(message, history):
        if not message.strip():
            return history, "⏱ Latency: —", "_..._", animate_flow(ex08_rag.FLOW_STEPS, 0)
        yield history, "⏱ Sending...", "_..._", animate_flow(ex08_rag.FLOW_STEPS, 1)
        time.sleep(0.2)
        yield history, "⏱ Retrieving docs...", "_Searching document store..._", animate_flow(ex08_rag.FLOW_STEPS, 2)
        time.sleep(0.3)
        yield history, "⏱ Building prompt...", "_Injecting context..._", animate_flow(ex08_rag.FLOW_STEPS, 3)
        time.sleep(0.2)
        yield history, "⏱ AI generating...", "_Generating grounded answer..._", animate_flow(ex08_rag.FLOW_STEPS, 4)
        try:
            result = ex08_rag.run(message)
            history = history + [[message, result["reply"]]]
            sources_md = "**Retrieved:** " + " · ".join(f"`{s}`" for s in result["sources"])
            yield (history, f"⏱ Latency: {result['latency']}s",
                   sources_md, animate_flow(ex08_rag.FLOW_STEPS, 5))
        except Exception as e:
            history = history + [[message, f"❌ Error: {e}"]]
            yield history, "⏱ Error", "_Error_", animate_flow(ex08_rag.FLOW_STEPS, 0)

    send_btn.click(respond, [msg_input, chatbot],
                   [chatbot, latency, sources_box, flow_display])
    msg_input.submit(respond, [msg_input, chatbot],
                     [chatbot, latency, sources_box, flow_display])
    clear_btn.click(lambda: ([], "⏱ Latency: —", "_..._", ex08_rag.FLOW_STEPS[0][1]),
                    outputs=[chatbot, latency, sources_box, flow_display])


# ─────────────────────────────────────────────
# MAIN APP ASSEMBLY
# ─────────────────────────────────────────────

def build_app():
    with gr.Blocks(title="AI Agent Learning Platform") as app:

        gr.HTML("""
<div style="padding:24px 0 16px 0; border-bottom:1px solid #21262d; margin-bottom:8px;">
  <div style="display:flex; align-items:center; gap:12px;">
    <span style="font-size:32px;">🤖</span>
    <div>
      <h1 style="margin:0; font-size:24px; font-weight:700; color:#e6edf3;">AI Agent Learning Platform</h1>
      <p style="margin:4px 0 0 0; font-size:14px; color:#8b949e;">
        Learn AI Agents from scratch — one concept per tab &nbsp;·&nbsp; Try each agent live &nbsp;·&nbsp; Watch animated flows
      </p>
    </div>
  </div>
  <div style="display:flex; gap:8px; margin-top:16px; flex-wrap:wrap;">
    <span style="background:#1f2937; color:#58a6ff; border:1px solid #1f4e8c; border-radius:20px; padding:3px 12px; font-size:12px; font-weight:600;">8 Exercises</span>
    <span style="background:#1f2937; color:#3fb950; border:1px solid #1a4731; border-radius:20px; padding:3px 12px; font-size:12px; font-weight:600;">Simple → RAG</span>
    <span style="background:#1f2937; color:#bc8cff; border:1px solid #3d2060; border-radius:20px; padding:3px 12px; font-size:12px; font-weight:600;">Live Chat + Animations</span>
  </div>
</div>
""")

        with gr.Tabs():
            with gr.Tab("01 · Simple Agent"):
                build_ex01_tab()
            with gr.Tab("02 · Memory & Persona"):
                build_ex02_tab()
            with gr.Tab("03 · Tool Use"):
                build_ex03_tab()
            with gr.Tab("04 · ReAct Loop"):
                build_ex04_tab()
            with gr.Tab("05 · Multi-Agent"):
                build_ex05_tab()
            with gr.Tab("06 · Streaming"):
                build_ex06_tab()
            with gr.Tab("07 · Structured Output"):
                build_ex07_tab()
            with gr.Tab("08 · RAG"):
                build_ex08_tab()

        gr.HTML("""
<div style="text-align:center; color:#484f58; font-size:12px; padding:16px 0; border-top:1px solid #21262d; margin-top:8px;">
  AI Agent Learning Series &nbsp;·&nbsp; 8 exercises from Simple → RAG &nbsp;·&nbsp;
  <a href="https://github.com/skalmodiya/ai-agent-learning" style="color:#58a6ff; text-decoration:none;">GitHub ↗</a>
</div>
""")

    return app


if __name__ == "__main__":
    app = build_app()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
        css=CSS,
        theme=gr.themes.Base(
            primary_hue="blue",
            neutral_hue="slate",
            font=gr.themes.GoogleFont("Inter"),
        ),
    )
