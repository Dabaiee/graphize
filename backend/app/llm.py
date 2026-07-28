"""Claude access layer.

Two helpers:
  - structured(): forces a JSON-schema-shaped response via output_config.format,
    so callers get a validated dict back (no brittle string parsing).
  - text(): a plain natural-language answer, with adaptive thinking on for the
    GraphRAG answer step.

Model defaults to claude-opus-4-8 (see config.MODEL).
"""
from __future__ import annotations

import json
from typing import Any

import anthropic

from . import config

_client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)


def structured(
    system: str,
    user: str,
    schema: dict[str, Any],
    *,
    max_tokens: int = 8000,
) -> dict[str, Any]:
    """Return a dict guaranteed to match `schema` (a JSON Schema object).

    Uses output_config.format=json_schema — the current, non-deprecated way to
    constrain the Messages API response. No assistant prefill (rejected on 4.x).
    """
    resp = _client.messages.create(
        model=config.MODEL,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
        output_config={
            "format": {
                "type": "json_schema",
                "schema": schema,
            }
        },
    )
    # With output_config.format the first text block is valid JSON for the schema.
    payload = next((b.text for b in resp.content if b.type == "text"), None)
    if payload is None:
        raise RuntimeError(f"No structured output returned (stop_reason={resp.stop_reason})")
    return json.loads(payload)


def text(
    system: str,
    user: str,
    *,
    thinking: bool = True,
    max_tokens: int = 4000,
) -> str:
    """Return a natural-language answer. Adaptive thinking on by default."""
    kwargs: dict[str, Any] = {
        "model": config.MODEL,
        "max_tokens": max_tokens,
        "system": system,
        "messages": [{"role": "user", "content": user}],
    }
    if thinking:
        kwargs["thinking"] = {"type": "adaptive"}
        kwargs["output_config"] = {"effort": "medium"}
    resp = _client.messages.create(**kwargs)
    return "".join(b.text for b in resp.content if b.type == "text").strip()
