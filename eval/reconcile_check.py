"""
reconcile_check.py - does the app's code-side owner rule help? Replays round-2 answers through
app/core.py (parse + reconcile), no new model runs, and rescores owners against gold.md.

Only the owner rule (reconcile step a) can change a score: it turns an owner into UNASSIGNED.
For every labelled item whose owner it changes: fixed if gold says UNASSIGNED, a false alarm if
the original owner was correct.

Usage:  python eval/reconcile_check.py
"""
import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "app"))
sys.path.insert(0, str(ROOT / "eval" / "scoring"))
from core import Item, reconcile  # noqa: E402
from score import load_gold  # noqa: E402


def answer_items(path):
    """Item lines in label numbering: non-empty answer lines except the header line."""
    text = path.read_text(encoding="utf-8").split("## Answer", 1)[1]
    out = []
    for raw in text.splitlines():
        line = re.sub(r"^\s*([-*•]|\d+[.)])\s*", "", raw).strip()
        if not line or [p.strip().lower() for p in line.split("|")] == ["owner", "task", "deadline"]:
            continue
        parts = [p.strip() for p in line.split("|")] + ["", ""]
        out.append(Item(parts[0], parts[1], parts[2]))
    return out


def main():
    gold = load_gold()
    labels = list(csv.DictReader(open(ROOT / "eval/scoring/r2/labels.csv", encoding="utf-8")))
    totals = {}
    changes = []
    for out in sorted((ROOT / "outputs-r2").glob("*.md")):
        rid = out.stem
        model, meeting = rid.split("_")[0], rid.split("_")[2]
        transcript = next((ROOT / "prompts").glob(f"{meeting}_*.txt")).read_text(encoding="utf-8")
        items = answer_items(out)
        before = [it.owner for it in items]
        for it in items:
            it.flags = []
        reconcile(list(items), transcript)  # step (a) edits owners in place
        t = totals.setdefault(model, {"fixed": 0, "false_alarm": 0, "other": 0, "matched": 0, "owner_ok_before": 0})
        seen = set()
        for r in labels:
            if r["run_id"] != rid or r["label"] != "matched" or int(r["gold"]) in seen:
                continue
            seen.add(int(r["gold"]))
            t["matched"] += 1
            t["owner_ok_before"] += r["owner_ok"] == "1"
            i = int(r["ext"]) - 1
            if items[i].owner == before[i]:
                continue
            gold_owner = gold[meeting][int(r["gold"])][0]
            kind = ("fixed" if gold_owner == "UNASSIGNED" and r["owner_ok"] == "0"
                    else "false_alarm" if r["owner_ok"] == "1" else "other")
            t[kind] += 1
            changes.append((rid, r["ext"], before[i], items[i].task, gold_owner, kind))

    print("| model | matched items | owner correct before | fixed | false alarms | owner correct after |")
    print("|---|---|---|---|---|---|")
    for m, t in totals.items():
        after = t["owner_ok_before"] + t["fixed"] - t["false_alarm"]
        print(f"| {m} | {t['matched']} | {t['owner_ok_before'] / t['matched']:.2f} | {t['fixed']} | "
              f"{t['false_alarm']} | {after / t['matched']:.2f} |")
    print()
    for c in changes:
        print(" ", c)


if __name__ == "__main__":
    main()
