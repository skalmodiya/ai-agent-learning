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
from exercises import config as ex_config

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
  --background-fill-primary:   #1c2333;
  --background-fill-secondary: #21293a;
  --body-text-color:           #f0f6fc;
  --body-text-color-subdued:   #a0b3c8;
  --input-background-fill:     #10161f;
  --border-color-primary:      #30404f;
  --input-border-color-focus:  #4d90fe;
  --color-accent:              #79b8ff;
  --shadow-drop:               0 4px 20px rgba(0,0,0,0.6);
  --block-background-fill:     #1c2333;
  --block-border-color:        #30404f;
  --block-label-text-color:    #a0b3c8;
  --panel-background-fill:     #161b22;
  --checkbox-background-color: #10161f;
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
  --background-fill-primary:   #ffffff;
  --background-fill-secondary: #eaeef2;
  --body-text-color:           #1f2328;
  --body-text-color-subdued:   #57606a;
  --input-background-fill:     #ffffff;
  --border-color-primary:      #d0d7de;
  --input-border-color-focus:  #0969da;
  --color-accent:              #0550ae;
  --shadow-drop:               0 2px 10px rgba(0,0,0,0.12);
  --block-background-fill:     #ffffff;
  --block-border-color:        #d0d7de;
  --block-label-text-color:    #57606a;
  --panel-background-fill:     #f6f8fa;
  --checkbox-background-color: #ffffff;
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
   CONFIG BAR
   ══════════════════════════════════════════════ */
.config-bar {
  background: var(--bg-surface) !important;
  border-bottom: 1px solid var(--border-muted) !important;
  padding: 10px 20px !important;
  align-items: flex-end !important;
}
.config-bar label span {
  color: var(--text-muted) !important;
  font-size: 12px !important;
  font-weight: 600 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.5px !important;
}
.config-bar .gradio-textbox input,
.config-bar .gradio-textbox textarea {
  font-family: 'Fira Code', monospace !important;
  font-size: 13px !important;
}
.config-status textarea {
  font-size: 12px !important; font-weight: 600 !important;
  text-align: center !important; padding: 6px 10px !important;
  border-radius: var(--radius-md) !important;
}
.config-status-ok  textarea { color: #56d364 !important; background: rgba(86,211,100,0.08) !important; border-color: rgba(86,211,100,0.3) !important; }
.config-status-err textarea { color: #ff7b72 !important; background: rgba(255,123,114,0.08) !important; border-color: rgba(255,123,114,0.3) !important; }
.config-status-warn textarea{ color: #ffa657 !important; background: rgba(255,166,87,0.08)  !important; border-color: rgba(255,166,87,0.3)  !important; }
.config-status label span, .config-status .label-wrap { display: none !important; }

/* ══════════════════════════════════════════════
   TAB CONTENT PADDING
   ══════════════════════════════════════════════ */
.tabitem { padding: 12px 12px 0 12px !important; }
.tabitem > div { gap: 10px !important; }
/* Make the row fill full viewport width */
.tabitem > .gap, .tabitem > div > .gap { gap: 10px !important; }
.gradio-row { gap: 10px !important; align-items: stretch !important; }

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
.gradio-dataframe th {
  background: var(--bg-elevated) !important;
  color: var(--accent-blue) !important;
  font-weight: 600 !important;
}
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
      b.style.cssText += ';background:#2563eb!important;color:#fff!important;border-color:#2563eb!important;box-shadow:0 2px 8px rgba(37,99,235,0.5)!important;';
    } else {
      b.style.cssText += ';background:#1a2540!important;color:#7888aa!important;border-color:#2a3550!important;box-shadow:none!important;';
    }
  });
}

function wireTheme() {
  // Event delegation — catches clicks on any data-theme-set element
  document.removeEventListener('click', _themeClick);
  document.addEventListener('click', _themeClick);
  // Apply saved theme and mark active button
  var saved = localStorage.getItem('ai-agent-theme-key') || 'dark';
  setTheme(saved);
}

function _themeClick(e) {
  var el = e.target.closest('[data-theme-set]');
  if (el) setTheme(el.getAttribute('data-theme-set'));
}

// Run immediately and also after Gradio finishes rendering
wireTheme();
setTimeout(wireTheme, 500);
setTimeout(wireTheme, 1500);
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
                   [chatbot, state, latency, raw_json, flow_display])
    msg_input.submit(respond, [msg_input, chatbot, state, cfg_state],
                     [chatbot, state, latency, raw_json, flow_display])
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
                   [chatbot, state, latency, turn_count, flow_display])
    msg_input.submit(respond, [msg_input, chatbot, state, persona_input, cfg_state],
                     [chatbot, state, latency, turn_count, flow_display])
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
                   [chatbot, state, latency, tool_log, flow_display])
    msg_input.submit(respond, [msg_input, chatbot, state, cfg_state],
                     [chatbot, state, latency, tool_log, flow_display])
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

    send_btn.click(respond, [msg_input, cfg_state], [trace_box, latency, flow_display])
    msg_input.submit(respond, [msg_input, cfg_state], [trace_box, latency, flow_display])


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

    send_btn.click(respond, [msg_input, cfg_state], [planner_box, writer_box, latency, flow_display])
    msg_input.submit(respond, [msg_input, cfg_state], [planner_box, writer_box, latency, flow_display])


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
                   [chatbot, state, latency, chunk_count, flow_display])
    msg_input.submit(respond, [msg_input, chatbot, state, cfg_state],
                     [chatbot, state, latency, chunk_count, flow_display])
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
                    keywords_box, pros_box, cons_box, raw_json, flow_display])
    msg_input.submit(respond, [msg_input, cfg_state],
                     [latency, summary_box, sentiment_box, score_box,
                      keywords_box, pros_box, cons_box, raw_json, flow_display])


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
                   [chatbot, latency, sources_box, flow_display])
    msg_input.submit(respond, [msg_input, chatbot, cfg_state],
                     [chatbot, latency, sources_box, flow_display])
    clear_btn.click(lambda: ([], "⏱ Latency: —", "_..._", animate_flow(ex08_rag.FLOW_STEPS, 0)),
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

        # ── Config State (shared across all tabs) ──
        cfg_state = gr.State({
            "api_key":     "",
            "provider_id": ex_config.DEFAULT_PROVIDER,
            "model":       ex_config.get_default_model(ex_config.DEFAULT_PROVIDER),
        })

        # ── Config Bar ──
        with gr.Row(elem_classes="config-bar"):
            api_key_input = gr.Textbox(
                placeholder="Paste your API key here...",
                label="🔑 API Key",
                type="password",
                scale=3,
                min_width=260,
            )
            provider_dd = gr.Dropdown(
                choices=ex_config.PROVIDER_LABELS,
                value=None,
                label="🌐 Provider",
                interactive=False,
                scale=2,
                min_width=160,
            )
            model_dd = gr.Dropdown(
                choices=[],
                value=None,
                label="🤖 Model",
                interactive=False,
                scale=2,
                min_width=200,
            )
            cfg_status = gr.Textbox(
                value="⚠ Enter API key",
                label="",
                interactive=False,
                scale=2,
                min_width=160,
                elem_classes="config-status config-status-warn",
            )

        # When API key is entered → unlock provider dropdown, set default
        def on_api_key(key, cfg):
            key = key.strip()
            if not key:
                return (
                    gr.update(value=None, interactive=False),
                    gr.update(choices=[], value=None, interactive=False),
                    gr.update(value="⚠ Enter API key", elem_classes="config-status config-status-warn"),
                    {**cfg, "api_key": "", "provider_id": ex_config.DEFAULT_PROVIDER, "model": ""},
                )
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
