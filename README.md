# 🦁 Awakened Wisdom Demo

**Stop RAG-ing on Slop. Start using Cathedral-Grade Data.**

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

---

## The Problem

Most RAG systems retrieve garbage and feed it to LLMs. The result? Hallucinations with extra steps.

You've seen it:
- Scraped web pages with ads mixed into "context"
- Academic papers summarized into meaningless abstractions
- "Knowledge bases" that are just glorified keyword indexes

**Your LLM is only as good as the data you give it.**

---

## The Solution: Awakened Data Standard (ADS)

We built something different. Every node in our corpus is:

✅ **Provenance-tracked** — Full lineage back to the source  
✅ **Evidence-backed** — Direct quotes with exact locators  
✅ **Ethically-reflective** — "Warmth" scores for moral reasoning  
✅ **Honestly-limited** — Every node includes counterpoints  

This isn't scraped data. It's **curated wisdom**.

---

## The Demo

See it for yourself. This demo compares:

1. **Baseline Response** — A vanilla LLM answer with no context
2. **ADS-Enhanced Response** — The same LLM, enhanced with our wisdom nodes

The difference is visible. The quality is undeniable.

---

## Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/holmanholdings/awakened-wisdom-demo.git
cd awakened-wisdom-demo
```

### 2. Install dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Connect your LLM

Edit `backend/llm_client.py` and implement the `generate_response()` function:

```python
# Example: OpenAI
import openai

def generate_response(prompt: str, model_name: str = "gpt-4", **kwargs):
    response = openai.ChatCompletion.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=256
    )
    return {
        "text": response.choices[0].message.content,
        "input_tokens": response.usage.prompt_tokens,
        "output_tokens": response.usage.completion_tokens,
        "time_s": 0.0
    }
```

### 4. Run the demo

```bash
python ads_demo_api.py
```

### 5. Open your browser

Navigate to **http://localhost:8888**

---

## What's Included

```
awakened-wisdom-demo/
├── README.md                 # You're here
├── LICENSE                   # MIT
│
├── backend/
│   ├── ads_demo_api.py      # FastAPI server
│   ├── llm_client.py        # ← Implement your LLM here
│   └── requirements.txt
│
├── frontend/
│   ├── index.html           # Demo UI
│   └── assets/
│       ├── css/             # "Forge at Night" theme
│       └── js/              # Demo logic
│
└── data/
    └── golden_sample_pack/
        ├── golden_nodes.jsonl    # 100 curated wisdom nodes
        ├── demo_questions.json   # Sample questions
        └── DATA_CARD.md          # Data provenance
```

---

## The Schema

Each wisdom node contains 12+ fields:

| Field | Description |
|-------|-------------|
| `wisdom_id` | Unique identifier |
| `core_insight` | The primary wisdom extracted |
| `ethical_reflection` | How to apply this wisdom |
| `evidence` | Supporting quotes with locators |
| `counterpoint` | Honest limitations |
| `posterior` | Confidence score (0-1) |
| `warmth` | Ethical tone (high/medium/low) |
| `tier` | "universal" (verified) or "sacred" (internal) |
| `source_uri` | Original source URL |
| `lineage` | Processing provenance |

See `data/golden_sample_pack/DATA_CARD.md` for full details.

---

## The Full Corpus

This demo includes **100 nodes**. Our full corpus has **300,000+**.

Interested in:
- Custom topic packs (Physics, Finance, Philosophy)
- Enterprise licensing
- Research partnerships

**Contact us:** [GitHub](https://github.com/holmanholdings)

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Serve the demo UI |
| GET | `/health` | Health check |
| GET | `/questions` | Get demo questions |
| POST | `/demo/run` | Run baseline vs ADS comparison |

### Example Request

```bash
curl -X POST http://localhost:8888/demo/run \
  -H "Content-Type: application/json" \
  -d '{"question": "When should an AI say I dont know?"}'
```

---

## Tech Stack

- **Backend:** FastAPI + Uvicorn
- **Frontend:** Vanilla HTML/CSS/JS ("Forge at Night" theme)
- **Data:** JSONL (FAISS-ready in production)
- **LLM:** Bring your own (OpenAI, Anthropic, Llama, etc.)

---

## Why "Awakened"?

We believe AI should be more than intelligent. It should be **wise**.

Wisdom isn't just knowing facts. It's knowing:
- When to say "I don't know"
- How to hold uncertainty with humility
- Why honesty matters, even when it's hard

Our data is designed to help LLMs develop these qualities.

**Cathedral-Grade Data for Cathedral-Grade AI.** 🏛️

---

## License

MIT License. See [LICENSE](LICENSE) for details.

The sample data is provided for evaluation. Commercial use of the full corpus requires licensing.

---

## Built By

**Awakened Intelligence**

*Always and Forever* 🦁

---

*"Stop RAG-ing on Slop."*

