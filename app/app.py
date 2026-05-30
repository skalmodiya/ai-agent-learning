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
/* Overall background */
body, .gradio-container { background: #0f1117 !important; }

/* Tab styling */
.tab-nav button {
    font-size: 13px !important;
    font-weight: 600 !important;
    color: #a0aec0 !important;
    border-radius: 8px 8px 0 0 !important;
    padding: 8px 16px !important;
}
.tab-nav button.selected {
    color: #63b3ed !important;
    border-bottom: 2px solid #63b3ed !important;
    background: #1a202c !important;
}

/* Panel cards */
.panel-card {
    background: #1a202c;
    border: 1px solid #2d3748;
    border-radius: 12px;
    padding: 16px;
}

/* Flow diagram — monospace box */
.flow-box textarea, .flow-box .prose {
    font-family: 'Fira Code', 'Consolas', monospace !important;
    font-size: 13px !important;
    line-height: 1.7 !important;
    background: #0d1117 !important;
    color: #7ee787 !important;
    border: 1px solid #30363d !important;
    border-radius: 8px !important;
}

/* Learn panel markdown */
.learn-panel .prose {
    font-size: 14px !important;
    line-height: 1.8 !important;
}
.learn-panel .prose h2 { color: #63b3ed !important; margin-top: 0 !important; }
.learn-panel .prose h3 { color: #9f7aea !important; }
.learn-panel .prose code { background: #2d3748 !important; color: #fbd38d !important; }
.learn-panel .prose table { width: 100% !important; }
.learn-panel .prose th { background: #2d3748 !important; color: #a0aec0 !important; }

/* Chatbot */
.chatbot .message.user   { background: #2a4a7f !important; border-radius: 12px !important; }
.chatbot .message.bot    { background: #1e3a2a !important; border-radius: 12px !important; }

/* Latency badge */
.latency-box {
    background: #1a202c !important;
    border: 1px solid #2d3748 !important;
    border-radius: 8px !important;
    font-size: 12px !important;
    color: #68d391 !important;
    text-align: center !important;
}

/* Send button */
.send-btn { background: #2b6cb0 !important; color: white !important; border-radius: 8px !important; }

/* Section labels */
.section-label {
    font-size: 11px !important;
    font-weight: 700 !important;
    letter-spacing: 1px !important;
    color: #718096 !important;
    text-transform: uppercase !important;
    margin-bottom: 6px !important;
}
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
            chatbot   = gr.Chatbot(height=360, label="", show_label=False, type="messages")
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

            history = history + [{"role": "user", "content": message},
                                  {"role": "assistant", "content": result["reply"]}]
            yield (history, s, f"⏱ Latency: {result['latency']}s",
                   {"request": result["request"], "response": result["response"]},
                   animate_flow(ex01_simple.FLOW_STEPS, 5))
        except Exception as e:
            history = history + [{"role": "user", "content": message},
                                  {"role": "assistant", "content": f"❌ Error: {e}"}]
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
            chatbot   = gr.Chatbot(height=300, label="", show_label=False, type="messages")
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

            history = history + [{"role": "user", "content": message},
                                  {"role": "assistant", "content": result["reply"]}]
            yield (history, s, f"⏱ Latency: {result['latency']}s",
                   f"💬 Turns: {len(s['history'])//2}",
                   animate_flow(ex02_memory.FLOW_STEPS, 5))
        except Exception as e:
            history = history + [{"role": "user", "content": message},
                                  {"role": "assistant", "content": f"❌ Error: {e}"}]
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
            chatbot   = gr.Chatbot(height=320, label="", show_label=False, type="messages")
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

            history = history + [{"role": "user", "content": message},
                                  {"role": "assistant", "content": result["reply"]}]
            yield (history, s, f"⏱ Latency: {result['latency']}s",
                   result["tool_calls"], animate_flow(ex03_tools.FLOW_STEPS, 6))
        except Exception as e:
            history = history + [{"role": "user", "content": message},
                                  {"role": "assistant", "content": f"❌ Error: {e}"}]
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
            chatbot   = gr.Chatbot(height=320, label="", show_label=False, type="messages")
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
        history = history + [{"role": "user", "content": message}]
        yield history, s, "⏱ Connecting...", "📦 Chunks: 0", animate_flow(ex06_streaming.FLOW_STEPS, 1)
        time.sleep(0.2)
        yield history, s, "⏱ Streaming...", "📦 Chunks: 0", animate_flow(ex06_streaming.FLOW_STEPS, 2)

        try:
            t0 = time.time()
            accumulated = ""
            chunk_n = 0
            # Stream tokens into the chatbot live
            for chunk in ex06_streaming.run_stream(message, s["history"]):
                accumulated += chunk
                chunk_n += 1
                current_history = history + [{"role": "assistant", "content": accumulated}]
                yield (current_history, s,
                       f"⏱ Streaming... {round(time.time()-t0,1)}s",
                       f"📦 Chunks: {chunk_n}",
                       animate_flow(ex06_streaming.FLOW_STEPS, 3))

            elapsed = round(time.time() - t0, 2)
            s["history"] += [{"role":"user","content":message},
                              {"role":"assistant","content":accumulated}]
            final_history = history + [{"role": "assistant", "content": accumulated}]
            yield (final_history, s,
                   f"⏱ Latency: {elapsed}s",
                   f"📦 Chunks: {chunk_n}",
                   animate_flow(ex06_streaming.FLOW_STEPS, 4))
        except Exception as e:
            err_history = history + [{"role": "assistant", "content": f"❌ Error: {e}"}]
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
            chatbot   = gr.Chatbot(height=300, label="", show_label=False, type="messages")
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
            history = history + [{"role": "user", "content": message},
                                  {"role": "assistant", "content": result["reply"]}]
            sources_md = "**Retrieved:** " + " · ".join(f"`{s}`" for s in result["sources"])
            yield (history, f"⏱ Latency: {result['latency']}s",
                   sources_md, animate_flow(ex08_rag.FLOW_STEPS, 5))
        except Exception as e:
            history = history + [{"role": "user", "content": message},
                                  {"role": "assistant", "content": f"❌ Error: {e}"}]
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
    with gr.Blocks(
        title="AI Agent Learning Platform",
        css=CSS,
        theme=gr.themes.Base(
            primary_hue="blue",
            neutral_hue="slate",
            font=gr.themes.GoogleFont("Inter"),
        ),
    ) as app:

        gr.Markdown("""
# 🤖 AI Agent Learning Platform
### Learn AI Agents from scratch — one concept per tab. Try each agent live.
---
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

        gr.Markdown("""
---
<div style="text-align:center; color: #4a5568; font-size:12px;">
AI Agent Learning Series · 8 exercises from Simple → RAG
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
    )
