"""
core.py - transcript -> action items, with the fixes the eval showed are needed.

Pipeline (each step exists because of a finding in eval/):
  1. extract    one request to a local model, thinking off, with the round-2 system prompt
                (thinking cost ~10x the time and often the answer: eval/04-analysis.md)
  2. parse      strict `owner | task | deadline` lines; skip the header line and any line copied
                from the prompt's example (both seen in round 2: eval/05-observations.md)
  3. reconcile  in code, not in the prompt: the prompt fixed deadlines but not owners
                - "we need..." given to the person who said it -> needs an owner
                - similar tasks with different owners -> flagged for review, never merged
  4. suggest    "we need..." sentences no item covers -> "possibly missed", for the user to confirm
"""
import re
import time
from dataclasses import asdict, dataclass, field

import requests

from . import config

INSTRUCTION = "Extract action items from this meeting as a list: owner, task, deadline."

NEED = re.compile(r"\b(we need|we should|someone (should|needs|has to)|somebody (should|needs|has to)|"
                  r"it would be good if|needs to be|has to be)\b", re.I)
# for "possibly missed" suggestions: NEED minus "has to be / needs to be", which state conditions
# ("it has to be live before...") more often than ask for a task (measured on round 2)
ASK = re.compile(r"\b(we need|we should|someone (should|needs|has to)|somebody (should|needs|has to)|"
                 r"it would be good if)\b", re.I)
COMMIT = re.compile(r"\b(i'll|i will|i can|i'm going to|let me|i'll take|that's mine|i'll do)\b", re.I)
STOP = set("a an the to of for and or in on at by with from is are be it this that we our i you".split())


@dataclass
class Item:
    owner: str
    task: str
    deadline: str
    flags: list = field(default_factory=list)


# ---------------- 1. extract ----------------
def extract(transcript, backend=None, cfg=None):
    """Send the transcript, return (answer text, seconds). Raises config.BackendError if the server is down."""
    cfg = cfg or config.load()
    backend = backend or cfg["default_backend"]
    b = config.check(backend, cfg)
    body = {
        "model": b["model"],
        "messages": [{"role": "system", "content": cfg["system_prompt"].read_text(encoding="utf-8")},
                     {"role": "user", "content": f"{INSTRUCTION}\n\n{transcript.strip()}\n"}],
        "temperature": 0,
        "max_tokens": cfg["max_tokens"],
        "chat_template_kwargs": {"enable_thinking": False},  # llama-server; ignored by Ollama
    }
    t0 = time.perf_counter()
    r = requests.post(f"{b['url']}/v1/chat/completions", json=body, timeout=cfg["timeout_s"])
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"] or "", time.perf_counter() - t0


# ---------------- 2. parse ----------------
def example_lines():
    """The example lines in the system prompt; models sometimes copy them into the answer."""
    text = config.load()["system_prompt"].read_text(encoding="utf-8")
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


def missed_needs(items, transcript):
    """'We need...' sentences that no extracted item covers. Shown for review, never added as items:
    some are parked ideas or needs someone took later in the meeting."""
    out = []
    for name, text in speaker_lines(transcript):
        for sent in re.split(r"(?<=[.!?])\s+", text):
            if (ASK.search(sent) and not COMMIT.search(sent) and not sent.rstrip().endswith("?")
                    and not re.match(r"\s*(maybe|perhaps)\b", sent, re.I)
                    and all(overlap(it.task, sent) < 0.2 for it in items)):
                out.append((name, sent.strip()))
    return out


# ---------------- output ----------------
def notes(transcript, backend=None):
    """The whole pipeline. Returns a plain dict, so the CLI and the web app share one result shape."""
    cfg = config.load()
    backend = backend or cfg["default_backend"]
    answer, secs = extract(transcript, backend, cfg)
    items, rejected = parse(answer)
    items = reconcile(items, transcript)
    return {
        "backend": backend, "seconds": round(secs, 1), "raw": answer,
        "items": [asdict(it) for it in items],
        "missed": [{"speaker": s, "sentence": t} for s, t in missed_needs(items, transcript)],
        "rejected": [r.strip() for r in rejected],
    }


def to_markdown(result):
    L = ["# Meeting notes", "", f"_{result['backend']} · {result['seconds']:.0f} s · {len(result['items'])} items_",
         "", "## Action items", "", "| owner | task | deadline | check |", "|---|---|---|---|"]
    for it in result["items"]:
        L.append(f"| {it['owner']} | {it['task']} | {it['deadline']} | {'; '.join(it['flags'])} |")
    if result["missed"]:
        L += ["", "## Possibly missed", "", "_Someone said this was needed, but no action item covers it._", ""]
        L += [f"- **{m['speaker']}:** \"{m['sentence']}\"" for m in result["missed"]]
    if result["rejected"]:
        L += ["", "## Lines the model wrote that are not items", ""] + [f"- `{r}`" for r in result["rejected"]]
    return "\n".join(L) + "\n"
