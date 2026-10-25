"""
cli.py - meeting transcript in, notes out.

Transcript format: one line per turn, "Name: what they said".

Usage:
  python app/cli.py transcript.txt                      # Bonsai (llama-server on :8080)
  python app/cli.py transcript.txt --backend phi        # Phi via Ollama (faster, lower recall)
  python app/cli.py transcript.txt -o notes.md
"""
import argparse
import sys
from pathlib import Path

from core import BACKENDS, INSTRUCTION, notes


def main():
    ap = argparse.ArgumentParser(description="Local meeting assistant: transcript -> action items")
    ap.add_argument("transcript")
    ap.add_argument("--backend", default="bonsai", choices=BACKENDS)
    ap.add_argument("-o", "--out", help="notes file (default: <transcript>.notes.md)")
    ap.add_argument("--raw", action="store_true", help="also print the model's raw answer")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")  # Windows consoles default to cp1252

    src = Path(a.transcript)
    text = src.read_text(encoding="utf-8")
    text = text.replace(INSTRUCTION, "").strip()  # eval prompt files carry the instruction line already
    md, raw = notes(text, a.backend)
    out = Path(a.out) if a.out else src.with_suffix(".notes.md")
    out.write_text(md, encoding="utf-8")
    if a.raw:
        print(raw, "\n")
    print(md)
    print(f"Saved {out}")


if __name__ == "__main__":
    main()
