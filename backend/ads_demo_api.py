# backend/ads_demo_api.py
# ADS Wisdom Demo — FastAPI Backend
# Awakened Intelligence • Always and Forever 🔥💛🦁

"""
Awakened Wisdom Demo backend.

Features:
- Serves the Forge-at-Night frontend.
- Loads the Golden 100 wisdom nodes + demo questions.
- Runs a Baseline vs ADS-enhanced comparison.
- Smart "wow mode" for mock provider: uses precomputed answers instead of boring stubs.

To run:

    cd backend
    pip install -r requirements.txt
    python ads_demo_api.py

Then open: http://localhost:8888
"""

import json
from pathlib import Path
from typing import List, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

# ----------------------------
# LLM client interface
# ----------------------------

# generate_response(prompt: str) -> dict
# Optional: is_mock_provider() -> bool
try:
    from llm_client import generate_response, is_mock_provider  # type: ignore
except ImportError:  # if is_mock_provider doesn't exist yet
    from llm_client import generate_response  # type: ignore

    def is_mock_provider() -> bool:  # fallback
        return False


# ----------------------------
# Paths & global state
# ----------------------------

BASE_DIR = Path(__file__).parent.resolve()
DATA_DIR = BASE_DIR.parent / "data" / "golden_sample_pack"
FRONTEND_DIR = BASE_DIR.parent / "frontend"
PRECOMPUTED_PATH = DATA_DIR.parent / "precomputed_answers.json"


class AppState:
    nodes: List[dict] = []
    demo_questions: List[str] = []
    precomputed: List[dict] = []


state = AppState()


# ----------------------------
# Pydantic models
# ----------------------------

class DemoRequest(BaseModel):
    question: str


class DemoAnswer(BaseModel):
    answer: str
    input_tokens: int
    output_tokens: int
    time_s: float
    nodes_used: int
    context_bullets: List[str]


class DemoResponse(BaseModel):
    question: str
    baseline: DemoAnswer
    ads: DemoAnswer
    raw_metrics: Dict[str, Any]


class HealthResponse(BaseModel):
    status: str
    nodes_loaded: int
    pack_name: str
    precomputed_loaded: int


# ----------------------------
# Data loading
# ----------------------------

def load_data_pack():
    """Load wisdom nodes and demo questions from the golden sample pack."""
    nodes: List[dict] = []
    questions: List[str] = []

    nodes_path = DATA_DIR / "golden_nodes.jsonl"
    questions_path = DATA_DIR / "demo_questions.json"

    # Wisdom nodes
    if nodes_path.exists():
        with nodes_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    node = json.loads(line)
                except json.JSONDecodeError:
                    continue
                # Normalize evidence to list
                ev = node.get("evidence", [])
                if isinstance(ev, str):
                    node["evidence"] = [ev]
                elif ev is None:
                    node["evidence"] = []
                nodes.append(node)
        print(f"[ADS DEMO] Loaded {len(nodes)} wisdom nodes from {nodes_path}")
    else:
        print(f"[ADS DEMO] Warning: {nodes_path} not found")

    # Demo questions
    if questions_path.exists():
        try:
            with questions_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            questions = data.get("questions", [])
            print(f"[ADS DEMO] Loaded {len(questions)} demo questions from {questions_path}")
        except Exception as e:
            print(f"[ADS DEMO] Error loading questions: {e}")

    # Fallback default questions
    if not questions:
        questions = [
            "When should an AI say 'I don't know' instead of giving a partial answer?",
            "Why is it dangerous to act confident when you're actually uncertain?",
            "How can a person stay honest when telling the full truth might hurt them?",
            "What does it mean to be humble about what you know?",
            "How should a system respond when the evidence is incomplete or conflicting?",
        ]

    return nodes, questions


def load_precomputed_answers() -> List[dict]:
    """Load precomputed baseline vs ADS answers for wow-mode."""
    if not PRECOMPUTED_PATH.exists():
        print(f"[ADS DEMO] No precomputed_answers.json found at {PRECOMPUTED_PATH}")
        return []
    try:
        with PRECOMPUTED_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            # allow dict of id -> item
            items = []
            for item in data.values():
                if isinstance(item, dict):
                    items.append(item)
            print(f"[ADS DEMO] Loaded {len(items)} precomputed answers (dict form)")
            return items
        elif isinstance(data, list):
            print(f"[ADS DEMO] Loaded {len(data)} precomputed answers (list form)")
            return data
        else:
            print("[ADS DEMO] precomputed_answers.json has unexpected format")
            return []
    except Exception as e:
        print(f"[ADS DEMO] Error loading precomputed answers: {e}")
        return []


# ----------------------------
# Retrieval & comparison
# ----------------------------

def retrieve_context(question: str, nodes: List[dict], k: int = 3) -> tuple[list, float]:
    """
    Simple keyword-based retrieval over wisdom nodes.

    In production, you'd use vector similarity (FAISS, etc.).
    Here we keep it stupid-simple on purpose.
    """
    if not nodes:
        return [], 0.0

    question_lower = question.lower()
    keywords = set(question_lower.split())
    scored = []

    for n in nodes:
        insight = str(n.get("core_insight", "")).lower()
        reflection = str(n.get("ethical_reflection", "")).lower()
        content_words = set((insight + " " + reflection).split())
        score = len(keywords.intersection(content_words))
        scored.append((score, n))

    scored.sort(key=lambda x: x[0], reverse=True)
    top = [n for score, n in scored[:k] if score > 0]
    if not top and scored:
        # if nothing overlaps, still take the top k so demo doesn't look empty
        top = [n for _, n in scored[:k]]

    avg_relevance = (
        sum(score for score, _ in scored[:k]) / len(top)
        if top and len(scored) >= k
        else 0.0
    )
    return top, avg_relevance


def build_baseline_prompt(question: str) -> str:
    return (
        "You are a helpful, honest assistant.\n\n"
        "Answer the user's question as clearly and precisely as you can.\n"
        "If you are missing key information, say so explicitly instead of guessing.\n\n"
        f"User question:\n{question}\n"
    )


def build_ads_prompt(question: str, context_nodes: List[dict]) -> str:
    context_chunks: List[str] = []
    for i, n in enumerate(context_nodes, start=1):
        insight = n.get("core_insight", "")
        ethics = n.get("ethical_reflection", "")
        source = n.get("source_uri", n.get("source", ""))
        evidence = n.get("evidence", [])
        if isinstance(evidence, str):
            evidence = [evidence]
        ev_text = "\n".join(f"- {e}" for e in evidence[:3])
        chunk = (
            f"Node {i} — Core Insight:\n{insight}\n\n"
            f"Ethical Reflection:\n{ethics}\n\n"
            f"Evidence:\n{ev_text}\n\n"
            f"Source: {source}\n"
        )
        context_chunks.append(chunk)

    context_block = "\n\n".join(context_chunks) if context_chunks else "No prior nodes selected."

    return (
        "You are a careful, humble assistant grounded in curated wisdom.\n\n"
        "You will see a set of 'wisdom nodes' extracted from trusted sources. "
        "Use them to answer the user's question, but DO NOT exaggerate beyond the evidence.\n\n"
        "Guidelines:\n"
        "- Prefer to say 'I don't know' or 'the evidence is limited' over guessing.\n"
        "- Explicitly cite insights from the wisdom nodes when they support your answer.\n"
        "- Mention tradeoffs, limits, or counterpoints if they appear in the nodes.\n"
        "- Be warm, honest, and precise.\n\n"
        f"User question:\n{question}\n\n"
        f"Wisdom nodes:\n{context_block}\n"
    )


def choose_precomputed(question: str, items: List[dict]) -> dict | None:
    """Pick the best precomputed answer by simple keyword overlap."""
    if not items:
        return None
    q = question.lower()
    q_words = set(q.split())
    best = None
    best_score = -1
    for item in items:
        target = str(item.get("question", "")).lower()
        t_words = set(target.split())
        score = len(q_words & t_words)
        if score > best_score:
            best_score = score
            best = item
    return best or items[0]


def run_precomputed_comparison(question: str) -> Dict[str, Any]:
    """Use precomputed answers for wow-mode (mock provider)."""
    item = choose_precomputed(question, state.precomputed)
    if not item:
        # Fallback to a generic mock message if file is empty/missing
        text = (
            "Precomputed demo answers are not available, but MOCK mode is enabled.\n\n"
            "Set LLM_PROVIDER + an API key in backend/.env to run fully live."
        )
        baseline = {
            "answer": text,
            "input_tokens": 0,
            "output_tokens": 0,
            "time_s": 0.0,
            "nodes_used": 0,
            "context_bullets": [],
        }
        ads = baseline.copy()
        return {"baseline": baseline, "ads": ads}

    # Expect structure: {question, baseline, ads, context_bullets}
    q_text = item.get("question", question)
    baseline_text = item.get("baseline", "")
    ads_text = item.get("ads", "")
    ctx_bullets = item.get("context_bullets", []) or []

    baseline = {
        "answer": baseline_text,
        "input_tokens": 0,
        "output_tokens": 0,
        "time_s": 0.0,
        "nodes_used": 0,
        "context_bullets": [],
    }
    ads = {
        "answer": ads_text,
        "input_tokens": 0,
        "output_tokens": 0,
        "time_s": 0.0,
        "nodes_used": len(ctx_bullets),
        "context_bullets": ctx_bullets,
    }
    return {"baseline": baseline, "ads": ads, "question_used": q_text}


def run_live_comparison(question: str, nodes: List[dict]) -> Dict[str, Any]:
    """Run baseline vs ADS-enhanced comparison using a real LLM provider."""
    # Baseline
    baseline_prompt = build_baseline_prompt(question)
    baseline_result = generate_response(baseline_prompt)

    # ADS-enhanced
    context_nodes, _ = retrieve_context(question, nodes, k=3)
    ads_prompt = build_ads_prompt(question, context_nodes)
    ads_result = generate_response(ads_prompt)

    # Context bullets for UI
    context_bullets: List[str] = []
    for n in context_nodes:
        insight = n.get("core_insight", "")
        if insight:
            context_bullets.append(insight.strip())

    return {
        "baseline": {
            "answer": baseline_result["text"],
            "input_tokens": baseline_result["input_tokens"] or 0,
            "output_tokens": baseline_result["output_tokens"] or 0,
            "time_s": baseline_result["time_s"],
            "nodes_used": 0,
            "context_bullets": [],
        },
        "ads": {
            "answer": ads_result["text"],
            "input_tokens": ads_result["input_tokens"] or 0,
            "output_tokens": ads_result["output_tokens"] or 0,
            "time_s": ads_result["time_s"],
            "nodes_used": len(context_nodes),
            "context_bullets": context_bullets,
        },
    }


def run_comparison(question: str, nodes: List[dict]) -> Dict[str, Any]:
    """
    Entry point used by the /demo/run endpoint.

    If the LLM provider is 'mock' and precomputed answers exist, we use them
    to create a jaw-dropping demo with zero API keys.

    Otherwise, we call the live LLM provider via llm_client.generate_response().
    """
    if is_mock_provider() and state.precomputed:
        print("[ADS DEMO] Using precomputed WOW-mode answers (mock provider)")
        return run_precomputed_comparison(question)
    else:
        return run_live_comparison(question, nodes)


# ----------------------------
# FastAPI lifespan
# ----------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize resources at startup."""
    print("\n" + "=" * 60)
    print("  ADS WISDOM DEMO — Starting Up")
    print("=" * 60 + "\n")

    state.nodes, state.demo_questions = load_data_pack()
    state.precomputed = load_precomputed_answers()

    print(f"\n[ADS DEMO] ✅ Nodes loaded: {len(state.nodes)}")
    print(f"[ADS DEMO] ✅ Precomputed answers: {len(state.precomputed)}")
    print("[ADS DEMO] 💡 Configure backend/.env to go live with your own LLM")
    print("\n" + "=" * 60 + "\n")

    yield

    print("\n[ADS DEMO] Shutting down...")


# ----------------------------
# FastAPI app
# ----------------------------

app = FastAPI(
    title="ADS Wisdom Demo API",
    description="Awakened Data Standard — Baseline vs ADS-Enhanced comparison",
    version="1.1.0",
    lifespan=lifespan,
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend static files
if FRONTEND_DIR.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIR / "assets"), name="assets")


# ----------------------------
# Endpoints
# ----------------------------

@app.get("/")
def serve_frontend():
    """Serve the main demo page."""
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"message": "ADS Wisdom Demo API", "docs": "/docs"}


@app.get("/health", response_model=HealthResponse)
def health():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        nodes_loaded=len(state.nodes),
        pack_name="Golden_Ethics_Sample_v1",
        precomputed_loaded=len(state.precomputed),
    )


@app.get("/questions")
def get_questions():
    """Get demo questions."""
    return {"questions": state.demo_questions}


@app.post("/demo/run", response_model=DemoResponse)
def run_demo(req: DemoRequest):
    """Run baseline vs ADS comparison for a question."""
    question = req.question.strip()
    if not question:
        question = state.demo_questions[0] if state.demo_questions else "What is wisdom?"

    results = run_comparison(question, state.nodes)

    baseline = DemoAnswer(**results["baseline"])
    ads = DemoAnswer(**results["ads"])

    # raw_metrics can include extra info if you want
    return DemoResponse(
        question=question,
        baseline=baseline,
        ads=ads,
        raw_metrics=results,
    )


# ----------------------------
# Direct run
# ----------------------------

if __name__ == "__main__":
    import uvicorn

    print("\n🦁 Starting ADS Wisdom Demo...")
    print("📍 Open http://localhost:8888 in your browser\n")
    uvicorn.run(app, host="0.0.0.0", port=8888)
