# The app

Turns a meeting into action items (`owner | task | deadline`), entirely on your own machine:
speech-to-text with **Moonshine**, extraction with a **small open model** on CPU, and checks in
plain code. The web app listens on `127.0.0.1` only; audio and notes never leave the laptop.

Every design choice comes from the eval in [`../eval/`](../eval/README.md):

| choice | why (evidence) |
|---|---|
| Bonsai 4B + system prompt by default; Phi / Granite selectable | round 2: no model won on every axis; Bonsai was best on recall, deadlines and strict format ([03b](../eval/03b-round2-results.md)) |
| thinking **off** | thinking took ~10× longer and lost 7 of 16 answers to the token cap ([04](../eval/04-analysis.md)) |
| strict `owner \| task \| deadline` lines, parsed in code | the app needs output a program can read; header lines and copied example lines are skipped |
| "we need…" raised and owned by the same person → **unowned** | the prompt couldn't fix this; the code rule fixed 11 wrong owners with 0 false alarms on round 2 (written after seeing those meetings) ([`reconcile_check.py`](../eval/reconcile_check.py)) |
| similar tasks with different owners are **flagged, never merged** | word overlap can't tell "draft" from "review the press release"; deleting a task on a guess is the worst error |
| no deadline, but the source sentence names one → filled in and flagged | the author's mic test: "I will change it today" came back as NONE; neutral on the round-2 answers ([05](../eval/05-observations.md)) |
| "we need…" that no item covers → **Possibly missed**, never added silently | the author's mic test: the model skipped "we need someone to book the room"; 6 suggestions, 0 noise on round 2 |
| **speaker buttons** instead of diarization | owner accuracy depends on speaker names; a button gives exact names, diarization would guess (diarization later) |
| **one microphone stream per meeting**; a click only moves the cut point | opening a mic per click lost ~0.5 s at every turn start; found by the demo take ([`../tests/browser/`](../tests/browser/mic_switch.test.js)) |
| sticky note per item, **colour = owner**, unowned = white card | the eval's hard part is *who*, so the design makes ownership visible at a glance |

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e .                          # adds the `meeting-assistant` command
```

Start one model server (they are listed in [`../meeting-assistant.toml`](../meeting-assistant.toml)):
- **Bonsai (default):** `.\scripts\start_bonsai.ps1` in its own terminal (model download and flags: [`../eval/01-setup.md`](../eval/01-setup.md))
- **Phi / Granite:** Ollama running, with `ollama pull phi4-mini` or `ollama pull granite4.2:3b`

```powershell
meeting-assistant check      # which model servers are up, with the fix if one isn't
```

## Use

**Web app** (live meetings):

```powershell
meeting-assistant serve      # then open http://127.0.0.1:8765
```

1. Put the participants in `meeting-assistant.toml` (`participants = [...]`). Each gets a sticky colour.
2. **Click your name and speak.** Click the next person when they talk, or your own name again to stop.
   Each turn is transcribed locally (about 10× faster than real time on a 4-core laptop).
3. Fix speech-to-text mistakes directly in the transcript.
4. **Extract action items.** Notes land one per task. White cards ask "Who'll take it?"; red pencil
   marks what to check; **Possibly missed** lists needs nobody took ("Stick it on" adds one).
5. Edit any note (type an owner and press Enter to recolour it), then **Copy as Markdown** or **Save**
   (`meetings/<date_time>/`, git-ignored).

The first start downloads the Moonshine model (~20 s).

**From a transcript file** (one line per turn, `Name: what they said`):

```powershell
meeting-assistant notes my-meeting.txt                 # writes my-meeting.notes.md
meeting-assistant notes my-meeting.txt --backend phi   # faster, finds fewer items
```

## Tests

```powershell
pytest                                     # unit + regression replay of the 30 round-2 answers + web API
cd tests\browser; npm install; npm test    # needs `meeting-assistant serve` running: no audio lost on speaker switch
```

## Known limits

- The owner rule only catches "we need…" given to **the person who said it**. If the model gives it to
  someone else, or splits a reassigned task across two people (the demo: Goutham asked, Ram agreed),
  the code flags the pair but cannot tell which owner is right.
- Duplicate detection is word overlap: it flags dependent tasks (fix / review the fix) and misses
  rephrased ones.
- One request per meeting; transcripts longer than ~800 tokens were not tested in the eval.
  Live chunking + cross-chunk reconciliation is next ([`../eval/08-next-iterations.md`](../eval/08-next-iterations.md)).
- English only. Real voices, accents and crosstalk are untested beyond the author's own mic tests.
- The app writes notes; it does not act on them (calendar, task tracker) yet.
