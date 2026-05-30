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
/* ══════════════════════════════════════════════
   CSS CUSTOM PROPERTIES — DARK THEME (default)
   ══════════════════════════════════════════════ */
:root {
  --bg-base:       #0d1117;
  --bg-surface:    #161b22;
  --bg-elevated:   #1c2128;
  --bg-overlay:    #1f2937;
  --border:        #30363d;
  --border-muted:  #21262d;
  --text-primary:  #e6edf3;
  --text-secondary:#c9d1d9;
  --text-muted:    #8b949e;
  --text-faint:    #6e7681;
  --accent-blue:   #58a6ff;
  --accent-green:  #3fb950;
  --accent-purple: #bc8cff;
  --accent-orange: #ffa657;
  --accent-red:    #f85149;
  --btn-primary:   #1f6feb;
  --btn-hover:     #388bfd;
  --user-bubble:   #1c3a5e;
  --bot-bubble:    #161b22;
  --code-bg:       #161b22;
  --code-text:     #7ee787;
}

/* ── LIGHT THEME ────────────────────────────── */
[data-theme="light"] {
  --bg-base:       #ffffff;
  --bg-surface:    #f6f8fa;
  --bg-elevated:   #eaeef2;
  --bg-overlay:    #e1e4e8;
  --border:        #d0d7de;
  --border-muted:  #e1e4e8;
  --text-primary:  #1f2328;
  --text-secondary:#24292f;
  --text-muted:    #57606a;
  --text-faint:    #8c959f;
  --accent-blue:   #0969da;
  --accent-green:  #1a7f37;
  --accent-purple: #8250df;
  --accent-orange: #bc4c00;
  --accent-red:    #cf222e;
  --btn-primary:   #0969da;
  --btn-hover:     #0550ae;
  --user-bubble:   #ddf4ff;
  --bot-bubble:    #f6f8fa;
  --code-bg:       #f6f8fa;
  --code-text:     #1a7f37;
}

/* ── BASE ───────────────────────────────────── */
html, body, .gradio-container, .main, .wrap {
  background: var(--bg-base) !important;
  color: var(--text-primary) !important;
  font-family: -apple-system, 'Inter', BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
}
.gradio-container { max-width: 100% !important; padding: 0 20px 40px !important; }
footer { background: var(--bg-base) !important; }

/* hide Gradio's own footer links */
footer a, .built-with { display: none !important; }

/* ── TABS ───────────────────────────────────── */
.tab-nav {
  border-bottom: 1px solid var(--border-muted) !important;
  background: transparent !important;
  gap: 0 !important;
}
.tab-nav button {
  font-size: 13px !important; font-weight: 500 !important;
  color: var(--text-muted) !important; background: transparent !important;
  border: none !important; border-bottom: 2px solid transparent !important;
  padding: 10px 16px !important; transition: all 0.15s !important;
  border-radius: 0 !important;
}
.tab-nav button:hover { color: var(--text-secondary) !important; background: var(--bg-elevated) !important; }
.tab-nav button.selected {
  color: var(--accent-blue) !important;
  border-bottom: 2px solid var(--accent-blue) !important;
  font-weight: 600 !important;
}

/* ── PANEL CARDS ────────────────────────────── */
.panel-card {
  background: var(--bg-surface) !important;
  border: 1px solid var(--border-muted) !important;
  border-radius: 12px !important;
  padding: 20px !important;
  min-height: 500px !important;
}
.panel-card:hover { border-color: var(--border) !important; }

/* ── SECTION LABELS ─────────────────────────── */
.section-label p, .section-label .prose p {
  font-size: 10px !important; font-weight: 700 !important;
  letter-spacing: 2px !important; text-transform: uppercase !important;
  color: var(--accent-blue) !important; margin: 0 0 14px 0 !important;
  display: flex !important; align-items: center !important; gap: 6px !important;
}

/* ── LEARN PANEL ────────────────────────────── */
.learn-panel .prose { font-size: 13.5px !important; line-height: 1.75 !important; }
.learn-panel .prose h2 {
  color: var(--text-primary) !important; font-size: 15px !important;
  font-weight: 700 !important; margin: 0 0 6px 0 !important;
  padding-bottom: 8px !important; border-bottom: 1px solid var(--border-muted) !important;
}
.learn-panel .prose h3 {
  color: var(--accent-purple) !important; font-size: 13px !important;
  font-weight: 600 !important; margin: 16px 0 6px 0 !important;
}
.learn-panel .prose p { color: var(--text-secondary) !important; margin: 6px 0 !important; }
.learn-panel .prose li { color: var(--text-secondary) !important; }
.learn-panel .prose strong { color: var(--text-primary) !important; font-weight: 600 !important; }

/* inline code */
.learn-panel .prose code {
  background: var(--code-bg) !important; color: var(--accent-orange) !important;
  padding: 1px 6px !important; border-radius: 4px !important;
  font-family: 'Fira Code', 'Cascadia Code', Consolas, monospace !important;
  font-size: 12px !important; border: 1px solid var(--border-muted) !important;
}
/* fenced code blocks */
.learn-panel .prose pre {
  background: var(--bg-base) !important; border: 1px solid var(--border) !important;
  border-radius: 8px !important; padding: 14px 16px !important; overflow-x: auto !important;
  margin: 10px 0 !important;
}
.learn-panel .prose pre code {
  background: transparent !important; color: var(--code-text) !important;
  font-size: 12px !important; padding: 0 !important; border: none !important;
}
/* tables */
.learn-panel .prose table { width: 100% !important; border-collapse: collapse !important; font-size: 13px !important; margin: 10px 0 !important; }
.learn-panel .prose thead tr { background: var(--bg-elevated) !important; }
.learn-panel .prose th {
  color: var(--accent-blue) !important; padding: 8px 12px !important;
  text-align: left !important; font-weight: 600 !important;
  border-bottom: 1px solid var(--border) !important;
}
.learn-panel .prose td {
  color: var(--text-secondary) !important; padding: 7px 12px !important;
  border-top: 1px solid var(--border-muted) !important;
}
.learn-panel .prose tr:hover td { background: var(--bg-elevated) !important; }

/* ── CHATBOT ─────────────────────────────────── */
/* outer wrapper — kill the white */
.chatbot, .chatbot > div, .chatbot > div > div,
[data-testid="chatbot"], [data-testid="chatbot"] > div,
.bubble-wrap, .chat-wrap, .messages-wrap {
  background: var(--bg-base) !important;
  border: 1px solid var(--border-muted) !important;
  border-radius: 10px !important;
}
/* empty state text */
.chatbot .empty { color: var(--text-faint) !important; }
/* message rows */
.chatbot .message { background: transparent !important; }
/* user bubble */
.chatbot .user, .chatbot .human,
.chatbot [data-testid="user"],
.chatbot .message-wrap > div:first-child {
  background: var(--user-bubble) !important;
  color: var(--text-primary) !important;
  border-radius: 16px 16px 4px 16px !important;
  border: 1px solid var(--accent-blue) !important;
  padding: 10px 14px !important; max-width: 85% !important;
  margin-left: auto !important;
}
/* bot bubble */
.chatbot .bot, .chatbot .assistant,
.chatbot [data-testid="bot"],
.chatbot .message-wrap > div:last-child {
  background: var(--bot-bubble) !important;
  color: var(--text-secondary) !important;
  border-radius: 16px 16px 16px 4px !important;
  border: 1px solid var(--border) !important;
  padding: 10px 14px !important; max-width: 85% !important;
}

/* ── INPUTS ──────────────────────────────────── */
.gradio-textbox textarea, .gradio-textbox input,
textarea, input[type="text"], input[type="search"] {
  background: var(--bg-surface) !important;
  color: var(--text-primary) !important;
  border: 1px solid var(--border) !important;
  border-radius: 8px !important; font-size: 14px !important;
  transition: border-color 0.15s, box-shadow 0.15s !important;
}
textarea:focus, input:focus {
  border-color: var(--accent-blue) !important;
  box-shadow: 0 0 0 3px rgba(88,166,255,0.12) !important;
  outline: none !important;
}
textarea::placeholder, input::placeholder { color: var(--text-faint) !important; }

/* hide "Textbox" label on latency boxes */
.latency-box label span, .latency-box .label-wrap { display: none !important; }
.latency-box textarea {
  background: var(--bg-base) !important;
  color: var(--accent-green) !important;
  border: 1px solid var(--border-muted) !important;
  border-radius: 8px !important; font-size: 12px !important;
  font-weight: 600 !important; text-align: center !important;
  padding: 6px !important;
}

/* ── BUTTONS ─────────────────────────────────── */
button.primary, .send-btn {
  background: var(--btn-primary) !important; color: #fff !important;
  border: none !important; border-radius: 8px !important;
  font-weight: 600 !important; font-size: 13px !important;
  padding: 8px 22px !important; transition: background 0.15s, transform 0.1s !important;
  cursor: pointer !important;
}
button.primary:hover  { background: var(--btn-hover) !important; }
button.primary:active { transform: scale(0.97) !important; }
button.secondary {
  background: var(--bg-elevated) !important; color: var(--text-muted) !important;
  border: 1px solid var(--border) !important; border-radius: 8px !important;
  font-size: 13px !important; transition: all 0.15s !important;
}
button.secondary:hover { background: var(--bg-overlay) !important; color: var(--text-primary) !important; }

/* Theme toggle buttons */
.theme-btn {
  background: var(--bg-elevated) !important; color: var(--text-muted) !important;
  border: 1px solid var(--border-muted) !important; border-radius: 20px !important;
  font-size: 12px !important; font-weight: 500 !important;
  padding: 4px 14px !important; cursor: pointer !important;
  transition: all 0.15s !important;
}
.theme-btn:hover, .theme-btn.active {
  background: var(--accent-blue) !important; color: #fff !important;
  border-color: var(--accent-blue) !important;
}

/* ── HOW IT WORKS — FLOW BOX ─────────────────── */
.flow-box, .flow-box > div { background: var(--bg-base) !important; }
.flow-box .prose {
  font-family: 'Fira Code', 'Cascadia Code', Consolas, monospace !important;
  font-size: 12px !important; line-height: 1.8 !important;
}
.flow-box .prose p   { color: var(--text-muted) !important; margin: 4px 0 !important; }
.flow-box .prose code, .flow-box .prose pre {
  background: var(--bg-base) !important; color: var(--code-text) !important;
  border: 1px solid var(--border-muted) !important; border-radius: 6px !important;
  font-size: 12px !important;
}
.flow-box .prose strong { color: var(--accent-orange) !important; }
.flow-box .prose em     { color: var(--accent-purple) !important; font-style: normal !important; }
.flow-box .prose del    { color: var(--text-faint) !important; }
.flow-box .prose hr     { border-color: var(--border-muted) !important; margin: 8px 0 !important; }

/* ── ACCORDION ───────────────────────────────── */
details, .accordion {
  background: var(--bg-surface) !important;
  border: 1px solid var(--border-muted) !important;
  border-radius: 8px !important;
}
details summary, .accordion summary {
  color: var(--text-muted) !important; font-size: 13px !important;
  padding: 8px 12px !important; cursor: pointer !important;
}
details summary:hover { color: var(--text-primary) !important; }

/* ── JSON VIEWER ─────────────────────────────── */
.json-holder, .json-holder * {
  background: var(--bg-base) !important; color: var(--code-text) !important;
  border-radius: 8px !important; font-size: 12px !important;
}

/* ── SCROLLBARS ──────────────────────────────── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-faint); }

/* ── THEME RADIO SWITCHER ────────────────────── */
.theme-radio { background: transparent !important; border: none !important; padding: 0 !important; }
.theme-radio .wrap { gap: 4px !important; flex-wrap: nowrap !important; }
.theme-radio label {
  background: var(--bg-elevated) !important; color: var(--text-muted) !important;
  border: 1px solid var(--border-muted) !important; border-radius: 20px !important;
  font-size: 12px !important; font-weight: 500 !important;
  padding: 4px 14px !important; cursor: pointer !important;
  transition: all 0.15s !important; white-space: nowrap !important;
}
.theme-radio label:has(input:checked),
.theme-radio label.selected {
  background: var(--accent-blue) !important; color: #fff !important;
  border-color: var(--accent-blue) !important; font-weight: 600 !important;
}
.theme-radio input[type="radio"] { display: none !important; }
"""

# JS that runs once on page load — applies saved theme and wires the Radio change
THEME_JS = """
function applyTheme(theme) {
  const resolved = (theme === '💻 System')
    ? (window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark')
    : (theme === '☀️ Light' ? 'light' : 'dark');
  document.documentElement.setAttribute('data-theme', resolved);
  localStorage.setItem('ai-agent-theme', theme);
}

// Restore on load
const saved = localStorage.getItem('ai-agent-theme') || '🌙 Dark';
applyTheme(saved);
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

            history = history + [{"role": "user", "content": message}, {"role": "assistant", "content": result["reply"]}]
            yield (history, s, f"⏱ Latency: {result['latency']}s",
                   {"request": result["request"], "response": result["response"]},
                   animate_flow(ex01_simple.FLOW_STEPS, 5))
        except Exception as e:
            history = history + [{"role": "user", "content": message}, {"role": "assistant", "content": f"❌ Error: {e}"}]
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

            history = history + [{"role": "user", "content": message}, {"role": "assistant", "content": result["reply"]}]
            yield (history, s, f"⏱ Latency: {result['latency']}s",
                   f"💬 Turns: {len(s['history'])//2}",
                   animate_flow(ex02_memory.FLOW_STEPS, 5))
        except Exception as e:
            history = history + [{"role": "user", "content": message}, {"role": "assistant", "content": f"❌ Error: {e}"}]
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

            history = history + [{"role": "user", "content": message}, {"role": "assistant", "content": result["reply"]}]
            yield (history, s, f"⏱ Latency: {result['latency']}s",
                   result["tool_calls"], animate_flow(ex03_tools.FLOW_STEPS, 6))
        except Exception as e:
            history = history + [{"role": "user", "content": message}, {"role": "assistant", "content": f"❌ Error: {e}"}]
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
            # Stream tokens — build history with dict format Gradio 6 expects
            for chunk in ex06_streaming.run_stream(message, s["history"]):
                accumulated += chunk
                chunk_n += 1
                current_history = history + [
                    {"role": "user",      "content": message},
                    {"role": "assistant", "content": accumulated},
                ]
                yield (current_history, s,
                       f"⏱ Streaming... {round(time.time()-t0,1)}s",
                       f"📦 Chunks: {chunk_n}",
                       animate_flow(ex06_streaming.FLOW_STEPS, 3))

            elapsed = round(time.time() - t0, 2)
            s["history"] += [{"role":"user","content":message},
                              {"role":"assistant","content":accumulated}]
            final_history = history + [
                {"role": "user",      "content": message},
                {"role": "assistant", "content": accumulated},
            ]
            yield (final_history, s,
                   f"⏱ Latency: {elapsed}s",
                   f"📦 Chunks: {chunk_n}",
                   animate_flow(ex06_streaming.FLOW_STEPS, 4))
        except Exception as e:
            err_history = history + [{"role": "user", "content": message}, {"role": "assistant", "content": f"❌ Error: {e}"}]
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
            history = history + [{"role": "user", "content": message}, {"role": "assistant", "content": result["reply"]}]
            sources_md = "**Retrieved:** " + " · ".join(f"`{s}`" for s in result["sources"])
            yield (history, f"⏱ Latency: {result['latency']}s",
                   sources_md, animate_flow(ex08_rag.FLOW_STEPS, 5))
        except Exception as e:
            history = history + [{"role": "user", "content": message}, {"role": "assistant", "content": f"❌ Error: {e}"}]
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
        js=f"() => {{ {THEME_JS} }}",  # runs on page load to restore saved theme
    ) as app:

        # ── Header ──
        with gr.Row(elem_classes="header-row"):
            with gr.Column(scale=8):
                gr.HTML("""
<div style="padding:18px 0 10px 0;">
  <div style="display:flex; align-items:center; gap:14px;">
    <span style="font-size:38px; line-height:1;">🤖</span>
    <div>
      <h1 style="margin:0; font-size:22px; font-weight:700; color:var(--text-primary); letter-spacing:-0.3px;">
        AI Agent Learning Platform
      </h1>
      <p style="margin:4px 0 0 0; font-size:13px; color:var(--text-muted);">
        Learn AI Agents from scratch &nbsp;·&nbsp; One concept per tab &nbsp;·&nbsp; Live chat &nbsp;·&nbsp; Animated flows
      </p>
    </div>
  </div>
  <div style="display:flex; gap:8px; margin-top:12px; flex-wrap:wrap;">
    <span style="background:var(--bg-elevated); color:var(--accent-blue);   border:1px solid var(--border-muted); border-radius:20px; padding:3px 12px; font-size:11px; font-weight:600;">📚 8 Exercises</span>
    <span style="background:var(--bg-elevated); color:var(--accent-green);  border:1px solid var(--border-muted); border-radius:20px; padding:3px 12px; font-size:11px; font-weight:600;">🚀 Simple → RAG</span>
    <span style="background:var(--bg-elevated); color:var(--accent-purple); border:1px solid var(--border-muted); border-radius:20px; padding:3px 12px; font-size:11px; font-weight:600;">⚡ Live Chat</span>
    <span style="background:var(--bg-elevated); color:var(--accent-orange); border:1px solid var(--border-muted); border-radius:20px; padding:3px 12px; font-size:11px; font-weight:600;">🔄 Animated Flows</span>
  </div>
</div>
""")
            with gr.Column(scale=2, min_width=220):
                theme_radio = gr.Radio(
                    choices=["🌙 Dark", "☀️ Light", "💻 System"],
                    value="🌙 Dark",
                    label="Theme",
                    interactive=True,
                    elem_classes="theme-radio",
                )

        gr.HTML('<div style="border-bottom:1px solid var(--border-muted); margin: 0 0 8px 0;"></div>')

        # ── Exercise Tabs ──
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
<div style="text-align:center; color:var(--text-faint); font-size:12px; padding:20px 0 8px 0; border-top:1px solid var(--border-muted); margin-top:16px;">
  AI Agent Learning Series &nbsp;·&nbsp; Simple → Memory → Tools → ReAct → Multi-Agent → Streaming → Structured → RAG &nbsp;·&nbsp;
  <a href="https://github.com/skalmodiya/ai-agent-learning" style="color:var(--accent-blue); text-decoration:none; font-weight:600;">GitHub ↗</a>
</div>
""")

        # ── Theme switcher logic ──
        # When the Radio changes, run JS to update data-theme on <html>
        theme_radio.change(
            fn=None,
            inputs=theme_radio,
            js="""(theme) => {
                const resolved = (theme === '💻 System')
                    ? (window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark')
                    : (theme === '☀️ Light' ? 'light' : 'dark');
                document.documentElement.setAttribute('data-theme', resolved);
                localStorage.setItem('ai-agent-theme', theme);
            }""",
        )

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
