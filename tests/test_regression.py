"""
Regression: replay the 30 real round-2 answers (outputs-r2/) through the app's checks and lock in
what was measured (eval/05-observations.md). If a change to core.py moves any of these numbers,
the test fails, and the change needs a new measurement and a dated observation, not a quiet edit.
"""
import csv
import sys
from pathlib import Path

import pytest

from meeting_assistant.core import missed_needs, parse, reconcile

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "eval"))
OUTPUTS = sorted((ROOT / "outputs-r2").glob("*.md"))


def answer(path):
    return path.read_text(encoding="utf-8").split("## Answer", 1)[1]


def transcript(path):
    meeting = path.stem.split("_")[2]
    return next((ROOT / "prompts").glob(f"{meeting}_*.txt")).read_text(encoding="utf-8")


def test_all_30_round2_answers_present():
    assert len(OUTPUTS) == 30


@pytest.mark.parametrize("path", OUTPUTS, ids=lambda p: p.stem[:24])
def test_no_gold_matched_task_is_lost(path):
    labels = [r for r in csv.DictReader(open(ROOT / "eval/scoring/r2/labels.csv", encoding="utf-8"))
              if r["run_id"] == path.stem and r["label"] == "matched"]
    items, _ = parse(answer(path))
    tasks_before = [it.task for it in items]
    kept = {it.task for it in reconcile(items, transcript(path))}
    for r in labels:
        ext = int(r["ext"]) - 1
        if ext < len(tasks_before):  # label numbering includes rejected two-field lines
            task = tasks_before[ext]
            assert task in kept or tasks_before.count(task) > 1, f"gold item {r['gold']} lost: {task}"


def test_owner_rule_matches_measurement():  # 11 fixed, 0 false alarms
    from reconcile_check import run
    totals, _ = run()
    assert {m: t["fixed"] for m, t in totals.items()} == {"bonsai": 2, "granite": 7, "phi": 2}
    assert sum(t["false_alarm"] for t in totals.values()) == 0


def test_missed_need_suggestions_match_measurement():  # 6 suggestions, 0 noise
    got = []
    for path in OUTPUTS:
        tr = transcript(path)
        got += [(path.stem.split("_")[0], path.stem.split("_")[2], s)
                for s, _ in missed_needs(reconcile(parse(answer(path))[0], tr), tr)]
    assert sorted(got) == sorted([("bonsai", "m10", "Priya"), ("granite", "m06", "Priya"),
                                  ("phi", "m06", "Priya"), ("phi", "m07", "Muhil"),
                                  ("phi", "m07", "Muhil"), ("phi", "m07", "Akhash")])
