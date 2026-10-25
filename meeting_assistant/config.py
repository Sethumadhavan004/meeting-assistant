"""
config.py - settings from meeting-assistant.toml, and a health check per model server.

The health check exists so a stopped server gives a clear message ("start scripts/start_bonsai.ps1")
instead of a connection traceback.
"""
import os
import tomllib
from pathlib import Path

import requests

ROOT = Path(__file__).parent.parent
CONFIG_PATH = Path(os.environ.get("MEETING_ASSISTANT_CONFIG", ROOT / "meeting-assistant.toml"))


def load():
    cfg = tomllib.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    cfg["system_prompt"] = ROOT / cfg["system_prompt"]
    return cfg


class BackendError(RuntimeError):
    """A model server is missing, not running, or doesn't have the model."""


HOW_TO_START = {
    "llama-server": "start it in its own terminal: .\\scripts\\start_bonsai.ps1",
    "ollama": "start Ollama, then: ollama pull {model}",
}


def check(name, cfg=None):
    """Raise BackendError with a fix-it message unless the backend can answer."""
    cfg = cfg or load()
    if name not in cfg["backends"]:
        raise BackendError(f"unknown backend '{name}'; configured: {', '.join(cfg['backends'])}")
    b = cfg["backends"][name]
    hint = HOW_TO_START[b["kind"]].format(model=b["model"])
    try:
        if b["kind"] == "ollama":
            tags = requests.get(f"{b['url']}/api/tags", timeout=5).json()
            if not any(m["name"].startswith(b["model"]) for m in tags.get("models", [])):
                raise BackendError(f"Ollama is running but '{b['model']}' isn't pulled; run: ollama pull {b['model']}")
        else:
            if requests.get(f"{b['url']}/health", timeout=5).json().get("status") != "ok":
                raise BackendError(f"{name} server is starting or unhealthy; wait, or {hint}")
    except requests.RequestException:
        raise BackendError(f"{name} server not reachable at {b['url']}; {hint}") from None
    return b
