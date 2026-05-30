"""
Exercise 08 - RAG (Retrieval-Augmented Generation)
====================================================
New concept: retrieve relevant documents and inject them into the prompt
so the agent answers from YOUR data.
"""

import sys, os, textwrap, requests

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def _check_venv():
    inside = (hasattr(sys, "real_prefix") or
              (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix))
    if not inside:
        print("\n  ERROR: No virtual environment detected.")
        print("  python -m venv venv && venv\\Scripts\\activate\n"); sys.exit(1)
_check_venv()

API_KEY  = "a6eb413e-5c42-4420-87c0-f59b2a4e5a84"
BASE_URL = "http://localhost:6655/anthropic/v1"
MODEL    = "claude-sonnet-4-6"
HEADERS  = {"x-api-key": API_KEY, "content-type": "application/json", "anthropic-version": "2023-06-01"}

try:
    TERM_WIDTH = min(os.get_terminal_size().columns, 80)
except OSError:
    TERM_WIDTH = 80

DOCUMENTS = [
    {"id":"doc1","title":"Leave Policy","content":
     "Employees get 20 days annual leave. Approval needed 2 weeks in advance. "
     "Max 5 carry-over days. Sick leave needs certificate after 3 days."},
    {"id":"doc2","title":"Remote Work","content":
     "Up to 3 remote days/week. Core hours 10am–3pm. "
     "Stable internet required. Agreed with team lead."},
    {"id":"doc3","title":"Expenses","content":
     "Under $50: no approval needed. Over $50: manager pre-approval. "
     "Submit within 30 days with receipts. Travel at economy rates."},
    {"id":"doc4","title":"AI Tools Policy","content":
     "Use approved AI tools only. No confidential data in public AI. "
     "Review AI output before external use. Internal AI: ai.internal.company.com"},
]

def retrieve(query, top_k=2):
    words = set(query.lower().split())
    scored = sorted(DOCUMENTS, key=lambda d: len(words & set((d["title"]+" "+d["content"]).lower().split())), reverse=True)
    return scored[:top_k]

def print_banner():
    b = "─" * TERM_WIDTH
    print(f"\n{b}")
    print("  Exercise 08 — RAG".center(TERM_WIDTH))
    print("  Agent answers from your documents, not training data".center(TERM_WIDTH))
    print(b)
    print("  Sample questions:")
    print("    'How many leave days do I get?'")
    print("    'Can I work from home every day?'")
    print("    'How do I claim a $200 expense?'")
    print(b + "\n")

def print_answer(reply, sources):
    b = "─" * TERM_WIDTH
    print(f"\n  \033[90mSources used: {', '.join(sources)}\033[0m")
    print(b + "\n  Agent\n  " + "┄"*(TERM_WIDTH-4))
    for para in reply.strip().split("\n"):
        if not para.strip(): print()
        else:
            for l in textwrap.wrap(para, TERM_WIDTH-4) or [para]: print(f"  {l}")
    print(b + "\n")

def print_error(msg): print(f"\n  ✖  {msg}\n")

def ask_agent(question):
    docs = retrieve(question)
    context = "\n\n".join(f"[{d['title']}]\n{d['content']}" for d in docs)
    prompt = (f"Answer ONLY from the documents below. If not covered, say so.\n\n"
              f"--- DOCUMENTS ---\n{context}\n--- END ---\n\nQuestion: {question}")
    payload = {"model": MODEL, "max_tokens": 1024,
               "messages": [{"role":"user","content":prompt}]}
    r = requests.post(f"{BASE_URL}/messages", headers=HEADERS, json=payload)
    r.raise_for_status()
    return r.json()["content"][0]["text"], [d["title"] for d in docs]

def main():
    print_banner()
    try:
        while True:
            question = input("  › ").strip()
            if not question: continue
            if question.lower() in ("quit","exit","q"):
                print(f"\n{'Goodbye!':^{TERM_WIDTH}}\n"); break
            try:
                reply, sources = ask_agent(question)
                print_answer(reply, sources)
            except requests.exceptions.ConnectionError:
                print_error("Cannot reach API.")
            except requests.exceptions.HTTPError as e:
                print_error(f"API error: {e}")
    except KeyboardInterrupt:
        print("\n\n  Interrupted. Goodbye!\n")

if __name__ == "__main__":
    main()
