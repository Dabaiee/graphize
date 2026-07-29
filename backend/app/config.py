"""Configuration.

Neo4j + app constants come from env only. The LLM config (provider, keys, model)
is runtime-mutable via the settings UI and persisted to a JSON file in the data
volume, so users can switch providers without editing .env or restarting.
"""
from __future__ import annotations

import json
import os

# --- Neo4j (infra, env only) ---
NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "fastgraph")

UPLOAD_DIR = os.environ.get("FASTGRAPH_UPLOAD_DIR", "/data/uploads")
CONFIG_FILE = os.environ.get("FASTGRAPH_CONFIG_FILE", os.path.join(UPLOAD_DIR, "config.json"))

CHUNK_SIZE = 1200
CHUNK_OVERLAP = 150
MAX_EXTRACTION_CONCURRENCY = 6

# --- LLM runtime config (env = defaults; UI can override; persisted to CONFIG_FILE) ---
_DEFAULTS = {
    "provider": os.environ.get("FASTGRAPH_PROVIDER", "anthropic").lower(),
    "anthropic_api_key": os.environ.get("ANTHROPIC_API_KEY", ""),
    "anthropic_model": os.environ.get("FASTGRAPH_MODEL", "claude-opus-4-8"),
    "openai_api_key": os.environ.get("OPENAI_API_KEY", ""),
    "openai_model": os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
    "openai_base_url": os.environ.get("OPENAI_BASE_URL", ""),
    "ollama_base_url": os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"),
    "ollama_model": os.environ.get("OLLAMA_MODEL", "llama3.1"),
}

STATE: dict[str, str] = dict(_DEFAULTS)
_SECRETS = {"anthropic_api_key", "openai_api_key"}


def _load() -> None:
    try:
        with open(CONFIG_FILE) as f:
            data = json.load(f)
        for k, v in data.items():
            if k in STATE and isinstance(v, str):
                STATE[k] = v
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        pass


_load()


def save() -> None:
    try:
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        with open(CONFIG_FILE, "w") as f:
            json.dump(STATE, f)
    except OSError:
        pass


def update(patch: dict) -> None:
    for k, v in patch.items():
        if k not in STATE or not isinstance(v, str):
            continue
        # A blank secret field means "keep existing" — don't wipe a saved key.
        if k in _SECRETS and v.strip() == "":
            continue
        STATE[k] = v.strip()
    save()


def active_model() -> str:
    return {
        "anthropic": STATE["anthropic_model"],
        "openai": STATE["openai_model"],
        "ollama": STATE["ollama_model"],
    }.get(STATE["provider"], STATE["anthropic_model"])


def provider_ready() -> bool:
    p = STATE["provider"]
    if p == "anthropic":
        return bool(STATE["anthropic_api_key"])
    if p == "openai":
        return bool(STATE["openai_api_key"])
    if p == "ollama":
        return bool(STATE["ollama_base_url"])
    return False


def public() -> dict:
    """Sanitized config for the UI — never returns raw secrets."""
    return {
        "provider": STATE["provider"],
        "anthropic_model": STATE["anthropic_model"],
        "openai_model": STATE["openai_model"],
        "openai_base_url": STATE["openai_base_url"],
        "ollama_base_url": STATE["ollama_base_url"],
        "ollama_model": STATE["ollama_model"],
        "keys_set": {
            "anthropic": bool(STATE["anthropic_api_key"]),
            "openai": bool(STATE["openai_api_key"]),
        },
        "provider_ready": provider_ready(),
        "active_model": active_model(),
    }
