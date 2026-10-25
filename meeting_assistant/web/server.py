"""
server.py - the local web app's API. Listens on 127.0.0.1 only: audio and notes never leave the machine.

  GET  /                 the page (static/index.html)
  GET  /api/config       model servers, default, participants
  GET  /api/health       which model servers are up (with fix-it messages)
  POST /api/transcribe   raw 16 kHz mono float32 audio (the browser resamples) -> text
  POST /api/notes        {transcript, backend} -> items, flags, possibly missed
  POST /api/save         {transcript, result} -> meetings/<date_time>/ (git-ignored)
"""
import datetime
import json
from pathlib import Path

import numpy as np
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .. import config, speech
from ..core import notes, to_markdown

STATIC = Path(__file__).parent / "static"
PARTICIPANTS = ["Akhash", "Goutham", "Muhil", "Priya", "Eric", "Darcy", "Elizabeth"]  # if the config has none

app = FastAPI(title="Meeting assistant (local)")
app.mount("/static", StaticFiles(directory=STATIC), name="static")


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


@app.get("/api/config")
def get_config():
    cfg = config.load()
    return {"default_backend": cfg["default_backend"], "participants": cfg.get("participants", PARTICIPANTS),
            "backends": {k: {"model": v["model"], "note": v["note"]} for k, v in cfg["backends"].items()}}


@app.get("/api/health")
def health():
    cfg, out = config.load(), {}
    for name in cfg["backends"]:
        try:
            config.check(name, cfg)
            out[name] = {"ok": True}
        except config.BackendError as e:
            out[name] = {"ok": False, "message": str(e)}
    return out


@app.post("/api/transcribe")
async def transcribe(request: Request):
    audio = np.frombuffer(await request.body(), dtype=np.float32)
    if len(audio) < speech.RATE // 5:
        return {"text": "", "seconds": 0}
    if len(audio) > speech.RATE * 60 * 10:
        raise HTTPException(413, "turn longer than 10 minutes; stop and start a new turn")
    return {"text": speech.transcribe(audio), "seconds": round(len(audio) / speech.RATE, 1)}


class NotesRequest(BaseModel):
    transcript: str
    backend: str | None = None


@app.post("/api/notes")
def make_notes(req: NotesRequest):
    if not req.transcript.strip():
        raise HTTPException(400, "transcript is empty")
    try:
        return notes(req.transcript, req.backend)
    except config.BackendError as e:
        raise HTTPException(503, str(e)) from None


class SaveRequest(BaseModel):
    transcript: str
    result: dict


@app.post("/api/save")
def save(req: SaveRequest):
    folder = config.ROOT / "meetings" / datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "transcript.txt").write_text(req.transcript.strip() + "\n", encoding="utf-8")
    (folder / "notes.md").write_text(to_markdown(req.result), encoding="utf-8")
    (folder / "notes.json").write_text(json.dumps(req.result, indent=2), encoding="utf-8")
    return {"folder": str(folder)}
