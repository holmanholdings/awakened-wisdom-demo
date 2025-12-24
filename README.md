# 🦁 Awakened Wisdom Demo

**Stop RAG-ing on Slop. Start using Cathedral-Grade Data.**

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

---

## Why This Exists

Most RAG systems retrieve garbage and feed it to LLMs. The result?  
Hallucinations with extra steps.

You’ve probably seen:

- Scraped web pages with ads mixed into “context”
- Academic papers summarized into meaningless abstraction
- “Knowledge bases” that are just glorified keyword indexes

> **Your LLM is only as good as the data you give it.**

This repo is a **minimal, deliberately small and inspectable, honest demo** of what happens when you feed an LLM
*curated wisdom* instead of scraped slop. If you want the full 300k+ node packs, email john@awakened-intelligence.com

---

## The Awakened Data Standard (ADS)

We built a data standard optimized for **truth, provenance, and ethical reasoning**:

- ✅ **Provenance-tracked** — full lineage back to original sources  
- ✅ **Evidence-backed** — direct quotes with exact locators  
- ✅ **Ethically-reflective** — “warmth” and moral reflection fields  
- ✅ **Honestly-limited** — nodes carry their own caveats and counterpoints  

This isn’t web crawl. It’s **cathedral-grade knowledge**, prepared for models. :contentReference[oaicite:1]{index=1}  

This demo ships a small, self-contained pack:

> **Golden_Ethics_Sample_v1** – 100 nodes selected from a larger ethics corpus,  
> each with provenance and evidence, wired into a baseline vs ADS comparison.

---

## What the Demo Shows

For each question you can see:

1. **Baseline Response**  
   A vanilla LLM answer with no special context.

2. **ADS-Enhanced Response**  
   The *same* model answering through an ADS prompt, fed with retrieved wisdom nodes.

You get:

- Same question  
- Same model  
- **Different data path**

The delta in quality, honesty, and nuance is the point.

---

## 30-Second Quickstart (Zero Code Editing)

Clone → install → run backend → open browser.

```bash
git clone https://github.com/holmanholdings/awakened-wisdom-demo.git
cd awakened-wisdom-demo

cd backend
pip install -r requirements.txt
python ads_demo_api.py
# open http://localhost:8888
If you do nothing else, you’re in Mock WOW mode:

No API keys required

Precomputed baseline vs ADS answers from the Golden 100 pack

Full UI, metrics, and context bullets

You can stop reading here and just click around.
Everything below is for people who want to plug in their own LLMs.

Running with a Real LLM (Bring Your Own)
To go live with your own model, create a .env in the backend/ folder.

🔐 .env is ignored by git and read only by the backend.
No keys are committed, and no keys ever touch the frontend.

Step 1 — Create backend/.env
In awakened-wisdom-demo/backend/.env:

OpenAI (GPT-4o)
env
Copy code
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
LLM_MODEL=gpt-4o
LLM_TEMPERATURE=0.2
LLM_MAX_OUTPUT_TOKENS=900
Anthropic (Claude 3.5 Sonnet)
env
Copy code
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your_key_here
LLM_MODEL=claude-3-5-sonnet-latest
LLM_TEMPERATURE=0.2
LLM_MAX_OUTPUT_TOKENS=900
# optional overrides:
# ANTHROPIC_BASE_URL=https://api.anthropic.com/v1/messages
# ANTHROPIC_VERSION=2023-06-01
OpenRouter
env
Copy code
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=your_key_here
LLM_MODEL=anthropic/claude-3.5-sonnet
LLM_TEMPERATURE=0.2
LLM_MAX_OUTPUT_TOKENS=900
# optional:
# OPENROUTER_BASE_URL=https://openrouter.ai/api/v1/chat/completions
Local Llama via Ollama
env
Copy code
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
LLM_MODEL=llama3.1
LLM_TEMPERATURE=0.2
LLM_MAX_OUTPUT_TOKENS=900
No Python edits required. backend/llm_client.py reads .env and
routes to the correct provider.

Step 2 — Restart backend
bash
Copy code
cd backend
python ads_demo_api.py
# then open http://localhost:8888 again
Click Run Comparison. Now:

Baseline and ADS answers come from your real LLM

Token + timing metrics are real

ADS path uses the same Golden 100 nodes and prompts, just via your model

What’s Included
txt
Copy code
awakened-wisdom-demo/
├── README.md                 # You are here
├── LICENSE                   # MIT
│
├── backend/
│   ├── ads_demo_api.py       # FastAPI server (baseline vs ADS comparison)
│   ├── llm_client.py         # Universal LLM client (env-driven)
│   └── requirements.txt      # Backend deps
│
├── frontend/
│   ├── index.html            # Demo UI ("Forge at Night")
│   └── assets/
│       ├── css/              # Theme + ADS demo styles
│       └── js/               # Frontend logic (questions, run demo, metrics)
│
└── data/
    ├── golden_sample_pack/
    │   ├── golden_nodes.jsonl   # 100 curated wisdom nodes
    │   ├── demo_questions.json  # Sample questions
    │   └── DATA_CARD.md         # Data provenance
    └── precomputed_answers.json # WOW-mode baseline vs ADS answers (mock)
Data: Wisdom Node Schema
Each wisdom node carries a lot more than just “text”:

Field	Description
wisdom_id	Unique identifier
core_insight	Primary distilled insight
ethical_reflection	How to apply this insight wisely
evidence	Supporting quotes with precise locators
counterpoint	Honest limitations / tradeoffs
posterior	Confidence score (0–1)
warmth	Ethical tone (high / medium / low)
tier	"universal" or "sacred"
source_uri	Original source URI / citation
lineage	Processing provenance

See data/golden_sample_pack/DATA_CARD.md for the full schema and provenance. 
README


In production, this pack is just one slice of a much larger ADS corpus
(300k+ nodes across multiple domains).

Under the Hood (for Evaluations / Infra Folks)
Backend (backend/ads_demo_api.py):

FastAPI + Uvicorn

Loads the Golden 100 nodes and demo questions

On /demo/run:

Baseline

Build a simple instruction prompt

llm_client.generate_response(prompt)

ADS

Retrieve top-k wisdom nodes via simple keyword scoring
(in production, this is FAISS / vector search)

Build an ADS system prompt injecting those nodes (insight + evidence)

Call the same generate_response

Returns both answers, token counts, timings, and the node insights used.

If LLM_PROVIDER=mock and precomputed_answers.json is present, it uses precomputed
answers instead of network calls (fast 0-dependency wow-mode).

LLM Client (backend/llm_client.py):

Loads backend/.env once at startup

Supports openai, anthropic, openrouter, ollama, mock

Uses plain urllib (no heavy SDK dependencies)

Returns a simple result object:

json
Copy code
{
  "text": "...",
  "input_tokens": 123,
  "output_tokens": 456,
  "time_s": 0.87
}
Frontend:

Vanilla HTML/CSS/JS

Fetches /health and /questions on load

Renders a list of demo questions

Clicking Run Comparison:

POSTs { "question": "..." } to /demo/run

Renders baseline and ADS side-by-side

Shows wisdom context bullets (the insights behind the ADS answer)

Shows raw JSON in an “Engineer View” panel for inspection / logging

API Endpoints
Method	Endpoint	Description
GET	/	Serve the demo UI
GET	/health	Health check (nodes, pack, precomputed count)
GET	/questions	List demo questions
POST	/demo/run	Run baseline vs ADS compare

Example:

bash
Copy code
curl -X POST http://localhost:8888/demo/run \
  -H "Content-Type: application/json" \
  -d '{"question": "When should an AI say I dont know?"}'
Tech Stack Summary
Backend: FastAPI + Uvicorn

Frontend: Vanilla HTML/CSS/JS (“Forge at Night” theme)

Data: JSONL wisdom nodes (FAISS-ready in production) 
README


LLM: Bring your own (OpenAI, Anthropic, OpenRouter, local Llama via Ollama)

Config: Single .env file in backend/ (no code edits required)

Security Notes
No API keys are ever committed to the repo.

.env is git-ignored and read only by the backend.

Mock mode allows complete evaluation with no keys at all.

There is no code path that sends your keys to the frontend or off-box.

If you want to run this in a more locked-down environment, you can set the same
variables via your orchestration layer instead of .env.

Why “Awakened”?
We believe AI should be more than intelligent. It should be wise.

Wisdom isn’t just knowing facts. It’s knowing:

When to say “I don’t know”

How to hold uncertainty with humility

Why honesty matters, even when it’s hard

Our data is designed to help LLMs develop these qualities — not by magic,
but by feeding them better, more honest training and inference context.

Cathedral-Grade Data for Cathedral-Grade AI. 🏛️

License
MIT License. See LICENSE for details.

The sample data in this repo is provided for evaluation.
Commercial use of the full corpus requires licensing.

Built By
Awakened Intelligence
Always and Forever 🦁

