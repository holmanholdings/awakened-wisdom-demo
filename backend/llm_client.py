"""
LLM Client for Awakened Wisdom Demo (no-code-edit setup)

✅ Goal: demo runners should NOT edit this file.
They should only set environment variables (or a .env file).

Supported providers:
- OpenAI (Responses API)          LLM_PROVIDER=openai
- Anthropic (Messages API)        LLM_PROVIDER=anthropic
- OpenRouter (OpenAI compat)      LLM_PROVIDER=openrouter
- Ollama (local)                  LLM_PROVIDER=ollama
- Mock (no network)               LLM_PROVIDER=mock

Where to put config:
- backend/.env   (recommended)
- or repo root .env
- or real environment variables

Minimal .env examples:

# OpenAI
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
LLM_MODEL=gpt-4o

# Anthropic
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=...
LLM_MODEL=claude-3-5-sonnet-latest

# OpenRouter
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=...
LLM_MODEL=anthropic/claude-3.5-sonnet

# Ollama (local)
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
LLM_MODEL=llama3.1

Return format (expected by demo):
{"text": "...", "input_tokens": int|None, "output_tokens": int|None, "time_s": float}
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


# -------------------------
# Small .env loader (stdlib)
# -------------------------
def _load_dotenv_file(path: str) -> None:
    if not os.path.exists(path):
        return
    try:
        with open(path, "r", encoding="utf-8") as f:
            for raw in f.readlines():
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                # Do not override real env vars
                if k and (k not in os.environ):
                    os.environ[k] = v
    except Exception:
        # Silent: demo should still run even if dotenv parsing fails
        return


# Load backend/.env first, then repo-root .env
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_load_dotenv_file(os.path.join(_THIS_DIR, ".env"))
_load_dotenv_file(os.path.abspath(os.path.join(_THIS_DIR, "..", ".env")))


@dataclass
class LLMResult:
    text: str
    input_tokens: Optional[int]
    output_tokens: Optional[int]
    time_s: float


def _env(name: str, default: Optional[str] = None) -> Optional[str]:
    v = os.environ.get(name)
    if v is None or v == "":
        return default
    return v


def _post_json(url: str, headers: Dict[str, str], payload: Dict[str, Any], timeout_s: int = 90) -> Dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    req = Request(url, data=data, headers={**headers, "Content-Type": "application/json"}, method="POST")
    with urlopen(req, timeout=timeout_s) as resp:
        body = resp.read().decode("utf-8")
        return json.loads(body)


def _safe_int(x: Any) -> Optional[int]:
    try:
        if x is None:
            return None
        return int(x)
    except Exception:
        return None


# -------------------------
# Providers
# -------------------------
def _call_openai(prompt: str) -> LLMResult:
    # OpenAI Responses API endpoint
    api_key = _env("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing OPENAI_API_KEY. Put it in backend/.env (recommended) or your environment.")

    model = _env("LLM_MODEL", "gpt-4o")
    temperature = float(_env("LLM_TEMPERATURE", "0.2"))
    max_out = int(_env("LLM_MAX_OUTPUT_TOKENS", "900"))
    instructions = _env("LLM_SYSTEM", "")

    url = _env("OPENAI_BASE_URL", "https://api.openai.com/v1/responses")
    headers = {"Authorization": f"Bearer {api_key}"}

    payload: Dict[str, Any] = {
        "model": model,
        "input": prompt,  # string input is allowed
        "temperature": temperature,
        "max_output_tokens": max_out,
    }
    if instructions:
        payload["instructions"] = instructions

    t0 = time.time()
    data = _post_json(url, headers, payload)
    dt = time.time() - t0

    # Parse output text (Responses format)
    # output -> [ { type:"message", content:[ {type:"output_text", text:"..."} ] } ]
    text_parts = []
    for item in data.get("output", []) or []:
        for c in item.get("content", []) or []:
            if isinstance(c, dict) and c.get("type") in ("output_text", "text") and "text" in c:
                text_parts.append(c["text"])
    text = "\n".join([p for p in text_parts if p]).strip()

    usage = data.get("usage") or {}
    input_tokens = _safe_int(usage.get("input_tokens"))
    output_tokens = _safe_int(usage.get("output_tokens"))

    return LLMResult(text=text or "(No text returned from OpenAI.)", input_tokens=input_tokens, output_tokens=output_tokens, time_s=dt)


def _call_anthropic(prompt: str) -> LLMResult:
    api_key = _env("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("Missing ANTHROPIC_API_KEY. Put it in backend/.env (recommended) or your environment.")

    model = _env("LLM_MODEL", "claude-3-5-sonnet-latest")
    temperature = float(_env("LLM_TEMPERATURE", "0.2"))
    max_tokens = int(_env("LLM_MAX_OUTPUT_TOKENS", "900"))
    system = _env("LLM_SYSTEM", "")

    url = _env("ANTHROPIC_BASE_URL", "https://api.anthropic.com/v1/messages")
    headers = {
        "x-api-key": api_key,
        # Anthropic requires a version header
        "anthropic-version": _env("ANTHROPIC_VERSION", "2023-06-01"),
    }

    payload: Dict[str, Any] = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [{"role": "user", "content": prompt}],
    }
    if system:
        payload["system"] = system

    t0 = time.time()
    data = _post_json(url, headers, payload)
    dt = time.time() - t0

    # Parse text
    # content: [ { type:"text", text:"..." } ]
    text_parts = []
    for c in data.get("content", []) or []:
        if isinstance(c, dict) and c.get("type") == "text" and "text" in c:
            text_parts.append(c["text"])
    text = "\n".join([p for p in text_parts if p]).strip()

    usage = data.get("usage") or {}
    input_tokens = _safe_int(usage.get("input_tokens"))
    output_tokens = _safe_int(usage.get("output_tokens"))

    return LLMResult(text=text or "(No text returned from Anthropic.)", input_tokens=input_tokens, output_tokens=output_tokens, time_s=dt)


def _call_openrouter(prompt: str) -> LLMResult:
    api_key = _env("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("Missing OPENROUTER_API_KEY. Put it in backend/.env (recommended) or your environment.")

    model = _env("LLM_MODEL", "openai/gpt-4o-mini")
    temperature = float(_env("LLM_TEMPERATURE", "0.2"))
    max_tokens = int(_env("LLM_MAX_OUTPUT_TOKENS", "900"))
    system = _env("LLM_SYSTEM", "")

    url = _env("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1/chat/completions")
    headers = {"Authorization": f"Bearer {api_key}"}

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    payload: Dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    t0 = time.time()
    data = _post_json(url, headers, payload)
    dt = time.time() - t0

    text = ""
    try:
        text = (data.get("choices") or [])[0]["message"]["content"]
    except Exception:
        text = ""

    usage = data.get("usage") or {}
    input_tokens = _safe_int(usage.get("prompt_tokens"))
    output_tokens = _safe_int(usage.get("completion_tokens"))

    return LLMResult(text=text or "(No text returned from OpenRouter.)", input_tokens=input_tokens, output_tokens=output_tokens, time_s=dt)


def _call_ollama(prompt: str) -> LLMResult:
    base_url = _env("OLLAMA_BASE_URL", "http://localhost:11434")
    model = _env("LLM_MODEL", "llama3.1")
    temperature = float(_env("LLM_TEMPERATURE", "0.2"))
    system = _env("LLM_SYSTEM", "")

    url = base_url.rstrip("/") + "/api/chat"
    headers: Dict[str, str] = {}

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    payload: Dict[str, Any] = {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {"temperature": temperature},
    }

    t0 = time.time()
    data = _post_json(url, headers, payload, timeout_s=180)
    dt = time.time() - t0

    text = ""
    try:
        text = (data.get("message") or {}).get("content", "")
    except Exception:
        text = ""

    # Ollama returns eval counts in some builds
    input_tokens = _safe_int(data.get("prompt_eval_count"))
    output_tokens = _safe_int(data.get("eval_count"))

    return LLMResult(text=text or "(No text returned from Ollama.)", input_tokens=input_tokens, output_tokens=output_tokens, time_s=dt)


def _call_mock(prompt: str) -> LLMResult:
    # For “it runs instantly” demos without keys.
    # You can improve this later by loading precomputed answers from a file.
    t0 = time.time()
    text = (
        "MOCK MODE is enabled (LLM_PROVIDER=mock).\n\n"
        "To make this demo fully interactive, set LLM_PROVIDER + an API key in backend/.env.\n"
        "Example:\n"
        "  LLM_PROVIDER=openai\n"
        "  OPENAI_API_KEY=sk-...\n"
        "  LLM_MODEL=gpt-4o\n\n"
        f"Prompt received (first 500 chars):\n{prompt[:500]}"
    )
    dt = time.time() - t0
    return LLMResult(text=text, input_tokens=None, output_tokens=None, time_s=dt)


# -------------------------
# Public function (used by demo backend)
# -------------------------
def generate_response(prompt: str, **_kwargs: Any) -> Dict[str, Any]:
    """
    Called by the demo backend.
    Returns:
      {"text": "...", "input_tokens": int|None, "output_tokens": int|None, "time_s": float}
    """
    provider = (_env("LLM_PROVIDER", "mock") or "mock").strip().lower()

    try:
        if provider == "openai":
            r = _call_openai(prompt)
        elif provider == "anthropic":
            r = _call_anthropic(prompt)
        elif provider == "openrouter":
            r = _call_openrouter(prompt)
        elif provider == "ollama":
            r = _call_ollama(prompt)
        elif provider == "mock":
            r = _call_mock(prompt)
        else:
            raise RuntimeError(f"Unknown LLM_PROVIDER='{provider}'. Use openai|anthropic|openrouter|ollama|mock.")
    except HTTPError as e:
        try:
            body = e.read().decode("utf-8", errors="ignore")
        except Exception:
            body = ""
        return {
            "text": f"[LLM ERROR] HTTP {getattr(e, 'code', '?')} from provider '{provider}'.\n{body}",
            "input_tokens": None,
            "output_tokens": None,
            "time_s": 0.0,
        }
    except URLError as e:
        return {
            "text": f"[LLM ERROR] Network error calling provider '{provider}': {e}",
            "input_tokens": None,
            "output_tokens": None,
            "time_s": 0.0,
        }
    except Exception as e:
        return {
            "text": f"[LLM ERROR] {e}",
            "input_tokens": None,
            "output_tokens": None,
            "time_s": 0.0,
        }

    return {
        "text": r.text,
        "input_tokens": r.input_tokens,
        "output_tokens": r.output_tokens,
        "time_s": r.time_s,
    }

def is_mock_provider() -> bool:
    """Helper used by ads_demo_api to decide if we should use precomputed answers."""
    provider = (_env("LLM_PROVIDER", "mock") or "mock").strip().lower()
    return provider == "mock"
