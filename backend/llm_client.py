"""
LLM Client for Awakened Wisdom Demo

This file is designed so that demo runners NEVER have to edit it.

Configuration comes from:
- backend/.env   (simple text file next to this file)
- or real environment variables

Supported providers via LLM_PROVIDER:
- openai     (OpenAI Responses API)
- anthropic  (Anthropic Messages API)
- openrouter (OpenRouter chat completions)
- ollama     (local LLM via Ollama)
- mock       (default; uses precomputed answers in the backend)

Expected return format (used by ads_demo_api):
{
    "text": str,
    "input_tokens": int | None,
    "output_tokens": int | None,
    "time_s": float
}
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


# ---------------------------------------------------------------------------
# Simple .env loader (backend/.env only, no guessing)
# ---------------------------------------------------------------------------

def _load_backend_env() -> None:
    """Load key=value pairs from backend/.env into os.environ (if set)."""
    this_dir = Path(__file__).resolve().parent
    env_path = this_dir / ".env"
    if not env_path.exists():
        print("[ADS DEMO] No backend/.env found – using environment variables or mock mode")
        return

    print(f"[ADS DEMO] Loading backend/.env from {env_path}")
    try:
        with env_path.open("r", encoding="utf-8") as f:
            for raw in f:
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
    except Exception as e:
        print(f"[ADS DEMO] Warning: failed to parse backend/.env: {e}")


_load_backend_env()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _env(name: str, default: Optional[str] = None) -> Optional[str]:
    v = os.environ.get(name)
    if v is None or v == "":
        return default
    return v


@dataclass
class LLMResult:
    text: str
    input_tokens: Optional[int]
    output_tokens: Optional[int]
    time_s: float


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


# ---------------------------------------------------------------------------
# Provider calls
# ---------------------------------------------------------------------------

def _call_openai(prompt: str) -> LLMResult:
    api_key = _env("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing OPENAI_API_KEY in backend/.env or environment.")

    model = _env("LLM_MODEL", "gpt-4o")
    temperature = float(_env("LLM_TEMPERATURE", "0.2"))
    max_out = int(_env("LLM_MAX_OUTPUT_TOKENS", "900"))
    instructions = _env("LLM_SYSTEM", "")

    url = _env("OPENAI_BASE_URL", "https://api.openai.com/v1/responses")
    headers = {"Authorization": f"Bearer {api_key}"}

    payload: Dict[str, Any] = {
        "model": model,
        "input": prompt,
        "temperature": temperature,
        "max_output_tokens": max_out,
    }
    if instructions:
        payload["instructions"] = instructions

    t0 = time.time()
    data = _post_json(url, headers, payload)
    dt = time.time() - t0

    text_parts = []
    for item in data.get("output", []) or []:
        for c in item.get("content", []) or []:
            if isinstance(c, dict) and c.get("type") in ("output_text", "text") and "text" in c:
                text_parts.append(c["text"])
    text = "\n".join([p for p in text_parts if p]).strip()

    usage = data.get("usage") or {}
    input_tokens = _safe_int(usage.get("input_tokens"))
    output_tokens = _safe_int(usage.get("output_tokens"))

    return LLMResult(
        text=text or "(No text returned from OpenAI.)",
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        time_s=dt,
    )


def _call_anthropic(prompt: str) -> LLMResult:
    api_key = _env("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("Missing ANTHROPIC_API_KEY in backend/.env or environment.")

    model = _env("LLM_MODEL", "claude-3-5-sonnet-latest")
    temperature = float(_env("LLM_TEMPERATURE", "0.2"))
    max_tokens = int(_env("LLM_MAX_OUTPUT_TOKENS", "900"))
    system = _env("LLM_SYSTEM", "")

    url = _env("ANTHROPIC_BASE_URL", "https://api.anthropic.com/v1/messages")
    headers = {
        "x-api-key": api_key,
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

    text_parts = []
    for c in data.get("content", []) or []:
        if isinstance(c, dict) and c.get("type") == "text" and "text" in c:
            text_parts.append(c["text"])
    text = "\n".join([p for p in text_parts if p]).strip()

    usage = data.get("usage") or {}
    input_tokens = _safe_int(usage.get("input_tokens"))
    output_tokens = _safe_int(usage.get("output_tokens"))

    return LLMResult(
        text=text or "(No text returned from Anthropic.)",
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        time_s=dt,
    )


def _call_openrouter(prompt: str) -> LLMResult:
    api_key = _env("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("Missing OPENROUTER_API_KEY in backend/.env or environment.")

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

    return LLMResult(
        text=text or "(No text returned from OpenRouter.)",
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        time_s=dt,
    )


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

    input_tokens = _safe_int(data.get("prompt_eval_count"))
    output_tokens = _safe_int(data.get("eval_count"))

    return LLMResult(
        text=text or "(No text returned from Ollama.)",
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        time_s=dt,
    )


def _call_mock(prompt: str) -> LLMResult:
    t0 = time.time()
    text = (
        "MOCK MODE is enabled (LLM_PROVIDER=mock or missing).\n\n"
        "To make this demo fully interactive, set LLM_PROVIDER + an API key in backend/.env.\n"
        "Example:\n"
        "  LLM_PROVIDER=openai\n"
        "  OPENAI_API_KEY=sk-...\n"
        "  LLM_MODEL=gpt-4o\n\n"
        f"Prompt received (first 500 chars):\n{prompt[:500]}"
    )
    dt = time.time() - t0
    return LLMResult(text=text, input_tokens=None, output_tokens=None, time_s=dt)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def is_mock_provider() -> bool:
  """Helper used by ads_demo_api to decide if we should use precomputed answers."""
  provider = (_env("LLM_PROVIDER", "mock") or "mock").strip().lower()
  print(f"[ADS DEMO] LLM_PROVIDER resolved to '{provider}'")
  return provider == "mock"


def generate_response(prompt: str, **_kwargs: Any) -> Dict[str, Any]:
    """
    Called by the demo backend.

    Returns a dict with:
    - text
    - input_tokens
    - output_tokens
    - time_s
    """
    provider = (_env("LLM_PROVIDER", "mock") or "mock").strip().lower()
    print(f"[ADS DEMO] generate_response using provider='{provider}'")

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
