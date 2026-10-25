"""
cli.py - the `meeting-assistant` command.

  meeting-assistant notes my-meeting.txt              transcript -> my-meeting.notes.md
  meeting-assistant notes my-meeting.txt --backend phi
  meeting-assistant check                             which model servers are up
  meeting-assistant serve                             web app at http://127.0.0.1:8765

Transcript format: one line per turn, "Name: what they said".
"""
import argparse
import sys
from pathlib import Path

from . import config
from .core import INSTRUCTION, notes, to_markdown


def cmd_notes(a):
    src = Path(a.transcript)
    text = src.read_text(encoding="utf-8").replace(INSTRUCTION, "").strip()  # eval prompt files include it
    result = notes(text, a.backend)
    md = to_markdown(result)
    out = Path(a.out) if a.out else src.with_suffix(".notes.md")
    out.write_text(md, encoding="utf-8")
    if a.raw:
        print(result["raw"], "\n")
    print(md)
    print(f"Saved {out}")


def cmd_check(_a):
    cfg = config.load()
    for name, b in cfg["backends"].items():
        try:
            config.check(name, cfg)
            print(f"  ok    {name:8} {b['url']}  ({b['note']})")
        except config.BackendError as e:
            print(f"  down  {name:8} {e}")


def cmd_serve(a):
    import uvicorn
    print(f"Meeting assistant: http://{a.host}:{a.port}  (Ctrl+C to stop)")
    uvicorn.run("meeting_assistant.web.server:app", host=a.host, port=a.port, log_level="warning")


def main():
    sys.stdout.reconfigure(encoding="utf-8")  # Windows consoles default to cp1252
    ap = argparse.ArgumentParser(prog="meeting-assistant", description="Local meeting assistant")
    sub = ap.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("notes", help="transcript file -> notes")
    n.add_argument("transcript")
    n.add_argument("--backend", help="model server from meeting-assistant.toml (default: its default_backend)")
    n.add_argument("-o", "--out", help="notes file (default: <transcript>.notes.md)")
    n.add_argument("--raw", action="store_true", help="also print the model's raw answer")
    sub.add_parser("check", help="show which model servers are reachable")
    s = sub.add_parser("serve", help="start the web app")
    s.add_argument("--host", default="127.0.0.1")  # localhost only: meetings stay on this machine
    s.add_argument("--port", type=int, default=8765)
    a = ap.parse_args()
    try:
        {"notes": cmd_notes, "check": cmd_check, "serve": cmd_serve}[a.cmd](a)
    except config.BackendError as e:
        sys.exit(f"Model server problem: {e}")


if __name__ == "__main__":
    main()
