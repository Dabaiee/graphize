"""Provider-agnostic LLM layer.

Supported providers (config.STATE["provider"]):
  - anthropic : Claude, structured outputs via output_config.format (best quality)
  - openai    : GPT, native strict json_schema response_format
  - ollama    : local free models via Ollama's OpenAI-compatible endpoint;
                JSON-mode + schema-in-prompt + validate/retry (weaker models)

All three expose the same two helpers used by the agents:
  - structured(system, user, schema) -> validated dict
  - text(system, user) -> string
Clients are built lazily and cached; reset_clients() is called when config changes.
"""
from __future__ import annotations

import json
import re
from typing import Any

from . import config

_clients: dict[str, Any] = {}


def reset_clients() -> None:
    _clients.clear()


# ---------------------------------------------------------------------------
# Clients
# ---------------------------------------------------------------------------

def _anthropic():
    if "anthropic" not in _clients:
        import anthropic
        _clients["anthropic"] = anthropic.Anthropic(api_key=config.STATE["anthropic_api_key"])
    return _clients["anthropic"]


def _openai_compatible():
    """One client for both OpenAI and Ollama (Ollama speaks the OpenAI API)."""
    if "openai" not in _clients:
        from openai import OpenAI
        if config.STATE["provider"] == "ollama":
            base = config.STATE["ollama_base_url"].rstrip("/") + "/v1"
            _clients["openai"] = OpenAI(base_url=base, api_key="ollama")
        else:
            kwargs: dict[str, Any] = {"api_key": config.STATE["openai_api_key"]}
            if config.STATE["openai_base_url"]:
                kwargs["base_url"] = config.STATE["openai_base_url"]
            _clients["openai"] = OpenAI(**kwargs)
    return _clients["openai"]


# ---------------------------------------------------------------------------
# Structured output
# ---------------------------------------------------------------------------

def structured(system: str, user: str, schema: dict[str, Any], *, max_tokens: int = 8000) -> dict[str, Any]:
    if config.STATE["provider"] == "anthropic":
        return _anthropic_structured(system, user, schema, max_tokens)
    return _openai_structured(system, user, schema)


def _anthropic_structured(system, user, schema, max_tokens):
    resp = _anthropic().messages.create(
        model=config.STATE["anthropic_model"],
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
        output_config={"format": {"type": "json_schema", "schema": schema}},
    )
    payload = next((b.text for b in resp.content if b.type == "text"), None)
    if payload is None:
        raise RuntimeError(f"No structured output (stop_reason={resp.stop_reason})")
    return json.loads(payload)


def _openai_structured(system, user, schema):
    client = _openai_compatible()
    model = config.active_model()

    if config.STATE["provider"] == "openai":
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            response_format={
                "type": "json_schema",
                "json_schema": {"name": "graphize_output", "schema": schema, "strict": True},
            },
        )
        return json.loads(resp.choices[0].message.content)

    # ollama / other OpenAI-compatible local models: JSON mode + schema-in-prompt.
    sys2 = (
        system
        + "\n\nReturn ONLY a single JSON object matching this JSON schema "
        "(no prose, no markdown fences):\n" + json.dumps(schema)
    )
    raw = ""
    for _ in range(2):
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": sys2}, {"role": "user", "content": user}],
            response_format={"type": "json_object"},
        )
        raw = resp.choices[0].message.content or ""
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            sys2 += "\n\nYour previous reply was not valid JSON. Output ONLY the JSON object."
    return json.loads(_extract_json(raw))  # last resort


def _extract_json(text: str) -> str:
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m:
        raise ValueError("Model did not return JSON.")
    return m.group(0)


# ---------------------------------------------------------------------------
# Free-text answer
# ---------------------------------------------------------------------------

def text(system: str, user: str, *, thinking: bool = True, max_tokens: int = 4000) -> str:
    if config.STATE["provider"] == "anthropic":
        kwargs: dict[str, Any] = {
            "model": config.STATE["anthropic_model"],
            "max_tokens": max_tokens,
            "system": system,
            "messages": [{"role": "user", "content": user}],
        }
        if thinking:
            kwargs["thinking"] = {"type": "adaptive"}
            kwargs["output_config"] = {"effort": "medium"}
        resp = _anthropic().messages.create(**kwargs)
        return "".join(b.text for b in resp.content if b.type == "text").strip()

    resp = _openai_compatible().chat.completions.create(
        model=config.active_model(),
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
    )
    return (resp.choices[0].message.content or "").strip()


# ---------------------------------------------------------------------------
# Connection test (for the settings UI)
# ---------------------------------------------------------------------------

def ping() -> dict[str, Any]:
    try:
        reply = text("You are a connectivity test.", "Reply with the single word: ok",
                     thinking=False, max_tokens=16)
        return {"ok": True, "reply": reply[:80],
                "provider": config.STATE["provider"], "model": config.active_model()}
    except Exception as e:  # surface the real error to the UI
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}
