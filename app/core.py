"""
core.py - transcript -> action items, with the fixes the eval showed are needed.

Pipeline (each step exists because of a finding in eval/):
  1. extract    one request to a local model, thinking off, with the round-2 system prompt
                (thinking cost ~10x the time and often the answer: eval/04-analysis.md)
  2. parse      strict `owner | task | deadline` lines; skip the header line and any line copied
                from the prompt's example (both seen in round 2: eval/05-observations.md)
  3. reconcile  in code, not in the prompt: the prompt fixed deadlines but not owners
                - "we need..." given to the person who said it -> needs an owner
                - one task listed twice with different owners -> conflict, shown for review
"""
import re
import time
from dataclasses import dataclass, field
from pathlib import Path

import requests

ROOT = Path(__file__).parent.parent
SYSTEM_PROMPT = ROOT / "prompts" / "system" / "meeting-assistant.md"
INSTRUCTION = "Extract action items from this meeting as a list: owner, task, deadline."

# Both servers speak the OpenAI chat API. Bonsai + system prompt was the round-2 pick; Phi is the fast option.
BACKENDS = {
    "bonsai": {"url": "http://127.0.0.1:8080/v1/chat/completions", "model": "bonsai-4b"},
    "phi": {"url": "http://127.0.0.1:11434/v1/chat/completions", "model": "phi4-mini"},
    "granite": {"url": "http://127.0.0.1:11434/v1/chat/completions", "model": "granite4.2:3b"},
}

NEED = re.compile(r"\b(we need|we should|someone (should|needs|has to)|somebody (should|needs|has to)|"
                  r"it would be good if|needs to be|has to be)\b", re.I)
COMMIT = re.compile(r"\b(i'll|i will|i can|i'm going to|let me|i'll take|that's mine|i'll do)\b", re.I)
STOP = set("a an the to of for and or in on at by with from is are be it this that we our i you".split())


@dataclass
class Item:
    owner: str
    task: str
    deadline: str
    flags: list = field(default_factory=list)


# ---------------- 1. extract ----------------
def extract(transcript, backend="bonsai", timeout=600):
    """Send the transcript, return (answer text, seconds)."""
    cfg = BACKENDS[backend]
    body = {
        "model": cfg["model"],
        "messages": [{"role": "system", "content": SYSTEM_PROMPT.read_text(encoding="utf-8")},
                     {"role": "user", "content": f"{INSTRUCTION}\n\n{transcript.strip()}\n"}],
        "temperature": 0,
        "max_tokens": 1000,
        "chat_template_kwargs": {"enable_thinking": False},  # llama-server; ignored by Ollama
    }
    t0 = time.perf_counter()
    r = requests.post(cfg["url"], json=body, timeout=timeout)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"] or "", time.perf_counter() - t0


# ---------------- 2. parse ----------------
def example_lines():
    """The example lines in the system prompt; models sometimes copy them into the answer."""
    text = SYSTEM_PROMPT.read_text(encoding="utf-8")
    after = text.split("Example:", 1)[-1]
    return {norm_line(l) for l in after.splitlines() if l.count("|") == 2}


def norm_line(line):
    return " | ".join(p.strip().lower() for p in line.split("|"))


def parse(answer):
    """Return (items, rejected lines). A line is an item only if it has exactly three fields."""
    examples, items, rejected = example_lines(), [], []
    for raw in answer.splitlines():
        line = re.sub(r"^\s*([-*•]|\d+[.)])\s*", "", raw).strip()
        if not line:
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) != 3 or not all(parts):
            rejected.append(raw)
        elif [p.lower() for p in parts] == ["owner", "task", "deadline"] or norm_line(line) in examples:
            continue  # header line, or the prompt's example copied
        else:
            items.append(Item(*parts))
    return items, rejected


# ---------------- 3. reconcile ----------------
def words(text):
    ws = {w for w in re.findall(r"[a-z0-9']+", text.lower()) if w not in STOP and len(w) > 2}
    return {w[:-1] if w.endswith("s") and len(w) > 3 else w for w in ws}  # caterers = caterer


def overlap(a, b):
    a, b = words(a), words(b)
    return len(a & b) / len(a | b) if a and b else 0.0


def speaker_lines(transcript):
    """'Name: text' lines -> [(name, text)]"""
    out = []
    for line in transcript.splitlines():
        m = re.match(r"^\s*([A-Z][\w .'-]{0,30}):\s*(.+)$", line)
        if m:
            out.append((m.group(1).strip(), m.group(2).strip()))
    return out


def reconcile(items, transcript):
    lines = speaker_lines(transcript)
    # (a) "we need..." raised by X and given to X, while X never committed to it -> needs an owner
    for it in items:
        if it.owner.upper() == "UNASSIGNED" or not lines:
            continue
        src = max(lines, key=lambda l: overlap(it.task, l[1]))
        committed = any(name.lower() == it.owner.lower() and COMMIT.search(text) and overlap(it.task, text) > 0.1
                        for name, text in lines)
        if src[0].lower() == it.owner.lower() and NEED.search(src[1]) and not committed:
            it.flags.append(f"{it.owner} raised this but nobody took it")
            it.owner = "UNASSIGNED"
    # (b) duplicates. Word overlap can't tell "draft the press release" from "review the press release"
    #     (measured: eval/05-observations.md), so only near-identical lines are merged; similar lines
    #     with different owners are kept and flagged. Never delete a task on a guess.
    kept = []
    for it in items:
        twin = next((k for k in kept if overlap(k.task, it.task) >= 0.8), None)
        if twin and twin.owner.lower() == it.owner.lower():
            continue                                      # exact repeat
        if twin and twin.owner.upper() == "UNASSIGNED" and not twin.flags:
            twin.owner, twin.task, twin.deadline = it.owner, it.task, it.deadline
            twin.flags.append("also listed as unassigned")  # someone committed to it
            continue
        if twin and it.owner.upper() == "UNASSIGNED":
            continue                                      # already owned
        for k in kept:
            if overlap(k.task, it.task) >= 0.4 and k.owner.lower() != it.owner.lower() \
                    and "UNASSIGNED" not in (k.owner.upper(), it.owner.upper()):
                k.flags.append(f"similar task for {it.owner}: check")
                it.flags.append(f"similar task for {k.owner}: check")
        kept.append(it)
    for k in kept:
        k.flags = list(dict.fromkeys(k.flags))  # unique, in order
    return kept


# ---------------- output ----------------
def to_markdown(items, rejected, meta):
    L = ["# Meeting notes", "", f"_{meta}_", "", "## Action items", "",
         "| owner | task | deadline | check |", "|---|---|---|---|"]
    for it in items:
        L.append(f"| {it.owner} | {it.task} | {it.deadline} | {'; '.join(it.flags)} |")
    if rejected:
        L += ["", "## Lines the model wrote that are not items", ""] + [f"- `{r.strip()}`" for r in rejected]
    return "\n".join(L) + "\n"


def notes(transcript, backend="bonsai"):
    answer, secs = extract(transcript, backend)
    items, rejected = parse(answer)
    items = reconcile(items, transcript)
    return to_markdown(items, rejected, f"{backend} · {secs:.0f} s · {len(items)} items"), answer
