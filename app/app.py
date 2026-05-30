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
import sqlite3

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
from exercises import config as ex_config

# ─────────────────────────────────────────────
# SQLITE — persist API key across restarts
# ─────────────────────────────────────────────

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.db")

def _db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)"
    )
    conn.commit()
    return conn

def db_get(key: str, default: str = "") -> str:
    try:
        with _db() as conn:
            row = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
            return row[0] if row else default
    except Exception:
        return default

def db_set(key: str, value: str) -> None:
    try:
        with _db() as conn:
            conn.execute(
                "INSERT INTO settings(key,value) VALUES(?,?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (key, value),
            )
    except Exception:
        pass

# ─────────────────────────────────────────────
# THEME & CSS
# ─────────────────────────────────────────────

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Fira+Code:wght@400;500&display=swap');

/* ══════════════════════════════════════════════
   TOKEN MAP — DARK (default)
   ══════════════════════════════════════════════ */
:root {
  --bg-base:        #0d1117;
  --bg-surface:     #161b22;
  --bg-card:        #1c2333;
  --bg-elevated:    #21293a;
  --bg-input:       #10161f;
  --border:         #30404f;
  --border-muted:   #243042;
  --border-active:  #4d90fe;
  --text-primary:   #f0f6fc;
  --text-secondary: #cdd9e5;
  --text-muted:     #a0b3c8;
  --text-faint:     #6b8099;
  --accent-blue:    #79b8ff;
  --accent-green:   #56d364;
  --accent-purple:  #d2a8ff;
  --accent-orange:  #ffa657;
  --accent-red:     #ff7b72;
  --accent-cyan:    #39c5cf;
  --btn-primary:    #1f6feb;
  --btn-hover:      #388bfd;
  --user-bubble:    #1c3d6e;
  --user-border:    #4d90fe;
  --bot-bubble:     #1c2333;
  --bot-border:     #30404f;
  --code-bg:        #161b22;
  --code-text:      #79c0ff;
  --glow-blue:      rgba(79,140,255,0.18);
  --header-bg:      linear-gradient(135deg,#0d1117 0%,#161b22 60%,#0e1620 100%);
  --tab-active-bg:  rgba(121,184,255,0.07);
  --shadow-card:    0 4px 20px rgba(0,0,0,0.6);
  --shadow-btn:     0 2px 8px rgba(31,111,235,0.4);
  --radius-sm:      6px;
  --radius-md:      10px;
  --radius-lg:      14px;
  --radius-xl:      20px;
}

/* ── Gradio internal CSS vars — DARK (maps Gradio's Svelte vars to our tokens) ── */
/* Gradio dropdown/select/input Svelte components read THESE vars, not ours.      */
/* Without overriding them the popup always renders with Gradio's white defaults. */
:root {
  --background-fill-primary:      #1c2333;
  --background-fill-secondary:    #21293a;
  --body-text-color:               #f0f6fc;
  --body-text-color-subdued:       #a0b3c8;
  --input-background-fill:         #10161f;
  --border-color-primary:          #30404f;
  --input-border-color-focus:      #4d90fe;
  --color-accent:                  #79b8ff;
  /* User message bubble — Gradio uses --color-accent-soft as bg */
  --color-accent-soft:             #1c3d6e;
  --border-color-accent-subdued:   #2d5a9e;
  --border-color-accent:           #4d90fe;
  --shadow-drop:                   0 4px 20px rgba(0,0,0,0.6);
  --block-background-fill:         #1c2333;
  --block-border-color:            #30404f;
  --block-label-text-color:        #a0b3c8;
  --panel-background-fill:         #161b22;
  --checkbox-background-color:     #10161f;
}

/* ── LIGHT THEME ────────────────────────────── */
[data-theme="light"] {
  --bg-base:        #f6f8fa;
  --bg-surface:     #ffffff;
  --bg-card:        #ffffff;
  --bg-elevated:    #eaeef2;
  --bg-input:       #ffffff;
  --border:         #d0d7de;
  --border-muted:   #e1e4e8;
  --border-active:  #0969da;
  --text-primary:   #1f2328;
  --text-secondary: #24292f;
  --text-muted:     #57606a;
  --text-faint:     #6e7781;
  --accent-blue:    #0550ae;
  --accent-green:   #116329;
  --accent-purple:  #6e40c9;
  --accent-orange:  #953800;
  --accent-red:     #82071e;
  --accent-cyan:    #065f73;
  --btn-primary:    #0969da;
  --btn-hover:      #0550ae;
  --user-bubble:    #ddf4ff;
  --user-border:    #54aeff;
  --bot-bubble:     #f6f8fa;
  --bot-border:     #d0d7de;
  --code-bg:        #eaeef2;
  --code-text:      #0550ae;
  --glow-blue:      rgba(9,105,218,0.12);
  --header-bg:      linear-gradient(135deg,#f0f6ff 0%,#ffffff 60%,#f6f0ff 100%);
  --tab-active-bg:  rgba(9,105,218,0.06);
  --shadow-card:    0 2px 10px rgba(0,0,0,0.08);
  --shadow-btn:     0 2px 6px rgba(9,105,218,0.25);
  /* Gradio internal vars — light overrides */
  --background-fill-primary:      #ffffff;
  --background-fill-secondary:    #eaeef2;
  --body-text-color:               #1f2328;
  --body-text-color-subdued:       #57606a;
  --input-background-fill:         #ffffff;
  --border-color-primary:          #d0d7de;
  --input-border-color-focus:      #0969da;
  --color-accent:                  #0550ae;
  --color-accent-soft:             #ddf4ff;
  --border-color-accent-subdued:   #54aeff;
  --border-color-accent:           #0969da;
  --shadow-drop:                   0 2px 10px rgba(0,0,0,0.12);
  --block-background-fill:         #ffffff;
  --block-border-color:            #d0d7de;
  --block-label-text-color:        #57606a;
  --panel-background-fill:         #f6f8fa;
  --checkbox-background-color:     #ffffff;
}

/* ══════════════════════════════════════════════
   RESET & BASE
   ══════════════════════════════════════════════ */
*, *::before, *::after { box-sizing: border-box; }

html, body {
  background: var(--bg-base) !important;
  color: var(--text-primary) !important;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
  -webkit-font-smoothing: antialiased;
}

.gradio-container {
  background: var(--bg-base) !important;
  max-width: 100% !important;
  padding: 0 0 48px 0 !important;
  color: var(--text-primary) !important;
}

.main, .wrap, .contain, .app, .block, .form, .gap {
  background: transparent !important;
  color: var(--text-primary) !important;
}

footer { display: none !important; }

/* Global text colour fallback */
p, span, li, td, th, label, div, h1, h2, h3, h4 {
  color: var(--text-primary);
}

/* ══════════════════════════════════════════════
   TAB BAR
   ══════════════════════════════════════════════ */
.tabs { background: transparent !important; }

.tab-nav {
  background: var(--bg-surface) !important;
  border-bottom: 1px solid var(--border-muted) !important;
  padding: 0 16px !important;
  display: flex !important;
  overflow-x: auto !important;
  scrollbar-width: none !important;
}
.tab-nav::-webkit-scrollbar { display: none !important; }

.tab-nav button {
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
  min-height: 600px !important;
  height: 100% !important;
  box-shadow: var(--shadow-card) !important;
  color: var(--text-primary) !important;
  overflow-y: auto !important;
}
.panel-card:hover { border-color: var(--border) !important; }

/* ══════════════════════════════════════════════
   SECTION LABELS
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
   LEARN PANEL
   ══════════════════════════════════════════════ */
.learn-panel .prose,
.learn-panel .prose * { color: var(--text-secondary) !important; }

.learn-panel .prose h2 {
  color: var(--text-primary) !important;
  font-size: 16px !important; font-weight: 700 !important;
  margin: 0 0 12px 0 !important; padding-bottom: 10px !important;
  border-bottom: 1px solid var(--border-muted) !important;
}
.learn-panel .prose h3 {
  color: var(--accent-purple) !important;
  font-size: 13px !important; font-weight: 600 !important;
  margin: 20px 0 8px 0 !important;
}
.learn-panel .prose strong { color: var(--text-primary) !important; font-weight: 600 !important; }
.learn-panel .prose em { color: var(--accent-cyan) !important; font-style: italic !important; }

.learn-panel .prose code {
  background: var(--code-bg) !important;
  color: var(--accent-orange) !important;
  padding: 2px 7px !important; border-radius: 5px !important;
  font-family: 'Fira Code', Consolas, monospace !important;
  font-size: 12px !important; border: 1px solid var(--border) !important;
}
.learn-panel .prose pre {
  background: var(--code-bg) !important; border: 1px solid var(--border) !important;
  border-radius: var(--radius-md) !important; padding: 16px 18px !important;
  overflow-x: auto !important; margin: 12px 0 !important;
}
.learn-panel .prose pre code {
  background: transparent !important; color: var(--code-text) !important;
  font-size: 12.5px !important; padding: 0 !important; border: none !important;
}

.learn-panel .prose table {
  width: 100% !important; border-collapse: separate !important;
  border-spacing: 0 !important; font-size: 13px !important; margin: 14px 0 !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-md) !important; overflow: hidden !important;
}
.learn-panel .prose thead tr { background: var(--bg-elevated) !important; }
.learn-panel .prose th {
  color: var(--accent-blue) !important; padding: 10px 14px !important;
  text-align: left !important; font-weight: 700 !important; font-size: 12px !important;
  border-bottom: 1px solid var(--border) !important;
}
.learn-panel .prose td {
  color: var(--text-secondary) !important; padding: 9px 14px !important;
  border-top: 1px solid var(--border-muted) !important;
}
.learn-panel .prose tr:hover td { background: var(--bg-elevated) !important; }
.learn-panel .prose ul, .learn-panel .prose ol { padding-left: 20px !important; }
.learn-panel .prose li { color: var(--text-secondary) !important; margin: 5px 0 !important; }

/* ══════════════════════════════════════════════
   CHATBOT
   ══════════════════════════════════════════════ */
.chatbot, .chatbot > div, .chatbot > div > div,
[data-testid="chatbot"], [data-testid="chatbot"] > div,
.bubble-wrap, .chat-wrap, .messages-wrap {
  background: var(--bg-input) !important;
  border: 1px solid var(--border-muted) !important;
  border-radius: var(--radius-md) !important;
}
.chatbot .empty { color: var(--text-muted) !important; font-size: 13px !important; }
.chatbot .message { background: transparent !important; padding: 8px 12px !important; }

.chatbot .user, .chatbot [data-testid="user"] {
  background: var(--user-bubble) !important;
  color: var(--text-primary) !important;
  border: 1px solid var(--user-border) !important;
  border-radius: 16px 16px 4px 16px !important;
  padding: 10px 14px !important; max-width: 82% !important; margin-left: auto !important;
}
.chatbot .bot, .chatbot [data-testid="bot"] {
  background: var(--bot-bubble) !important;
  color: var(--text-primary) !important;
  border: 1px solid var(--bot-border) !important;
  border-radius: 16px 16px 16px 4px !important;
  padding: 10px 14px !important; max-width: 82% !important;
}
/* ensure ALL text inside chatbot bubbles is always readable */
.chatbot .user p, .chatbot .user span, .chatbot .user li,
.chatbot .user div, .chatbot .user code { color: var(--text-primary) !important; }
.chatbot .bot  p, .chatbot .bot  span, .chatbot .bot  li,
.chatbot .bot  div, .chatbot .bot  code { color: var(--text-primary) !important; }
/* Gradio 6 message wrapper selectors */
[data-testid="user"] *, [data-testid="bot"] * { color: var(--text-primary) !important; }
.message-wrap *, .prose * { color: var(--text-primary) !important; }
/* override any white background that Gradio sets on message content */
.chatbot .message-wrap, .chatbot .message-wrap > div,
.chatbot .bubble-wrap > div { background: transparent !important; }
/* Force user bubble dark — Gradio svelte scoped selector */
.bubble.user-row, .user-row.bubble,
.message-bubble-border.user { background-color: #1c3d6e !important; color: #f0f6fc !important; }
.message-bubble-border.user *, .bubble.user-row * { color: #f0f6fc !important; }
/* Force bot bubble dark */
.message-bubble-border.bot, .bubble.bot-row, .bot-row.bubble {
  background-color: var(--bot-bubble) !important; color: var(--text-primary) !important;
}
/* Code / pre blocks inside ANY chatbot bubble — dark bg, light text */
.message-bubble-border pre,
.message-bubble-border code,
.bubble.user-row pre, .bubble.user-row code,
.bubble.bot-row  pre, .bubble.bot-row  code,
[data-testid="bot"] pre,  [data-testid="bot"] code,
[data-testid="user"] pre, [data-testid="user"] code,
.chatbot .bot  pre, .chatbot .bot  code,
.chatbot .user pre, .chatbot .user code {
  background: #161b22 !important;
  color: #79c0ff !important;
  border: 1px solid #30404f !important;
  border-radius: 6px !important;
  font-family: 'Fira Code', Consolas, monospace !important;
  font-size: 12.5px !important;
}
.message-bubble-border pre,
[data-testid="bot"] pre, [data-testid="user"] pre,
.chatbot .bot pre, .chatbot .user pre {
  padding: 12px 16px !important;
  overflow-x: auto !important;
  display: block !important;
  white-space: pre !important;
}
.message-bubble-border pre code,
[data-testid="bot"] pre code, [data-testid="user"] pre code,
.chatbot .bot pre code, .chatbot .user pre code {
  background: transparent !important;
  border: none !important;
  padding: 0 !important;
  color: #79c0ff !important;
}
/* inline code gets slightly different treatment */
.message-bubble-border p code,
[data-testid="bot"] p code, [data-testid="user"] p code {
  background: #21293a !important;
  color: #ffa657 !important;
  padding: 2px 6px !important;
  border-radius: 4px !important;
  font-size: 12px !important;
}
/* Light theme: bot bubble and code blocks */
[data-theme="light"] .message-bubble-border.bot,
[data-theme="light"] .bubble.bot-row {
  background-color: #f6f8fa !important; color: #1f2328 !important;
}
[data-theme="light"] .message-bubble-border pre,
[data-theme="light"] .message-bubble-border code,
[data-theme="light"] [data-testid="bot"] pre,
[data-theme="light"] [data-testid="bot"] code,
[data-theme="light"] .chatbot .bot pre,
[data-theme="light"] .chatbot .bot code {
  background: #eaeef2 !important;
  color: #0550ae !important;
  border-color: #d0d7de !important;
}
[data-theme="light"] .message-bubble-border p code,
[data-theme="light"] [data-testid="bot"] p code {
  background: #eaeef2 !important; color: #953800 !important;
}
/* Light theme user bubble */
[data-theme="light"] .bubble.user-row,
[data-theme="light"] .user-row.bubble,
[data-theme="light"] .message-bubble-border.user { background-color: #ddf4ff !important; color: #1f2328 !important; }
[data-theme="light"] .message-bubble-border.user *,
[data-theme="light"] .bubble.user-row * { color: #1f2328 !important; }

/* ══════════════════════════════════════════════
   INPUTS & TEXTAREAS
   ══════════════════════════════════════════════ */
.gradio-textbox textarea, .gradio-textbox input,
textarea, input[type="text"], input[type="search"],
input[type="password"] {
  background: var(--bg-input) !important;
  color: var(--text-primary) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-md) !important;
  font-size: 14px !important; padding: 10px 14px !important;
  transition: border-color 0.15s, box-shadow 0.15s !important;
}
textarea:focus, input:focus {
  border-color: var(--border-active) !important;
  box-shadow: 0 0 0 3px var(--glow-blue) !important;
  outline: none !important;
}
textarea::placeholder, input::placeholder { color: var(--text-faint) !important; }

/* Input labels */
.gradio-textbox label span,
.gradio-dropdown label span,
label span, .label-wrap span {
  color: var(--text-muted) !important;
  font-size: 12.5px !important;
  font-weight: 600 !important;
}

/* Latency / stat boxes */
.latency-box label span, .latency-box .label-wrap { display: none !important; }
.latency-box textarea {
  background: var(--bg-elevated) !important;
  color: var(--accent-green) !important;
  border: 1px solid var(--border-muted) !important;
  border-radius: var(--radius-md) !important;
  font-size: 12px !important; font-weight: 600 !important;
  text-align: center !important; padding: 6px 12px !important;
}

/* ══════════════════════════════════════════════
   DROPDOWNS — Gradio uses svelte-select internally
   Class names from Dropdown--Uz_kS2s.css:
   .wrap .wrap-inner .secondary-wrap .options .item .active .icon-wrap
   ══════════════════════════════════════════════ */

/* Outer container */
.gradio-dropdown .wrap,
.gradio-dropdown .wrap-inner {
  background: var(--bg-input) !important;
  color: var(--text-primary) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-md) !important;
  min-height: 38px !important;
}
.gradio-dropdown .wrap:focus-within {
  border-color: var(--border-active) !important;
  box-shadow: 0 0 0 3px var(--glow-blue) !important;
}

/* Selected value text */
.gradio-dropdown .secondary-wrap,
.gradio-dropdown .secondary-wrap span,
.gradio-dropdown .wrap-inner span,
.gradio-dropdown input {
  color: var(--text-primary) !important;
  background: transparent !important;
  font-size: 13.5px !important;
}

/* Placeholder / subdued text */
.gradio-dropdown .subdued { color: var(--text-faint) !important; }

/* Chevron icon */
.gradio-dropdown .icon-wrap svg { color: var(--text-muted) !important; fill: var(--text-muted) !important; }

/* THE DROPDOWN LIST — this is the white box in the screenshot.
   Gradio portals the popup to <body> so it escapes .gradio-dropdown.
   Target it globally by class name (from Dropdown--Uz_kS2s.css). */
.gradio-dropdown .options,
.options.svelte-1ou0lab,
ul.options,
.listbox-options,
[data-testid="dropdown-options"],
.dropdown-options {
  background: #1c2333 !important;
  border: 1px solid #30404f !important;
  border-radius: var(--radius-md) !important;
  box-shadow: 0 8px 32px rgba(0,0,0,0.7) !important;
  padding: 4px !important;
  z-index: 9999 !important;
  overflow: hidden !important;
  color: #f0f6fc !important;
}

/* Each option row */
.gradio-dropdown .options .item,
.gradio-dropdown .options .inner-item,
.item.svelte-1ou0lab,
.options.svelte-1ou0lab li,
.listbox-option,
[data-testid="dropdown-option"] {
  color: #cdd9e5 !important;
  background: transparent !important;
  border-radius: var(--radius-sm) !important;
  padding: 8px 12px !important;
  font-size: 13.5px !important;
  cursor: pointer !important;
  transition: background 0.1s, color 0.1s !important;
}

/* Hover + active (keyboard-focused) option */
.gradio-dropdown .options .item:hover,
.gradio-dropdown .options .item.active,
.gradio-dropdown .options .inner-item:hover,
.item.svelte-1ou0lab:hover,
.active.svelte-1ou0lab,
.listbox-option:hover,
[data-testid="dropdown-option"]:hover {
  background: #21293a !important;
  color: #f0f6fc !important;
}

/* Disabled state */
.gradio-dropdown[disabled] .wrap,
.gradio-dropdown .wrap[disabled] {
  opacity: 0.45 !important;
  cursor: not-allowed !important;
}


/* Light theme: dropdown list stays white with dark text */
[data-theme="light"] .gradio-dropdown .options,
[data-theme="light"] .options.svelte-1ou0lab,
[data-theme="light"] ul.options,
[data-theme="light"] .listbox-options {
  background: #ffffff !important;
  border-color: #d0d7de !important;
  box-shadow: 0 8px 24px rgba(0,0,0,0.15) !important;
  color: #1f2328 !important;
}
[data-theme="light"] .gradio-dropdown .options .item,
[data-theme="light"] .gradio-dropdown .options .inner-item,
[data-theme="light"] .item.svelte-1ou0lab,
[data-theme="light"] .listbox-option {
  color: #24292f !important;
}
[data-theme="light"] .gradio-dropdown .options .item:hover,
[data-theme="light"] .gradio-dropdown .options .item.active,
[data-theme="light"] .item.svelte-1ou0lab:hover,
[data-theme="light"] .active.svelte-1ou0lab {
  background: #eaeef2 !important;
  color: #1f2328 !important;
}

/* ══════════════════════════════════════════════
   BUTTONS
   ══════════════════════════════════════════════ */
button.primary, .send-btn {
  background: linear-gradient(135deg, #1f6feb, #1558c9) !important;
  color: #ffffff !important;
  border: none !important; border-radius: var(--radius-md) !important;
  font-weight: 600 !important; font-size: 13.5px !important;
  padding: 9px 24px !important; transition: all 0.15s !important;
  box-shadow: var(--shadow-btn) !important;
}
button.primary:hover {
  background: linear-gradient(135deg, #388bfd, #1f6feb) !important;
  transform: translateY(-1px) !important;
}
button.primary:active { transform: scale(0.97) !important; }

button.secondary {
  background: var(--bg-elevated) !important;
  color: var(--text-secondary) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-md) !important;
  font-size: 13px !important; font-weight: 500 !important;
  padding: 9px 20px !important; transition: all 0.15s !important;
}
button.secondary:hover {
  background: var(--bg-surface) !important;
  color: var(--text-primary) !important;
  border-color: var(--border-active) !important;
}

/* ══════════════════════════════════════════════
   HOW IT WORKS — FLOW BOX
   ══════════════════════════════════════════════ */
.flow-box, .flow-box > div {
  background: var(--bg-input) !important;
  border: 1px solid var(--border-muted) !important;
  border-radius: var(--radius-md) !important;
  padding: 18px 20px !important;
  min-height: 300px !important;
}
.flow-box .prose, .flow-box .prose * {
  font-size: 13.5px !important;
  line-height: 1.8 !important;
  color: var(--text-secondary) !important;
}
.flow-box .prose code,
.flow-box .prose pre,
.flow-box .prose pre code {
  background: var(--bg-card) !important;
  color: var(--code-text) !important;
  border: 1px solid var(--border-muted) !important;
  border-radius: var(--radius-sm) !important;
  font-family: 'Fira Code', Consolas, monospace !important;
  font-size: 12px !important;
  padding: 3px 9px !important;
}
.flow-box .prose pre { padding: 12px 16px !important; overflow-x: auto !important; margin: 8px 0 !important; }
.flow-box .prose pre code { padding: 0 !important; border: none !important; background: transparent !important; }
.flow-box .prose strong { color: var(--accent-blue) !important; font-weight: 700 !important; }
.flow-box .prose em     { color: var(--text-muted) !important; font-style: italic !important; }
.flow-box .prose hr     { border-color: var(--border-muted) !important; margin: 12px 0 !important; }

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
  color: var(--text-secondary) !important;
  font-size: 13px !important; font-weight: 500 !important;
  padding: 10px 14px !important; cursor: pointer !important;
}
details summary:hover {
  color: var(--text-primary) !important;
  background: var(--bg-card) !important;
}
/* content inside accordion */
details > div, .accordion > div {
  background: var(--bg-elevated) !important;
  color: var(--text-secondary) !important;
  padding: 12px 14px !important;
}

/* ══════════════════════════════════════════════
   JSON VIEWER
   ══════════════════════════════════════════════ */
.json-holder, .json-holder * {
  background: var(--code-bg) !important;
  color: var(--code-text) !important;
  border-radius: var(--radius-md) !important;
  font-family: 'Fira Code', monospace !important;
  font-size: 12px !important;
}

/* ══════════════════════════════════════════════
   THEME RADIO (hidden — just for Gradio wiring)
   ══════════════════════════════════════════════ */
.theme-radio { display: none !important; }

/* ══════════════════════════════════════════════
   SCROLLBARS
   ══════════════════════════════════════════════ */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-faint); }

/* ══════════════════════════════════════════════
   UNIFIED TOP BAR
   ══════════════════════════════════════════════ */

/* Gradio Row renders: .gradio-row > .gap (flex container) > children */
/* Target only the .gap inside our topbar row to set flex layout */
.topbar-row > .gap {
  display: flex !important;
  flex-direction: row !important;
  align-items: center !important;
  flex-wrap: nowrap !important;
  gap: 10px !important;
  width: 100% !important;
}
.topbar-row {
  background: var(--bg-surface) !important;
  border-bottom: 1px solid var(--border-muted) !important;
  padding: 0 20px !important;
  min-height: 64px !important;
}

/* Branding HTML block */
.topbar-brand-col { flex: 0 0 auto !important; padding-right: 14px !important; border-right: 1px solid var(--border-muted) !important; align-self: center !important; }
.topbar-brand { display: flex; align-items: center; gap: 10px; white-space: nowrap; }
.topbar-logo  { width: 34px; height: 34px; border-radius: 8px; flex-shrink: 0; background: linear-gradient(135deg,#2563eb,#7c3aed); display: flex; align-items: center; justify-content: center; font-size: 18px; }
.topbar-title { font-size: 13px; font-weight: 700; color: var(--text-primary) !important; letter-spacing: -0.2px; line-height: 1.2; }
.topbar-sub   { font-size: 10px; color: var(--text-faint) !important; margin-top: 1px; }

/* Topbar input fields — compact labels + 34px input height */
.topbar-input { align-self: center !important; }
.topbar-input .label-wrap span,
.topbar-input label span {
  font-size: 10px !important; font-weight: 700 !important; color: var(--text-faint) !important;
  text-transform: uppercase !important; letter-spacing: 0.5px !important;
}
.topbar-input textarea,
.topbar-input input[type="text"],
.topbar-input input[type="password"] {
  height: 34px !important; min-height: 34px !important;
  padding: 5px 10px !important; font-size: 13px !important;
}
.topbar-input .wrap,
.topbar-input .wrap-inner {
  min-height: 34px !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-md) !important;
  background: var(--bg-input) !important;
}

/* Status pill — no label, coloured border */
.topbar-status { align-self: center !important; flex: 0 0 auto !important; }
.topbar-status .label-wrap { display: none !important; }
.topbar-status textarea {
  height: 34px !important; min-height: 34px !important;
  font-size: 11px !important; font-weight: 700 !important;
  padding: 5px 10px !important; text-align: center !important;
  border-radius: var(--radius-md) !important;
}
.config-status-ok   textarea { color: #56d364 !important; background: rgba(86,211,100,0.08) !important; border-color: rgba(86,211,100,0.3) !important; }
.config-status-err  textarea { color: #ff7b72 !important; background: rgba(255,123,114,0.08) !important; border-color: rgba(255,123,114,0.3) !important; }
.config-status-warn textarea { color: #ffa657 !important; background: rgba(255,166,87,0.08)  !important; border-color: rgba(255,166,87,0.3)  !important; }

/* Theme column container */
.theme-col { flex: 0 0 auto !important; align-self: center !important; padding: 0 !important; }
.theme-label { font-size: 10px !important; font-weight: 700 !important; color: var(--text-faint) !important; text-transform: uppercase !important; text-align: center !important; margin-bottom: 4px !important; }
/* Theme button row — Gradio Row inner .gap must be horizontal */
.theme-btn-row > .gap {
  display: flex !important; flex-direction: row !important;
  gap: 4px !important; flex-wrap: nowrap !important;
  justify-content: center !important; align-items: center !important;
  padding: 0 !important;
}
/* Each button's Gradio wrapper */
.theme-btn { flex: 0 0 32px !important; min-width: 32px !important; }
.theme-btn button {
  width: 32px !important; height: 32px !important; min-width: 32px !important;
  padding: 0 !important; font-size: 16px !important; line-height: 1 !important;
  border-radius: 7px !important; display: flex !important;
  align-items: center !important; justify-content: center !important;
  background: var(--bg-elevated) !important; color: var(--text-secondary) !important;
  border: 1px solid var(--border) !important; transition: all 0.15s !important; cursor: pointer !important;
}
.theme-btn button:hover { border-color: var(--border-active) !important; background: var(--bg-card) !important; color: var(--text-primary) !important; }
.theme-btn-dark button { background: var(--btn-primary) !important; border-color: var(--btn-primary) !important; color: #fff !important; }

/* TAB CONTENT */
.tabitem { padding: 10px !important; }
.gradio-row { gap: 10px !important; align-items: stretch !important; }
.gradio-container > .main > .wrap { padding: 0 !important; }

/* ══════════════════════════════════════════════
   PERSONA TEXTBOX (ex02)
   ══════════════════════════════════════════════ */
.gradio-textbox label span { color: var(--text-muted) !important; }

/* ══════════════════════════════════════════════
   TOOL CALLS / TRACE BOXES
   ══════════════════════════════════════════════ */
.gradio-json, .gradio-json *, .gradio-dataframe,
.gradio-dataframe * {
  background: var(--code-bg) !important;
  color: var(--text-secondary) !important;
  font-family: 'Fira Code', monospace !important;
  font-size: 12px !important;
}
.gradio-dataframe th { background: var(--bg-elevated) !important; color: var(--accent-blue) !important; font-weight: 600 !important; }
.gradio-dataframe td { color: var(--text-secondary) !important; }

/* ══════════════════════════════════════════════
   RESPONSIVE
   ══════════════════════════════════════════════ */
@media (max-width: 900px) {
  .panel-card { min-height: 300px !important; padding: 14px 16px !important; }
  .tab-nav button { padding: 10px 10px !important; font-size: 11.5px !important; }
}
@media (max-width: 600px) {
  .tab-nav button { padding: 8px 8px !important; font-size: 11px !important; }
}

"""

# JS that runs once on page load — applies saved theme
THEME_JS = """
function applyTheme(t) {
  var resolved = t === 'system'
    ? (window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark')
    : t;
  document.documentElement.setAttribute('data-theme', resolved);
  localStorage.setItem('ai-agent-theme', t);
}
var saved = localStorage.getItem('ai-agent-theme') || 'dark';
applyTheme(saved);
setTimeout(function(){ applyTheme(localStorage.getItem('ai-agent-theme') || 'dark'); }, 800);
"""


# ─────────────────────────────────────────────
# FLOW ANIMATION HELPER
# ─────────────────────────────────────────────

def animate_flow(steps: list, active_idx: int) -> str:
    """
    Render a clean vertical step list.
    - Completed: ✅ Step Name
    - Active:    ▶ Step Name  +  full diagram/description below
    - Future:    ○ Step Name  (dimmed)
    """
    def label(key: str) -> str:
        return key.replace("_", " ").title()

    sections = []
    for i, (key, text) in enumerate(steps):
        is_idle = (i == 0 and key in ("idle", "waiting", "start"))

        if is_idle:
            if active_idx == 0:
                # Show the idle diagram before anything starts
                sections.append(f"*Waiting for your message...*\n\n{text}")
            # skip idle step once processing begins
            continue

        if i < active_idx:
            sections.append(f"✅ &nbsp;**{label(key)}**")
        elif i == active_idx:
            sections.append(f"**▶ {label(key)}**\n\n{text}")
        else:
            sections.append(f"○ &nbsp;{label(key)}")

    return "\n\n".join(sections) if sections else steps[0][1]


# ─────────────────────────────────────────────
# PER-EXERCISE TAB BUILDERS
# ─────────────────────────────────────────────

def build_ex01_tab(cfg_state):
    state = gr.State({"history": []})

    with gr.Row(equal_height=False):
        # ── Panel 1: Learn ──
        with gr.Column(scale=2, elem_classes="panel-card learn-panel"):
            gr.Markdown("### 📖 Learn", elem_classes="section-label")
            gr.Markdown(ex01_simple.CONCEPT)

        # ── Panel 2: Try It ──
        with gr.Column(scale=4, elem_classes="panel-card"):
            gr.Markdown("### ▶ Try It Live", elem_classes="section-label")
            chatbot   = gr.Chatbot(height=480, label="", show_label=False)
            msg_input = gr.Textbox(placeholder="Type a message...", show_label=False, lines=1)
            with gr.Row():
                send_btn  = gr.Button("Send", variant="primary", elem_classes="send-btn")
                clear_btn = gr.Button("Clear", variant="secondary")
            latency   = gr.Textbox(label="", value="⏱ Latency: —", interactive=False,
                                   elem_classes="latency-box", max_lines=1)
            with gr.Accordion("🔍 Raw JSON (last request/response)", open=False):
                raw_json = gr.JSON(label="")

        # ── Panel 3: How It Works ──
        with gr.Column(scale=2, elem_classes="panel-card"):
            gr.Markdown("### 🔄 How It Works", elem_classes="section-label")
            flow_display = gr.Markdown(
                animate_flow(ex01_simple.FLOW_STEPS, 0), elem_classes="flow-box"
            )

    def respond(message, history, s, cfg):
        if not message.strip():
            return history, s, "⏱ Latency: —", None, animate_flow(ex01_simple.FLOW_STEPS, 0)
        try:
            # Animate: input
            yield history, s, "⏱ Sending...", None, animate_flow(ex01_simple.FLOW_STEPS, 1)
            time.sleep(0.3)
            yield history, s, "⏱ Sending...", None, animate_flow(ex01_simple.FLOW_STEPS, 2)
            time.sleep(0.3)
            yield history, s, "⏱ Waiting for AI...", None, animate_flow(ex01_simple.FLOW_STEPS, 3)

            result = ex01_simple.run(message, cfg=cfg)

            yield history, s, "⏱ Parsing...", None, animate_flow(ex01_simple.FLOW_STEPS, 4)
            time.sleep(0.2)

            history = history + [{"role": "user", "content": message}, {"role": "assistant", "content": result["reply"]}]
            yield (history, s, f"⏱ Latency: {result['latency']}s",
                   {"request": result["request"], "response": result["response"]},
                   animate_flow(ex01_simple.FLOW_STEPS, 5))
        except Exception as e:
            history = history + [{"role": "user", "content": message}, {"role": "assistant", "content": f"❌ Error: {e}"}]
            yield history, s, "⏱ Error", None, animate_flow(ex01_simple.FLOW_STEPS, 0)

    send_btn.click(respond, [msg_input, chatbot, state, cfg_state],
                   [chatbot, state, latency, raw_json, flow_display]).then(
                   lambda: gr.update(value=""), outputs=msg_input)
    msg_input.submit(respond, [msg_input, chatbot, state, cfg_state],
                     [chatbot, state, latency, raw_json, flow_display]).then(
                     lambda: gr.update(value=""), outputs=msg_input)
    clear_btn.click(lambda: ([], {"history": []}, "⏱ Latency: —", None, animate_flow(ex01_simple.FLOW_STEPS, 0)),
                    outputs=[chatbot, state, latency, raw_json, flow_display])


def build_ex02_tab(cfg_state):
    state = gr.State({"history": []})

    with gr.Row(equal_height=False):
        with gr.Column(scale=2, elem_classes="panel-card learn-panel"):
            gr.Markdown("### 📖 Learn", elem_classes="section-label")
            gr.Markdown(ex02_memory.CONCEPT)

        with gr.Column(scale=4, elem_classes="panel-card"):
            gr.Markdown("### ▶ Try It Live", elem_classes="section-label")
            persona_input = gr.Textbox(
                value=ex02_memory.DEFAULT_PERSONA,
                label="System Prompt (persona) — edit me!",
                lines=2,
            )
            chatbot   = gr.Chatbot(height=480, label="", show_label=False)
            msg_input = gr.Textbox(placeholder="Type a message...", show_label=False, lines=1)
            with gr.Row():
                send_btn  = gr.Button("Send", variant="primary", elem_classes="send-btn")
                clear_btn = gr.Button("Clear Chat", variant="secondary")
            latency = gr.Textbox(label="", value="⏱ Latency: —", interactive=False,
                                 elem_classes="latency-box", max_lines=1)
            turn_count = gr.Textbox(label="", value="💬 Turns: 0", interactive=False,
                                    elem_classes="latency-box", max_lines=1)

        with gr.Column(scale=2, elem_classes="panel-card"):
            gr.Markdown("### 🔄 How It Works", elem_classes="section-label")
            flow_display = gr.Markdown(animate_flow(ex02_memory.FLOW_STEPS, 0), elem_classes="flow-box")

    def respond(message, history, s, persona, cfg):
        if not message.strip():
            return history, s, "⏱ Latency: —", f"💬 Turns: {len(s['history'])//2}", animate_flow(ex02_memory.FLOW_STEPS, 0)
        try:
            yield history, s, "⏱ Sending...", f"💬 Turns: {len(s['history'])//2}", animate_flow(ex02_memory.FLOW_STEPS, 1)
            time.sleep(0.3)
            yield history, s, "⏱ Sending...", f"💬 Turns: {len(s['history'])//2}", animate_flow(ex02_memory.FLOW_STEPS, 2)
            time.sleep(0.2)
            yield history, s, "⏱ Waiting for AI...", f"💬 Turns: {len(s['history'])//2}", animate_flow(ex02_memory.FLOW_STEPS, 3)

            result = ex02_memory.run(message, s["history"], persona, cfg=cfg)
            s["history"] = result["history"]

            history = history + [{"role": "user", "content": message}, {"role": "assistant", "content": result["reply"]}]
            yield (history, s, f"⏱ Latency: {result['latency']}s",
                   f"💬 Turns: {len(s['history'])//2}",
                   animate_flow(ex02_memory.FLOW_STEPS, 5))
        except Exception as e:
            history = history + [{"role": "user", "content": message}, {"role": "assistant", "content": f"❌ Error: {e}"}]
            yield history, s, "⏱ Error", f"💬 Turns: {len(s['history'])//2}", animate_flow(ex02_memory.FLOW_STEPS, 0)

    send_btn.click(respond, [msg_input, chatbot, state, persona_input, cfg_state],
                   [chatbot, state, latency, turn_count, flow_display]).then(
                   lambda: gr.update(value=""), outputs=msg_input)
    msg_input.submit(respond, [msg_input, chatbot, state, persona_input, cfg_state],
                     [chatbot, state, latency, turn_count, flow_display]).then(
                     lambda: gr.update(value=""), outputs=msg_input)
    clear_btn.click(lambda: ([], {"history": []}, "⏱ Latency: —", "💬 Turns: 0", animate_flow(ex02_memory.FLOW_STEPS, 0)),
                    outputs=[chatbot, state, latency, turn_count, flow_display])


def build_ex03_tab(cfg_state):
    state = gr.State({"history": []})

    with gr.Row(equal_height=False):
        with gr.Column(scale=2, elem_classes="panel-card learn-panel"):
            gr.Markdown("### 📖 Learn", elem_classes="section-label")
            gr.Markdown(ex03_tools.CONCEPT)

        with gr.Column(scale=4, elem_classes="panel-card"):
            gr.Markdown("### ▶ Try It Live", elem_classes="section-label")
            chatbot   = gr.Chatbot(height=480, label="", show_label=False)
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

        with gr.Column(scale=2, elem_classes="panel-card"):
            gr.Markdown("### 🔄 How It Works", elem_classes="section-label")
            flow_display = gr.Markdown(animate_flow(ex03_tools.FLOW_STEPS, 0), elem_classes="flow-box")

    def respond(message, history, s, cfg):
        if not message.strip():
            return history, s, "⏱ Latency: —", [], animate_flow(ex03_tools.FLOW_STEPS, 0)
        try:
            yield history, s, "⏱ Sending...", [], animate_flow(ex03_tools.FLOW_STEPS, 1)
            time.sleep(0.3)
            yield history, s, "⏱ AI deciding...", [], animate_flow(ex03_tools.FLOW_STEPS, 2)

            result = ex03_tools.run(message, s["history"], cfg=cfg)
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

    send_btn.click(respond, [msg_input, chatbot, state, cfg_state],
                   [chatbot, state, latency, tool_log, flow_display]).then(
                   lambda: gr.update(value=""), outputs=msg_input)
    msg_input.submit(respond, [msg_input, chatbot, state, cfg_state],
                     [chatbot, state, latency, tool_log, flow_display]).then(
                     lambda: gr.update(value=""), outputs=msg_input)
    clear_btn.click(lambda: ([], {"history": []}, "⏱ Latency: —", [], animate_flow(ex03_tools.FLOW_STEPS, 0)),
                    outputs=[chatbot, state, latency, tool_log, flow_display])


def build_ex04_tab(cfg_state):
    with gr.Row(equal_height=False):
        with gr.Column(scale=2, elem_classes="panel-card learn-panel"):
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

        with gr.Column(scale=2, elem_classes="panel-card"):
            gr.Markdown("### 🔄 How It Works", elem_classes="section-label")
            flow_display = gr.Markdown(animate_flow(ex04_react.FLOW_STEPS, 0), elem_classes="flow-box")

    def respond(message, cfg):
        if not message.strip():
            return "_Enter a question..._", "⏱ Latency: —", animate_flow(ex04_react.FLOW_STEPS, 0)
        yield "⏳ _Thinking..._", "⏱ Running ReAct loop...", animate_flow(ex04_react.FLOW_STEPS, 1)
        time.sleep(0.3)
        yield "⏳ _Thinking..._", "⏱ Running ReAct loop...", animate_flow(ex04_react.FLOW_STEPS, 2)
        try:
            result = ex04_react.run(message, cfg=cfg)
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

    send_btn.click(respond, [msg_input, cfg_state], [trace_box, latency, flow_display]).then(
                   lambda: gr.update(value=""), outputs=msg_input)
    msg_input.submit(respond, [msg_input, cfg_state], [trace_box, latency, flow_display]).then(
                     lambda: gr.update(value=""), outputs=msg_input)


def build_ex05_tab(cfg_state):
    with gr.Row(equal_height=False):
        with gr.Column(scale=2, elem_classes="panel-card learn-panel"):
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

        with gr.Column(scale=2, elem_classes="panel-card"):
            gr.Markdown("### 🔄 How It Works", elem_classes="section-label")
            flow_display = gr.Markdown(animate_flow(ex05_multi_agent.FLOW_STEPS, 0), elem_classes="flow-box")

    def respond(message, cfg):
        if not message.strip():
            return "_Enter a task..._", "_..._", "⏱ Latency: —", animate_flow(ex05_multi_agent.FLOW_STEPS, 0)
        yield "_Planner thinking..._", "_Waiting for plan..._", "⏱ Running...", animate_flow(ex05_multi_agent.FLOW_STEPS, 1)
        time.sleep(0.3)
        try:
            result = ex05_multi_agent.run(message, cfg=cfg)
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

    send_btn.click(respond, [msg_input, cfg_state], [planner_box, writer_box, latency, flow_display]).then(
                   lambda: gr.update(value=""), outputs=msg_input)
    msg_input.submit(respond, [msg_input, cfg_state], [planner_box, writer_box, latency, flow_display]).then(
                     lambda: gr.update(value=""), outputs=msg_input)


def build_ex06_tab(cfg_state):
    state = gr.State({"history": []})

    with gr.Row(equal_height=False):
        with gr.Column(scale=2, elem_classes="panel-card learn-panel"):
            gr.Markdown("### 📖 Learn", elem_classes="section-label")
            gr.Markdown(ex06_streaming.CONCEPT)

        with gr.Column(scale=4, elem_classes="panel-card"):
            gr.Markdown("### ▶ Try It Live", elem_classes="section-label")
            gr.Markdown("_Watch tokens arrive one by one — the reply builds in real time._",
                        elem_classes="section-label")
            chatbot   = gr.Chatbot(height=480, label="", show_label=False)
            msg_input = gr.Textbox(placeholder="Type a message...", show_label=False, lines=1)
            with gr.Row():
                send_btn  = gr.Button("Send", variant="primary", elem_classes="send-btn")
                clear_btn = gr.Button("Clear", variant="secondary")
            with gr.Row():
                latency    = gr.Textbox(label="", value="⏱ Latency: —", interactive=False,
                                        elem_classes="latency-box", max_lines=1)
                chunk_count = gr.Textbox(label="", value="📦 Chunks: 0", interactive=False,
                                         elem_classes="latency-box", max_lines=1)

        with gr.Column(scale=2, elem_classes="panel-card"):
            gr.Markdown("### 🔄 How It Works", elem_classes="section-label")
            flow_display = gr.Markdown(animate_flow(ex06_streaming.FLOW_STEPS, 0), elem_classes="flow-box")

    def respond(message, history, s, cfg):
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
            for chunk in ex06_streaming.run_stream(message, s["history"], cfg=cfg):
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

    send_btn.click(respond, [msg_input, chatbot, state, cfg_state],
                   [chatbot, state, latency, chunk_count, flow_display]).then(
                   lambda: gr.update(value=""), outputs=msg_input)
    msg_input.submit(respond, [msg_input, chatbot, state, cfg_state],
                     [chatbot, state, latency, chunk_count, flow_display]).then(
                     lambda: gr.update(value=""), outputs=msg_input)
    clear_btn.click(lambda: ([], {"history": []}, "⏱ Latency: —", "📦 Chunks: 0", animate_flow(ex06_streaming.FLOW_STEPS, 0)),
                    outputs=[chatbot, state, latency, chunk_count, flow_display])


def build_ex07_tab(cfg_state):
    with gr.Row(equal_height=False):
        with gr.Column(scale=2, elem_classes="panel-card learn-panel"):
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

        with gr.Column(scale=2, elem_classes="panel-card"):
            gr.Markdown("### 🔄 How It Works", elem_classes="section-label")
            flow_display = gr.Markdown(animate_flow(ex07_structured.FLOW_STEPS, 0), elem_classes="flow-box")

    def respond(message, cfg):
        if not message.strip():
            return ("⏱ Latency: —", "", "", "", "", "", "", None,
                    animate_flow(ex07_structured.FLOW_STEPS, 0))
        yield ("⏱ Sending...", "", "", "", "", "", "", None,
               animate_flow(ex07_structured.FLOW_STEPS, 1))
        time.sleep(0.3)
        yield ("⏱ AI analyzing...", "", "", "", "", "", "", None,
               animate_flow(ex07_structured.FLOW_STEPS, 2))
        try:
            result = ex07_structured.run(message, cfg=cfg)
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

    send_btn.click(respond, [msg_input, cfg_state],
                   [latency, summary_box, sentiment_box, score_box,
                    keywords_box, pros_box, cons_box, raw_json, flow_display]).then(
                   lambda: gr.update(value=""), outputs=msg_input)
    msg_input.submit(respond, [msg_input, cfg_state],
                     [latency, summary_box, sentiment_box, score_box,
                      keywords_box, pros_box, cons_box, raw_json, flow_display]).then(
                     lambda: gr.update(value=""), outputs=msg_input)


def build_ex08_tab(cfg_state):
    with gr.Row(equal_height=False):
        with gr.Column(scale=2, elem_classes="panel-card learn-panel"):
            gr.Markdown("### 📖 Learn", elem_classes="section-label")
            gr.Markdown(ex08_rag.CONCEPT)
            gr.Markdown("### 📄 Document Store")
            for doc in ex08_rag.DOCUMENTS:
                with gr.Accordion(f"📄 {doc['title']}", open=False):
                    gr.Markdown(doc["content"])

        with gr.Column(scale=4, elem_classes="panel-card"):
            gr.Markdown("### ▶ Try It Live", elem_classes="section-label")
            chatbot   = gr.Chatbot(height=480, label="", show_label=False)
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

        with gr.Column(scale=2, elem_classes="panel-card"):
            gr.Markdown("### 🔄 How It Works", elem_classes="section-label")
            flow_display = gr.Markdown(animate_flow(ex08_rag.FLOW_STEPS, 0), elem_classes="flow-box")

    def respond(message, history, cfg):
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
            result = ex08_rag.run(message, cfg=cfg)
            history = history + [{"role": "user", "content": message}, {"role": "assistant", "content": result["reply"]}]
            sources_md = "**Retrieved:** " + " · ".join(f"`{s}`" for s in result["sources"])
            yield (history, f"⏱ Latency: {result['latency']}s",
                   sources_md, animate_flow(ex08_rag.FLOW_STEPS, 5))
        except Exception as e:
            history = history + [{"role": "user", "content": message}, {"role": "assistant", "content": f"❌ Error: {e}"}]
            yield history, "⏱ Error", "_Error_", animate_flow(ex08_rag.FLOW_STEPS, 0)

    send_btn.click(respond, [msg_input, chatbot, cfg_state],
                   [chatbot, latency, sources_box, flow_display]).then(
                   lambda: gr.update(value=""), outputs=msg_input)
    msg_input.submit(respond, [msg_input, chatbot, cfg_state],
                     [chatbot, latency, sources_box, flow_display]).then(
                     lambda: gr.update(value=""), outputs=msg_input)
    clear_btn.click(lambda: ([], "⏱ Latency: —", "_..._", animate_flow(ex08_rag.FLOW_STEPS, 0)),
                    outputs=[chatbot, latency, sources_box, flow_display])


# ─────────────────────────────────────────────
# MAIN APP ASSEMBLY
# ─────────────────────────────────────────────

def build_app():
    with gr.Blocks(
        title="AI Agent Learning Platform",
        fill_width=True,
    ) as app:

        # ── Top bar: logo | API key | Provider | Model | status | theme ──
        cfg_state = gr.State({
            "api_key":     "",
            "provider_id": ex_config.DEFAULT_PROVIDER,
            "model":       ex_config.get_default_model(ex_config.DEFAULT_PROVIDER),
        })

        with gr.Row(elem_classes="topbar-row"):
            # Branding column (pure HTML, auto-width)
            gr.HTML("""
<div class="topbar-brand">
  <div class="topbar-logo">🤖</div>
  <div>
    <div class="topbar-title">AI Agent Learning</div>
    <div class="topbar-sub">Simple → RAG</div>
  </div>
</div>
""", elem_classes="topbar-brand-col")

            api_key_input = gr.Textbox(
                placeholder="API Key",
                show_label=True,
                label="🔑 Key",
                type="password",
                scale=3,
                min_width=180,
                elem_classes="topbar-input",
            )
            provider_dd = gr.Dropdown(
                choices=ex_config.PROVIDER_LABELS,
                value=None,
                label="🌐 Provider",
                show_label=True,
                interactive=False,
                scale=2,
                min_width=130,
                elem_classes="topbar-input",
            )
            model_dd = gr.Dropdown(
                choices=[],
                value=None,
                label="🤖 Model",
                show_label=True,
                interactive=False,
                scale=2,
                min_width=160,
                elem_classes="topbar-input",
            )
            cfg_status = gr.Textbox(
                value="⚠ Enter key",
                show_label=False,
                interactive=False,
                scale=1,
                min_width=100,
                elem_classes="config-status config-status-warn topbar-status",
            )
            with gr.Column(scale=0, min_width=112, elem_classes="theme-col"):
                gr.HTML('<div class="theme-label">Theme</div>')
                with gr.Row(elem_classes="theme-btn-row"):
                    theme_dark_btn   = gr.Button("🌙", variant="secondary", size="sm", min_width=34, elem_classes="theme-btn theme-btn-dark")
                    theme_light_btn  = gr.Button("☀️", variant="secondary", size="sm", min_width=34, elem_classes="theme-btn theme-btn-light")
                    theme_system_btn = gr.Button("💻", variant="secondary", size="sm", min_width=34, elem_classes="theme-btn theme-btn-system")

        # When API key is entered → unlock provider dropdown, set default
        def on_api_key(key, cfg):
            key = key.strip()
            if not key:
                db_set("api_key", "")
                return (
                    gr.update(value=None, interactive=False),
                    gr.update(choices=[], value=None, interactive=False),
                    gr.update(value="⚠ Enter API key", elem_classes="config-status config-status-warn"),
                    {**cfg, "api_key": "", "provider_id": ex_config.DEFAULT_PROVIDER, "model": ""},
                )
            db_set("api_key", key)
            default_label = ex_config.PROVIDERS[ex_config.DEFAULT_PROVIDER]["label"]
            default_models = ex_config.get_models(ex_config.DEFAULT_PROVIDER)
            default_model  = default_models[0]
            return (
                gr.update(value=default_label, choices=ex_config.PROVIDER_LABELS, interactive=True),
                gr.update(choices=default_models, value=default_model, interactive=True),
                gr.update(value=f"✅ {default_label} · {default_model}", elem_classes="config-status config-status-ok"),
                {**cfg, "api_key": key, "provider_id": ex_config.DEFAULT_PROVIDER, "model": default_model},
            )

        api_key_input.change(
            on_api_key,
            inputs=[api_key_input, cfg_state],
            outputs=[provider_dd, model_dd, cfg_status, cfg_state],
        )

        # ── Restore API key on page load from SQLite ──
        def restore_api_key(cfg):
            saved_key = db_get("api_key")
            updates = on_api_key(saved_key, cfg)
            return updates + (gr.update(value=saved_key),)

        app.load(
            fn=restore_api_key,
            inputs=[cfg_state],
            outputs=[provider_dd, model_dd, cfg_status, cfg_state, api_key_input],
        )

        # When provider changes → refresh model list, pick first model
        def on_provider(provider_label, cfg):
            if not provider_label:
                return gr.update(choices=[], value=None), gr.update(value="⚠ Select provider", elem_classes="config-status config-status-warn"), cfg
            pid    = ex_config.label_to_id(provider_label)
            models = ex_config.get_models(pid)
            model  = models[0]
            return (
                gr.update(choices=models, value=model, interactive=True),
                gr.update(value=f"✅ {provider_label} · {model}", elem_classes="config-status config-status-ok"),
                {**cfg, "provider_id": pid, "model": model},
            )

        provider_dd.change(
            on_provider,
            inputs=[provider_dd, cfg_state],
            outputs=[model_dd, cfg_status, cfg_state],
        )

        # When model changes → update cfg
        def on_model(model, cfg):
            if not model:
                return cfg
            pid = cfg.get("provider_id", ex_config.DEFAULT_PROVIDER)
            label = ex_config.PROVIDERS[pid]["label"]
            return {**cfg, "model": model}

        model_dd.change(
            on_model,
            inputs=[model_dd, cfg_state],
            outputs=[cfg_state],
        )

        def _theme_js(name):
            return f"""() => {{
                var t = '{name}';
                var resolved = t === 'system'
                    ? (window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark') : t;
                document.documentElement.setAttribute('data-theme', resolved);
                localStorage.setItem('ai-agent-theme', t);
                document.querySelectorAll('.theme-btn button').forEach(function(b) {{
                    b.style.background = 'var(--bg-elevated)';
                    b.style.color = 'var(--text-muted)';
                    b.style.borderColor = 'var(--border)';
                }});
                var active = document.querySelector('.theme-btn-' + t + ' button');
                if (active) {{
                    active.style.background = 'var(--btn-primary)';
                    active.style.color = '#ffffff';
                    active.style.borderColor = 'var(--btn-primary)';
                }}
            }}"""

        theme_dark_btn.click(fn=None,   js=_theme_js("dark"))
        theme_light_btn.click(fn=None,  js=_theme_js("light"))
        theme_system_btn.click(fn=None, js=_theme_js("system"))

        # ── Exercise Tabs ──
        with gr.Tabs():
            with gr.Tab("01 · Simple Agent"):
                build_ex01_tab(cfg_state)
            with gr.Tab("02 · Memory & Persona"):
                build_ex02_tab(cfg_state)
            with gr.Tab("03 · Tool Use"):
                build_ex03_tab(cfg_state)
            with gr.Tab("04 · ReAct Loop"):
                build_ex04_tab(cfg_state)
            with gr.Tab("05 · Multi-Agent"):
                build_ex05_tab(cfg_state)
            with gr.Tab("06 · Streaming"):
                build_ex06_tab(cfg_state)
            with gr.Tab("07 · Structured Output"):
                build_ex07_tab(cfg_state)
            with gr.Tab("08 · RAG"):
                build_ex08_tab(cfg_state)

        gr.HTML("""
<div style="text-align:center; color:var(--text-faint); font-size:12px; padding:20px 0 8px 0; border-top:1px solid var(--border-muted); margin-top:16px;">
  AI Agent Learning Series &nbsp;·&nbsp; Simple → Memory → Tools → ReAct → Multi-Agent → Streaming → Structured → RAG &nbsp;·&nbsp;
  <a href="https://github.com/skalmodiya/ai-agent-learning" style="color:var(--accent-blue); text-decoration:none; font-weight:600;">GitHub ↗</a>
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
        js=f"() => {{ {THEME_JS} }}",
        css=CSS,
        theme=gr.themes.Base(
            primary_hue="blue",
            neutral_hue="slate",
            font=gr.themes.GoogleFont("Inter"),
        ),
    )
