# Exercise 08 — RAG (Retrieval-Augmented Generation)

## What's New vs Exercise 07

The agent answers from **your own documents**, not its training data.

## The RAG Pipeline

```
1. User asks a question
       ↓
2. Search your document store for relevant chunks
       ↓
3. Inject those chunks into the prompt as context
       ↓
4. AI answers based on the provided context
```

## Why Not Just Train the Model?

- Training costs $$$ and weeks of time
- Your data changes — RAG updates instantly
- RAG is transparent — you can see exactly what context was used
- RAG reduces hallucinations by grounding answers in real documents

## Document Store (in this exercise)

We simulate 4 company policy documents in memory:
- Leave Policy
- Remote Work Guidelines
- Expense Reimbursement Policy
- AI Tools Usage Policy

## Key Concepts

| Term | Meaning |
|---|---|
| **Retrieval** | Finding relevant documents from a store |
| **Augmented** | Prompt enhanced with retrieved documents |
| **Generation** | AI generates answer from augmented prompt |
| **Chunk** | A small piece of a larger document |
| **Vector DB** | Real systems use Pinecone/Chroma for semantic search |

## How to Run

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python agent.py
```

## Try It

- "How many leave days do I get?"
- "Can I work from home every day?"
- "How do I claim a $200 expense?"
- "Can I use ChatGPT for work?"

## You've Completed the Series!

You've now covered the full AI Agent learning arc:
01 Simple → 02 Memory → 03 Tools → 04 ReAct → 05 Multi-Agent → 06 Streaming → 07 Structured → 08 RAG
