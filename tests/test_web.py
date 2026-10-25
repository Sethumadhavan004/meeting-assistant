"""Web API tests, in-process. The model call is faked, so no model server is needed."""
import pytest
from fastapi.testclient import TestClient

from meeting_assistant import config
from meeting_assistant.web import server

FAKE = {"backend": "bonsai", "seconds": 1.0, "raw": "Akhash | send the budget | Friday",
        "items": [{"owner": "Akhash", "task": "send the budget", "deadline": "Friday", "flags": []}],
        "missed": [{"speaker": "Priya", "sentence": "We need someone to book the room."}], "rejected": []}


@pytest.fixture
def client(monkeypatch, tmp_path):
    monkeypatch.setattr(server, "notes", lambda transcript, backend=None: FAKE)
    monkeypatch.setattr(config, "ROOT", tmp_path)  # saves go to a temp folder
    return TestClient(server.app)


def test_page_and_config(client):
    assert "Meeting Assistant" in client.get("/").text
    cfg = client.get("/api/config").json()
    assert cfg["default_backend"] in cfg["backends"]


def test_empty_transcript_is_rejected(client):
    assert client.post("/api/notes", json={"transcript": "  "}).status_code == 400


def test_notes_returns_items_and_suggestions(client):
    r = client.post("/api/notes", json={"transcript": "Akhash: I'll send the budget by Friday."}).json()
    assert r["items"][0]["owner"] == "Akhash"
    assert r["missed"][0]["speaker"] == "Priya"


def test_server_down_is_a_503_with_the_fix(client, monkeypatch):
    def down(*_a, **_k):
        raise config.BackendError("bonsai server not reachable; start it: .\\scripts\\start_bonsai.ps1")
    monkeypatch.setattr(server, "notes", down)
    r = client.post("/api/notes", json={"transcript": "A: b"})
    assert r.status_code == 503 and "start_bonsai" in r.json()["detail"]


def test_too_short_audio_returns_empty_text(client):
    assert client.post("/api/transcribe", content=b"\x00" * 400).json() == {"text": "", "seconds": 0}


def test_save_writes_transcript_and_notes(client, tmp_path):
    folder = client.post("/api/save", json={"transcript": "Akhash: hi", "result": FAKE}).json()["folder"]
    files = {p.name for p in (tmp_path / "meetings").iterdir() for p in p.iterdir()}
    assert files == {"transcript.txt", "notes.md", "notes.json"}
    assert folder.startswith(str(tmp_path))
