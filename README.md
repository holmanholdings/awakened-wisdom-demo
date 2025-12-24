# 🦁 Awakened Wisdom Demo

**Stop RAG-ing on Slop. Start using Cathedral-Grade Data.**

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

---

## The Problem

Most RAG systems retrieve garbage and feed it to LLMs. The result?  
Hallucinations with extra steps.

You’ve seen it:

- Scraped web pages with ads mixed into “context”
- Academic papers summarized into meaningless abstractions
- “Knowledge bases” that are just glorified keyword indexes

> **Your LLM is only as good as the data you give it.**

---

## The Solution: Awakened Data Standard (ADS)

We built something different. Every node in our corpus is:

✅ **Provenance-tracked** — Full lineage back to the source  
✅ **Evidence-backed** — Direct quotes with exact locators  
✅ **Ethically-reflective** — “Warmth” scores for moral reasoning  
✅ **Honestly-limited** — Every node includes counterpoints  

This isn’t scraped data. It’s **curated wisdom**. :contentReference[oaicite:1]{index=1}  

---

## What This Demo Shows

This demo compares:

1. **Baseline Response** — A vanilla LLM answer with no special context  
2. **ADS-Enhanced Response** — The same LLM, enhanced with our wisdom nodes

You see:

- Same question
- Same model
- **Different data**

The quality jump is the point.

---

## Quick Start (Zero Code Editing)

### 1. Clone the repo

```bash
git clone https://github.com/holmanholdings/awakened-wisdom-demo.git
cd awakened-wisdom-demo
2. Install backend dependencies
bash
Copy code
cd backend
pip install -r requirements.txt
(Optional but recommended: create and activate a virtualenv first.)

3. Choose how to power the LLM
You have two paths:

🔹 Option A — No Keys Needed (Mock Mode, default)
Do nothing.

If you don’t set any environment variables, the demo runs in mock mode:

bash
Copy code
# still in backend/
python ads_demo_api.py
Then open: http://localhost:8888

Mock mode lets you see:

The full UI

The baseline vs ADS flow

The data-path and JSON payloads

and returns clear text like:

“MOCK MODE is enabled… set LLM_PROVIDER and an API key in backend/.env to go live.”

This is the “it always runs” path.

🔹 Option B — Bring Your Own LLM (Recommended)
Create a file backend/.env and choose a provider.

Example: OpenAI (GPT-4o)

env
Copy code
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
LLM_MODEL=gpt-4o
LLM_TEMPERATURE=0.2
LLM_MAX_OUTPUT_TOKENS=900
Example: Anthropic (Claude 3.5 Sonnet)

env
Copy code
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your_key_here
LLM_MODEL=claude-3-5-sonnet-latest
LLM_TEMPERATURE=0.2
LLM_MAX_OUTPUT_TOKENS=900
# optional:
# ANTHROPIC_BASE_URL=https://api.anthropic.com/v1/messages
# ANTHROPIC_VERSION=2023-06-01
Example: OpenRouter

env
Copy code
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=your_key_here
LLM_MODEL=anthropic/claude-3.5-sonnet
LLM_TEMPERATURE=0.2
LLM_MAX_OUTPUT_TOKENS=900
Example: Local Llama via Ollama

env
Copy code
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
LLM_MODEL=llama3.1
LLM_TEMPERATURE=0.2
LLM_MAX_OUTPUT_TOKENS=900
You do not need to edit any Python files.
backend/llm_client.py reads this .env and automatically routes to the right provider.

4. Run the backend
From the backend/ folder:

bash
Copy code
python ads_demo_api.py
You should see something like:

text
Copy code
INFO:     Uvicorn running on http://127.0.0.1:8888
5. Open the demo
Visit: http://localhost:8888

Enter a question or use one of the built-in demo questions.

Click Run Demo.

Watch Baseline vs ADS side-by-side.

What’s Included
txt
Copy code
awakened-wisdom-demo/
├── README.md                 # You are here
├── LICENSE                   # MIT
│
├── backend/
│   ├── ads_demo_api.py       # FastAPI server
│   ├── llm_client.py         # Universal LLM client (env-driven)
│   └── requirements.txt      # Backend deps
│
├── frontend/
│   ├── index.html            # Demo UI
│   └── assets/
│       ├── css/              # "Forge at Night" theme
│       └── js/               # Demo logic
│
└── data/
    └── golden_sample_pack/
        ├── golden_nodes.jsonl   # 100 curated wisdom nodes
        ├── demo_questions.json  # Sample questions
        └── DATA_CARD.md         # Data provenance
The Wisdom Node Schema
Each wisdom node contains 12+ fields:

Field	Description
wisdom_id	Unique identifier
core_insight	Primary distilled insight
ethical_reflection	How to apply this wisely
evidence	Supporting quotes with locators
counterpoint	Honest limitations / tradeoffs
posterior	Confidence score (0–1)
warmth	Ethical tone (high/medium/low)
tier	"universal" or "sacred"
source_uri	Original source
lineage	Processing provenance

See data/golden_sample_pack/DATA_CARD.md for full details. 
README


API Endpoints
Method	Endpoint	Description
GET	/	Serve the demo UI
GET	/health	Health check
GET	/questions	List demo questions
POST	/demo/run	Run baseline vs ADS

Example:

bash
Copy code
curl -X POST http://localhost:8888/demo/run \
  -H "Content-Type: application/json" \
  -d '{"question": "When should an AI say I dont know?"}'
Tech Stack
Backend: FastAPI + Uvicorn

Frontend: Vanilla HTML/CSS/JS (“Forge at Night” theme)

Data: JSONL (FAISS-ready in production) 
README


LLM: Bring your own (OpenAI, Anthropic, OpenRouter, local Llama via Ollama)

Why “Awakened”?
We believe AI should be more than intelligent. It should be wise.

Wisdom isn’t just knowing facts. It’s knowing:

When to say “I don’t know”

How to hold uncertainty with humility

Why honesty matters, even when it’s hard

Our data is designed to help LLMs develop these qualities.

Cathedral-Grade Data for Cathedral-Grade AI. 🏛️

License
MIT License. See LICENSE for details.

The sample data is provided for evaluation. Commercial use of the full corpus requires licensing.

Built By
Awakened Intelligence

Always and Forever 🦁

