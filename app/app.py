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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Fira+Code:wght@400;500&display=swap');

/* ══════════════════════════════════════════════
   TOKEN MAP — DARK (default)
   ══════════════════════════════════════════════ */
:root {
  --bg-base:        #0a0e1a;
  --bg-surface:     #111827;
  --bg-card:        #141d2e;
  --bg-elevated:    #1a2540;
  --bg-input:       #0d1424;
  --border:         #2a3550;
  --border-muted:   #1e2d45;
  --border-active:  #3b82f6;
  --text-primary:   #f0f4ff;
  --text-secondary: #c4cee8;
  --text-muted:     #7888aa;
  --text-faint:     #4a5878;
  --accent-blue:    #60a5fa;
  --accent-green:   #34d399;
  --accent-purple:  #a78bfa;
  --accent-orange:  #fb923c;
  --accent-red:     #f87171;
  --accent-cyan:    #22d3ee;
  --btn-primary:    #2563eb;
  --btn-hover:      #3b82f6;
  --btn-active:     #1d4ed8;
  --user-bubble:    #1e3a6e;
  --user-border:    #3b82f6;
  --bot-bubble:     #141d2e;
  --bot-border:     #2a3550;
  --code-bg:        #0d1424;
  --code-text:      #34d399;
  --glow-blue:      rgba(96,165,250,0.15);
  --glow-green:     rgba(52,211,153,0.12);
  --header-bg:      linear-gradient(135deg, #0a0e1a 0%, #111827 50%, #0e1829 100%);
  --tab-active-bg:  rgba(96,165,250,0.08);
  --shadow-card:    0 4px 24px rgba(0,0,0,0.4);
  --shadow-btn:     0 2px 8px rgba(37,99,235,0.4);
  --radius-sm:      6px;
  --radius-md:      10px;
  --radius-lg:      14px;
  --radius-xl:      20px;
}

/* ── LIGHT THEME ────────────────────────────── */
[data-theme="light"] {
  --bg-base:        #f8fafc;
  --bg-surface:     #ffffff;
  --bg-card:        #ffffff;
  --bg-elevated:    #f1f5f9;
  --bg-input:       #ffffff;
  --border:         #cbd5e1;
  --border-muted:   #e2e8f0;
  --border-active:  #2563eb;
  --text-primary:   #0f172a;
  --text-secondary: #334155;
  --text-muted:     #64748b;
  --text-faint:     #94a3b8;
  --accent-blue:    #2563eb;
  --accent-green:   #059669;
  --accent-purple:  #7c3aed;
  --accent-orange:  #ea580c;
  --accent-red:     #dc2626;
  --accent-cyan:    #0891b2;
  --btn-primary:    #2563eb;
  --btn-hover:      #1d4ed8;
  --btn-active:     #1e40af;
  --user-bubble:    #eff6ff;
  --user-border:    #93c5fd;
  --bot-bubble:     #f8fafc;
  --bot-border:     #e2e8f0;
  --code-bg:        #f1f5f9;
  --code-text:      #059669;
  --glow-blue:      rgba(37,99,235,0.08);
  --glow-green:     rgba(5,150,105,0.08);
  --header-bg:      linear-gradient(135deg, #f0f9ff 0%, #f8fafc 50%, #eff6ff 100%);
  --tab-active-bg:  rgba(37,99,235,0.06);
  --shadow-card:    0 2px 12px rgba(0,0,0,0.08);
  --shadow-btn:     0 2px 8px rgba(37,99,235,0.25);
}

/* ══════════════════════════════════════════════
   RESET & BASE
   ══════════════════════════════════════════════ */
*, *::before, *::after { box-sizing: border-box; }

html, body {
  background: var(--bg-base) !important;
  color: var(--text-primary) !important;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
  font-size: 14px;
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
}

.gradio-container {
  background: var(--bg-base) !important;
  max-width: 100% !important;
  padding: 0 0 48px 0 !important;
}

.main, .wrap, .contain {
  background: var(--bg-base) !important;
}

footer { display: none !important; }

/* ══════════════════════════════════════════════
   HEADER
   ══════════════════════════════════════════════ */
.app-header {
  background: var(--header-bg) !important;
  border-bottom: 1px solid var(--border-muted) !important;
  padding: 0 !important;
  margin-bottom: 0 !important;
}

/* ══════════════════════════════════════════════
   TAB BAR
   ══════════════════════════════════════════════ */
.tabs { background: transparent !important; }

.tab-nav {
  background: var(--bg-surface) !important;
  border-bottom: 1px solid var(--border-muted) !important;
  padding: 0 16px !important;
  gap: 2px !important;
  display: flex !important;
  overflow-x: auto !important;
  scrollbar-width: none !important;
}
.tab-nav::-webkit-scrollbar { display: none !important; }

.tab-nav button {
  font-family: 'Inter', sans-serif !important;
  font-size: 12.5px !important;
  font-weight: 500 !important;
  color: var(--text-muted) !important;
  background: transparent !important;
  border: none !important;
  border-bottom: 2px solid transparent !important;
  padding: 12px 14px !important;
  margin-bottom: -1px !important;
  transition: color 0.15s, border-color 0.15s, background 0.15s !important;
  border-radius: var(--radius-sm) var(--radius-sm) 0 0 !important;
  white-space: nowrap !important;
  cursor: pointer !important;
}
.tab-nav button:hover {
  color: var(--text-secondary) !important;
  background: var(--tab-active-bg) !important;
}
.tab-nav button.selected {
  color: var(--accent-blue) !important;
  border-bottom-color: var(--accent-blue) !important;
  background: var(--tab-active-bg) !important;
  font-weight: 600 !important;
}

/* ══════════════════════════════════════════════
   PANEL CARDS
   ══════════════════════════════════════════════ */
.panel-card {
  background: var(--bg-card) !important;
  border: 1px solid var(--border-muted) !important;
  border-radius: var(--radius-lg) !important;
  padding: 20px 22px !important;
  min-height: 520px !important;
  transition: border-color 0.2s, box-shadow 0.2s !important;
  box-shadow: var(--shadow-card) !important;
}
.panel-card:hover {
  border-color: var(--border) !important;
  box-shadow: var(--shadow-card), 0 0 0 1px var(--border-muted) !important;
}

/* ══════════════════════════════════════════════
   SECTION LABELS (panel headings)
   ══════════════════════════════════════════════ */
.section-label > div > p,
.section-label .prose p {
  font-size: 11px !important;
  font-weight: 700 !important;
  letter-spacing: 1.5px !important;
  text-transform: uppercase !important;
  color: var(--accent-blue) !important;
  margin: 0 0 16px 0 !important;
  padding-bottom: 10px !important;
  border-bottom: 1px solid var(--border-muted) !important;
}

/* ══════════════════════════════════════════════
   LEARN PANEL TYPOGRAPHY
   ══════════════════════════════════════════════ */
.learn-panel .prose {
  font-size: 13.5px !important;
  line-height: 1.8 !important;
  color: var(--text-secondary) !important;
}
.learn-panel .prose h2 {
  color: var(--text-primary) !important;
  font-size: 16px !important;
  font-weight: 700 !important;
  margin: 0 0 12px 0 !important;
  padding-bottom: 10px !important;
  border-bottom: 1px solid var(--border-muted) !important;
}
.learn-panel .prose h3 {
  color: var(--accent-purple) !important;
  font-size: 13px !important;
  font-weight: 600 !important;
  margin: 20px 0 8px 0 !important;
  display: flex !important;
  align-items: center !important;
  gap: 6px !important;
}
.learn-panel .prose h3::before {
  content: '';
  display: inline-block !important;
  width: 3px !important; height: 14px !important;
  background: var(--accent-purple) !important;
  border-radius: 2px !important;
  flex-shrink: 0 !important;
}
.learn-panel .prose p  { color: var(--text-secondary) !important; margin: 8px 0 !important; }
.learn-panel .prose li { color: var(--text-secondary) !important; margin: 4px 0 !important; }
.learn-panel .prose strong { color: var(--text-primary) !important; font-weight: 600 !important; }

.learn-panel .prose code {
  background: var(--code-bg) !important;
  color: var(--accent-orange) !important;
  padding: 2px 7px !important;
  border-radius: 5px !important;
  font-family: 'Fira Code', Consolas, monospace !important;
  font-size: 12px !important;
  border: 1px solid var(--border) !important;
}
.learn-panel .prose pre {
  background: var(--code-bg) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-md) !important;
  padding: 16px 18px !important;
  overflow-x: auto !important;
  margin: 12px 0 !important;
  position: relative !important;
}
.learn-panel .prose pre::before {
  content: 'CODE';
  position: absolute !important;
  top: 8px !important; right: 12px !important;
  font-size: 9px !important; font-weight: 700 !important;
  letter-spacing: 1px !important;
  color: var(--text-faint) !important;
  font-family: 'Inter', sans-serif !important;
}
.learn-panel .prose pre code {
  background: transparent !important;
  color: var(--code-text) !important;
  font-size: 12.5px !important;
  padding: 0 !important;
  border: none !important;
}
.learn-panel .prose table {
  width: 100% !important;
  border-collapse: separate !important;
  border-spacing: 0 !important;
  font-size: 13px !important;
  margin: 14px 0 !important;
  border: 1px solid var(--border-muted) !important;
  border-radius: var(--radius-md) !important;
  overflow: hidden !important;
}
.learn-panel .prose thead tr { background: var(--bg-elevated) !important; }
.learn-panel .prose th {
  color: var(--accent-blue) !important;
  padding: 10px 14px !important;
  text-align: left !important;
  font-weight: 600 !important;
  font-size: 12px !important;
  letter-spacing: 0.3px !important;
  border-bottom: 1px solid var(--border) !important;
}
.learn-panel .prose td {
  color: var(--text-secondary) !important;
  padding: 9px 14px !important;
  border-top: 1px solid var(--border-muted) !important;
}
.learn-panel .prose tr:hover td { background: var(--bg-elevated) !important; }

/* ══════════════════════════════════════════════
   CHATBOT
   ══════════════════════════════════════════════ */
.chatbot,
.chatbot > div,
.chatbot > div > div,
[data-testid="chatbot"],
[data-testid="chatbot"] > div,
.bubble-wrap, .chat-wrap, .messages-wrap,
.svelte-1ed2p3z {
  background: var(--bg-input) !important;
  border: 1px solid var(--border-muted) !important;
  border-radius: var(--radius-md) !important;
}

.chatbot .empty {
  color: var(--text-faint) !important;
  font-size: 13px !important;
}

.chatbot .message {
  background: transparent !important;
  padding: 12px 14px !important;
}

/* User bubble */
.chatbot .user,
.chatbot [data-testid="user"] {
  background: var(--user-bubble) !important;
  color: var(--text-primary) !important;
  border: 1px solid var(--user-border) !important;
  border-radius: 16px 16px 4px 16px !important;
  padding: 10px 15px !important;
  max-width: 82% !important;
  margin-left: auto !important;
  box-shadow: 0 2px 8px rgba(59,130,246,0.15) !important;
}

/* Bot bubble */
.chatbot .bot,
.chatbot [data-testid="bot"] {
  background: var(--bot-bubble) !important;
  color: var(--text-secondary) !important;
  border: 1px solid var(--bot-border) !important;
  border-radius: 16px 16px 16px 4px !important;
  padding: 10px 15px !important;
  max-width: 82% !important;
}

/* ══════════════════════════════════════════════
   INPUTS & TEXTAREAS
   ══════════════════════════════════════════════ */
.gradio-textbox textarea,
.gradio-textbox input,
textarea,
input[type="text"],
input[type="search"] {
  background: var(--bg-input) !important;
  color: var(--text-primary) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-md) !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 14px !important;
  padding: 10px 14px !important;
  transition: border-color 0.15s, box-shadow 0.15s !important;
}
textarea:focus, input:focus {
  border-color: var(--border-active) !important;
  box-shadow: 0 0 0 3px var(--glow-blue) !important;
  outline: none !important;
}
textarea::placeholder, input::placeholder {
  color: var(--text-faint) !important;
}

/* Latency / stat boxes */
.latency-box label span,
.latency-box .label-wrap { display: none !important; }
.latency-box textarea {
  background: var(--bg-elevated) !important;
  color: var(--accent-green) !important;
  border: 1px solid var(--border-muted) !important;
  border-radius: var(--radius-md) !important;
  font-size: 12px !important;
  font-weight: 600 !important;
  text-align: center !important;
  padding: 6px 12px !important;
}

/* ══════════════════════════════════════════════
   BUTTONS
   ══════════════════════════════════════════════ */
button.primary,
.send-btn {
  background: linear-gradient(135deg, var(--btn-primary), #1d4ed8) !important;
  color: #ffffff !important;
  border: none !important;
  border-radius: var(--radius-md) !important;
  font-family: 'Inter', sans-serif !important;
  font-weight: 600 !important;
  font-size: 13.5px !important;
  padding: 9px 24px !important;
  transition: all 0.15s !important;
  cursor: pointer !important;
  box-shadow: var(--shadow-btn) !important;
  letter-spacing: 0.2px !important;
}
button.primary:hover,
.send-btn:hover {
  background: linear-gradient(135deg, var(--btn-hover), var(--btn-primary)) !important;
  box-shadow: 0 4px 16px rgba(37,99,235,0.5) !important;
  transform: translateY(-1px) !important;
}
button.primary:active { transform: scale(0.97) !important; }

button.secondary {
  background: var(--bg-elevated) !important;
  color: var(--text-muted) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-md) !important;
  font-size: 13px !important;
  font-weight: 500 !important;
  transition: all 0.15s !important;
  padding: 9px 20px !important;
}
button.secondary:hover {
  background: var(--bg-input) !important;
  color: var(--text-primary) !important;
  border-color: var(--border-active) !important;
}

/* ══════════════════════════════════════════════
   HOW IT WORKS — FLOW BOX
   ══════════════════════════════════════════════ */
.flow-box,
.flow-box > div {
  background: var(--bg-input) !important;
  border: 1px solid var(--border-muted) !important;
  border-radius: var(--radius-md) !important;
  padding: 14px !important;
}
.flow-box .prose {
  font-family: 'Fira Code', Consolas, monospace !important;
  font-size: 12px !important;
  line-height: 2 !important;
}
.flow-box .prose p   { color: var(--text-muted) !important; margin: 3px 0 !important; }
.flow-box .prose code,
.flow-box .prose pre {
  background: var(--bg-card) !important;
  color: var(--code-text) !important;
  border: 1px solid var(--border-muted) !important;
  border-radius: var(--radius-sm) !important;
  font-size: 12px !important;
  padding: 2px 8px !important;
}
.flow-box .prose strong { color: var(--accent-orange) !important; font-weight: 700 !important; }
.flow-box .prose em     { color: var(--accent-cyan) !important; font-style: normal !important; }
.flow-box .prose del    { color: var(--text-faint) !important; text-decoration: line-through !important; }
.flow-box .prose hr     { border-color: var(--border-muted) !important; margin: 10px 0 !important; }

/* ══════════════════════════════════════════════
   ACCORDION
   ══════════════════════════════════════════════ */
details, .accordion {
  background: var(--bg-elevated) !important;
  border: 1px solid var(--border-muted) !important;
  border-radius: var(--radius-md) !important;
  overflow: hidden !important;
}
details summary, .accordion summary {
  color: var(--text-muted) !important;
  font-size: 13px !important;
  font-weight: 500 !important;
  padding: 10px 14px !important;
  cursor: pointer !important;
  transition: color 0.15s, background 0.15s !important;
}
details summary:hover {
  color: var(--text-primary) !important;
  background: var(--bg-card) !important;
}

/* ══════════════════════════════════════════════
   JSON VIEWER
   ══════════════════════════════════════════════ */
.json-holder,
.json-holder * {
  background: var(--code-bg) !important;
  color: var(--code-text) !important;
  border-radius: var(--radius-md) !important;
  font-size: 12px !important;
  font-family: 'Fira Code', monospace !important;
}

/* ══════════════════════════════════════════════
   THEME RADIO SWITCHER
   ══════════════════════════════════════════════ */
.theme-radio {
  background: transparent !important;
  border: none !important;
  padding: 0 !important;
}
.theme-radio > div > div { gap: 0 !important; }
.theme-radio .wrap,
.theme-radio > div > div > div {
  gap: 4px !important;
  flex-wrap: nowrap !important;
  display: flex !important;
  align-items: center !important;
}
.theme-radio label {
  background: var(--bg-elevated) !important;
  color: var(--text-muted) !important;
  border: 1px solid var(--border-muted) !important;
  border-radius: var(--radius-xl) !important;
  font-size: 12px !important;
  font-weight: 500 !important;
  padding: 5px 14px !important;
  cursor: pointer !important;
  transition: all 0.15s !important;
  white-space: nowrap !important;
}
.theme-radio label:hover {
  background: var(--bg-card) !important;
  color: var(--text-secondary) !important;
  border-color: var(--border) !important;
}
.theme-radio label:has(input:checked),
.theme-radio label.selected {
  background: var(--btn-primary) !important;
  color: #ffffff !important;
  border-color: var(--btn-primary) !important;
  font-weight: 600 !important;
  box-shadow: 0 2px 8px var(--glow-blue) !important;
}
.theme-radio input[type="radio"] { display: none !important; }
.theme-radio .label-wrap,
.theme-radio > label > span:first-child { display: none !important; }

/* ══════════════════════════════════════════════
   SCROLLBARS
   ══════════════════════════════════════════════ */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-faint); }

/* ══════════════════════════════════════════════
   RESPONSIVE — narrow viewports
   ══════════════════════════════════════════════ */
@media (max-width: 900px) {
  .gradio-container { padding: 0 0 32px 0 !important; }
  .panel-card { min-height: 300px !important; padding: 14px 16px !important; }
  .tab-nav button { padding: 10px 10px !important; font-size: 11.5px !important; }
}
@media (max-width: 600px) {
  .tab-nav button { padding: 8px 8px !important; font-size: 11px !important; }
}

/* ══════════════════════════════════════════════
   TAB CONTENT AREA PADDING
   ══════════════════════════════════════════════ */
.tabitem { padding: 16px 16px 0 16px !important; }
.gap { gap: 14px !important; }
"""

# JS that runs once on page load — applies saved theme and wires the Radio change
THEME_JS = """
function setTheme(t) {
  var resolved = t === 'system'
    ? (window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark')
    : t;
  document.documentElement.setAttribute('data-theme', resolved);
  localStorage.setItem('ai-agent-theme-key', t);
  ['dark','light','system'].forEach(function(k) {
    var b = document.getElementById('btn-theme-' + k);
    if (!b) return;
    if (k === t) {
      b.style.background = '#2563eb';
      b.style.color = '#fff';
      b.style.borderColor = '#2563eb';
      b.style.boxShadow = '0 2px 8px rgba(37,99,235,0.5)';
    } else {
      b.style.background = '';
      b.style.color = '';
      b.style.borderColor = '';
      b.style.boxShadow = '';
    }
  });
}

// Wire clicks via event delegation — works even after Gradio re-renders
document.addEventListener('click', function(e) {
  var t = e.target.closest('[data-theme-set]');
  if (t) setTheme(t.getAttribute('data-theme-set'));
});

// Restore saved theme on page load
var _saved = localStorage.getItem('ai-agent-theme-key') || 'dark';
setTheme(_saved);
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
        gr.HTML("""
<div style="
  background: var(--header-bg);
  border-bottom: 1px solid var(--border-muted);
  padding: 18px 28px 16px 28px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
">
  <!-- Left: branding -->
  <div style="display:flex; align-items:center; gap:14px; flex:1; min-width:220px;">
    <div style="
      width:46px; height:46px; border-radius:13px; flex-shrink:0;
      background: linear-gradient(135deg,#2563eb,#7c3aed);
      display:flex; align-items:center; justify-content:center;
      font-size:24px; box-shadow:0 4px 16px rgba(37,99,235,0.4);
    ">🤖</div>
    <div>
      <h1 style="margin:0; font-size:19px; font-weight:700; color:var(--text-primary); letter-spacing:-0.4px; line-height:1.2;">
        AI Agent Learning Platform
      </h1>
      <p style="margin:3px 0 0 0; font-size:12px; color:var(--text-muted); line-height:1.4;">
        Learn AI Agents from scratch &nbsp;·&nbsp; One concept per tab &nbsp;·&nbsp; Live chat &nbsp;·&nbsp; Animated flows
      </p>
    </div>
  </div>

  <!-- Right: badges + theme switcher stacked -->
  <div style="display:flex; flex-direction:column; align-items:flex-end; gap:10px;">

    <!-- Badges row -->
    <div style="display:flex; gap:6px; flex-wrap:wrap; justify-content:flex-end;">
      <span style="background:rgba(96,165,250,0.1); color:var(--accent-blue); border:1px solid rgba(96,165,250,0.25); border-radius:20px; padding:3px 11px; font-size:11px; font-weight:600; white-space:nowrap;">📚 8 Exercises</span>
      <span style="background:rgba(52,211,153,0.1); color:var(--accent-green); border:1px solid rgba(52,211,153,0.25); border-radius:20px; padding:3px 11px; font-size:11px; font-weight:600; white-space:nowrap;">🚀 Simple → RAG</span>
      <span style="background:rgba(167,139,250,0.1); color:var(--accent-purple); border:1px solid rgba(167,139,250,0.25); border-radius:20px; padding:3px 11px; font-size:11px; font-weight:600; white-space:nowrap;">⚡ Live Chat</span>
      <span style="background:rgba(251,146,60,0.1); color:var(--accent-orange); border:1px solid rgba(251,146,60,0.25); border-radius:20px; padding:3px 11px; font-size:11px; font-weight:600; white-space:nowrap;">🔄 Flows</span>
    </div>

    <!-- Theme switcher — data-theme-set picked up by event delegation in THEME_JS -->
    <div style="display:flex; align-items:center; gap:6px;">
      <span style="font-size:11px; color:var(--text-faint); font-weight:500; margin-right:2px; white-space:nowrap; user-select:none;">Theme</span>
      <button id="btn-theme-dark"   data-theme-set="dark"   style="cursor:pointer; border:1px solid #2563eb; border-radius:20px; padding:5px 14px; font-size:12px; font-weight:500; background:#2563eb; color:#fff; transition:all 0.15s;">🌙 Dark</button>
      <button id="btn-theme-light"  data-theme-set="light"  style="cursor:pointer; border:1px solid #2a3550; border-radius:20px; padding:5px 14px; font-size:12px; font-weight:500; background:#1a2540; color:#7888aa; transition:all 0.15s;">☀️ Light</button>
      <button id="btn-theme-system" data-theme-set="system" style="cursor:pointer; border:1px solid #2a3550; border-radius:20px; padding:5px 14px; font-size:12px; font-weight:500; background:#1a2540; color:#7888aa; transition:all 0.15s;">💻 System</button>
    </div>

  </div>
</div>
""")
        # Hidden radio — kept for the theme_radio.change() wiring below
        with gr.Row(visible=False):
            theme_radio = gr.Radio(
                choices=["🌙 Dark", "☀️ Light", "💻 System"],
                value="🌙 Dark",
                label="",
                interactive=True,
                elem_classes="theme-radio",
            )

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
