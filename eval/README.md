# Eval: small open models for meeting action items on an 8 GB CPU-only laptop

**Research question:** on an 8 GB CPU-only laptop, which small open model gives the best
action-item quality per second and per GB, and what does "thinking" mode cost?

## Index

| file | contents | changes over time? |
|---|---|---|
| [01-setup.md](01-setup.md) | hardware, runtimes, models | rarely |
| [02-protocol.md](02-protocol.md) | prompts, gold set, rubric, fairness rules | frozen before runs |
| [03-results.md](03-results.md) | tables generated from `runs.csv` + `scores.csv`, no opinions | regenerated |
| [04-analysis.md](04-analysis.md) | what the numbers mean, app design implications | yes |
| [05-observations.md](05-observations.md) | qualitative notes from runs | append-only |
| [06-questions.md](06-questions.md) | open doubts, with status | yes |
| [07-limitations.md](07-limitations.md) | confounds and biases | yes |
| [08-next-iterations.md](08-next-iterations.md) | roadmap for optimisation rounds | yes |
| `scoring/` | labels.csv, runs.csv, score.py, REVIEW.md | labels reviewed by author |
| `report.py`, `charts/` | builds `03-results.md` and the charts from the CSVs | regenerated |
| [03b-round2-results.md](03b-round2-results.md), `compare.py` | round 2 (system prompt) vs baseline, seen vs held-out meetings | regenerated |
| `reconcile_check.py` | replays round-2 answers through the app's code checks, rescored against gold | regenerated |
| `../tests/` | unit tests, the round-2 regression replay, web API, browser mic test | yes |
| `../demo/` | the demo video's scripts and both take logs (a scripted re-enactment) | frozen |
| `raw/` | logs exactly as captured, **never edited** | append-only |

Raw data never changes; interpretation does. Keeping them apart means rewriting the
analysis can't corrupt the evidence.

## Where the data lives

- `../prompts/*.txt`: one meeting per file, identical text sent to every model
- `../gold.md`: hand-written correct answers (written before any model run)
- `../runs.csv`: one row per run (speed, tokens, RAM, CPU), written by `eval_runner.py`
- `../outputs/<run_id>.md`: full prompt, thinking and answer for each run
- `../scores.csv`: per-run quality scores against `gold.md`
- `raw/manual/`: the first hand-typed runs (Oct 22–23, 2026). Historical only, not mixed into `runs.csv`

## How to reproduce

```powershell
cd D:\projects\meeting-assistant
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Ollama models
ollama pull granite4.2:3b
ollama pull phi4-mini

# Bonsai: in its OWN terminal, left open (see 01-setup.md)
# then, browser closed:
python eval_runner.py baseline
python eval_runner.py run --model bonsai  --think on
python eval_runner.py run --model bonsai  --think off
# stop the Bonsai server (Ctrl+C) to free RAM, then:
python eval_runner.py run --model granite --think on
python eval_runner.py run --model granite --think off
python eval_runner.py run --model phi     --think off

# score (after labelling outputs in eval/scoring/labels.csv), then build tables + charts
python eval/scoring/score.py
python eval/report.py

# round 2: the same runs with the system prompt, into runs-r2.csv / outputs-r2/
.\scripts\run_round2.ps1 -Part ollama      # and -Part bonsai with the Bonsai server up
python eval/scoring/score.py --dir r2
cd eval; python compare.py; python reconcile_check.py; cd ..

# the app's checks, locked to the measured numbers
pytest
```

