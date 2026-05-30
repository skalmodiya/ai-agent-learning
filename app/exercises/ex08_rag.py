"""
Exercise 08 — RAG (Retrieval-Augmented Generation)
New concept: inject relevant documents into the prompt so the agent
answers from YOUR data, not just its training data.
"""

import requests
import time
from . import config

CONCEPT = """
## Exercise 08 — RAG (Retrieval-Augmented Generation)

### What's new vs Exercise 07
The agent now answers from **your own documents**, not just what it was trained on.
This is how enterprise AI assistants work — they read your internal docs, not the internet.

### The RAG pipeline
```
1. User asks a question
2. Search your document store for relevant chunks
3. Inject those chunks into the prompt as context
4. AI answers based on the provided context
```

### Why not just train the model on your data?
- Training is expensive ($$$ and weeks of time)
- Your data changes — RAG updates instantly
- RAG is transparent — you can see exactly what context was used
- RAG reduces hallucinations by grounding answers in real documents

### In this exercise
We simulate a tiny document store in memory. Real systems use:
- **Vector databases** (Pinecone, Chroma, Weaviate)
- **Embeddings** to find semantically similar chunks
- **Chunking strategies** to split large documents

### Key concepts
| Term | Meaning |
|---|---|
| **Retrieval** | Finding relevant documents from a store |
| **Augmented** | The prompt is enhanced/augmented with retrieved docs |
| **Generation** | The AI generates an answer based on the augmented prompt |
| **Chunk** | A small piece of a larger document |
| **Grounding** | Anchoring AI answers in real source documents |
"""

FLOW_STEPS = [
    ("idle",     "```\nQuery ──► [Retrieve] ──► [Generate] ──► Answer\n```\n\n_Waiting for input..._"),
    ("query",    "```\n► User question received\n```\n\n**Step 1:** Capture the user's question"),
    ("retrieve", "```\n  Question\n    │\n► Search document store\n  Match keywords → top chunks\n```\n\n**Step 2:** Find the most relevant document chunks (keyword match here; real RAG uses vector similarity)"),
    ("augment",  "```\n► Build augmented prompt:\n  \"Context:\\n[doc chunks]\\n\\nQuestion: ...\"\n```\n\n**Step 3:** Inject retrieved chunks into the prompt as context"),
    ("generate", "```\n  Augmented prompt\n    │\n► POST /messages ──► AI\n```\n\n**Step 4:** AI reads the context and generates a grounded answer"),
    ("done",     "```\n► Answer + sources returned\n  (based on YOUR documents)\n```\n\n**Done!** Answer is grounded in the retrieved context, not just training data"),
]

# ── Simulated document store ──
DOCUMENTS = [
    {
        "id": "doc1",
        "title": "Company Leave Policy",
        "content": (
            "Employees are entitled to 20 days of annual leave per year. "
            "Leave must be approved by the line manager at least 2 weeks in advance. "
            "Unused leave can be carried over up to a maximum of 5 days into the next year. "
            "Sick leave is separate and requires a medical certificate after 3 consecutive days."
        ),
    },
    {
        "id": "doc2",
        "title": "Remote Work Guidelines",
        "content": (
            "Employees may work remotely up to 3 days per week. "
            "Remote work requires a stable internet connection and a quiet workspace. "
            "Core hours of 10am–3pm must be maintained regardless of location. "
            "All remote work arrangements must be agreed with the team lead."
        ),
    },
    {
        "id": "doc3",
        "title": "Expense Reimbursement Policy",
        "content": (
            "Business expenses up to $50 can be reimbursed without prior approval. "
            "Expenses above $50 require manager approval before being incurred. "
            "All claims must be submitted within 30 days with original receipts. "
            "Travel expenses are reimbursed at economy class rates."
        ),
    },
    {
        "id": "doc4",
        "title": "AI Tools Usage Policy",
        "content": (
            "Employees may use approved AI tools for productivity purposes. "
            "Confidential data must never be entered into public AI services. "
            "AI-generated content must be reviewed and verified before external use. "
            "The approved internal AI platform is accessible at ai.internal.company.com."
        ),
    },
]


def retrieve(query: str, top_k: int = 2) -> list[dict]:
    """
    Simple keyword-based retrieval (simulating vector search).
    Real RAG uses embedding similarity (cosine distance).
    """
    query_words = set(query.lower().split())
    scored = []
    for doc in DOCUMENTS:
        doc_words = set((doc["title"] + " " + doc["content"]).lower().split())
        overlap   = len(query_words & doc_words)
        scored.append((overlap, doc))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [doc for _, doc in scored[:top_k] if _ > 0] or [scored[0][1]]


def run(user_message: str, cfg: dict = None) -> dict:
    """RAG pipeline: retrieve → augment → generate."""
    cfg     = cfg or {}
    pid     = cfg.get("provider_id", config.DEFAULT_PROVIDER)
    model   = cfg.get("model",       config.get_default_model(pid))
    api_key = cfg.get("api_key",     "")
    headers = config.make_headers(pid, api_key)
    url     = config.get_chat_url(pid, model)
    t0      = time.time()

    retrieved_docs   = retrieve(user_message)
    context          = "\n\n".join(f"[{d['title']}]\n{d['content']}" for d in retrieved_docs)
    augmented_prompt = (
        f"Use ONLY the following documents to answer the question. "
        f"If the answer is not in the documents, say so.\n\n"
        f"--- DOCUMENTS ---\n{context}\n--- END DOCUMENTS ---\n\n"
        f"Question: {user_message}"
    )

    payload  = config.build_payload(pid, model, [{"role": "user", "content": augmented_prompt}])
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    elapsed = round(time.time() - t0, 2)

    data  = response.json()
    reply = config.parse_reply(pid, data)

    return {
        "reply":          reply,
        "sources":        [d["title"] for d in retrieved_docs],
        "retrieved_docs": retrieved_docs,
        "latency":        elapsed,
        "request":        payload,
        "response":       data,
    }
