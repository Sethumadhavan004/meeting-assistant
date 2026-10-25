# Meeting assistant v0 (local)

Turns a meeting into action items (`owner | task | deadline`), entirely on your own machine:
speech-to-text with **Moonshine**, extraction with a **small open model** on CPU, and a check step in
plain code. Nothing leaves the laptop.

Every design choice comes from the eval in [`../eval/`](../eval/README.md):

| choice | why (evidence) |
|---|---|
| Bonsai 4B + system prompt by default; Phi / Granite selectable | round 2: no model won on every axis; Bonsai was best on recall, deadlines and strict format ([03b](../eval/03b-round2-results.md)) |
| thinking **off** | thinking took ~10× longer and lost 7 of 16 answers to the token cap ([04](../eval/04-analysis.md)) |
| strict `owner \| task \| deadline` lines, parsed in code | the app needs output a program can read; header lines and copied example lines are skipped |
| "we need…" raised and owned by the same person → **UNASSIGNED** | the prompt couldn't fix this; the code rule fixed 11 wrong owners with 0 false alarms on round 2 ([`reconcile_check.py`](../eval/reconcile_check.py)) |
| similar tasks with different owners are **flagged, never merged** | word overlap can't tell "draft" from "review the press release"; deleting a task on a guess is the worst error |
| "who is speaking" buttons instead of diarization | owner accuracy depends on speaker names; a button gives exact names, a diarization model would guess (v1; diarization later) |

## Setup

```powershell
cd D:\projects\meeting-assistant
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt          # includes useful-moonshine-onnx and sounddevice
```

Start one model server:
- **Bonsai (default):** `.\scripts\start_bonsai.ps1` in its own terminal (see `eval/01-setup.md`)
- **Phi / Granite:** Ollama running, with `ollama pull phi4-mini` or `ollama pull granite4.2:3b`

## Use

**From a transcript file** (one line per turn, `Name: what they said`):

```powershell
python app\cli.py my-meeting.txt                 # writes my-meeting.notes.md
python app\cli.py my-meeting.txt --backend phi   # faster, finds fewer items
```

**Live, with the window:**

```powershell
python app\gui.py
```

1. Type the participants and press **Set**. One button appears per person.
2. **Click your name, speak, click it again** (or click the next speaker). Each turn is transcribed
   locally (~10× faster than real time on a 4-core laptop) and added as `Name: text`.
3. Fix any speech-to-text mistakes directly in the transcript box.
4. **Extract action items**, then read the **check** column before sharing.
5. **Save** writes `meetings/<date_time>/transcript.txt` and `notes.md` (git-ignored).

The first start downloads the Moonshine model (~20 s).

## Known limits (v0)

- The owner rule only catches "we need…" given to **the person who said it**. If the model gives it to
  someone else (m10: Priya's "somebody needs to" → Akhash), it is not caught.
- Duplicate detection is word overlap: it flags dependent tasks (fix / review the fix) and misses
  rephrased ones ("take the caterer quotes instead").
- One request per meeting; long meetings (> ~800 tokens of transcript) were not tested in the eval.
  Live chunking + cross-chunk reconciliation is the next step (`eval/08-next-iterations.md`).
- English only (Moonshine and the eval meetings).
- Actions (calendar, task tracker) are not done by the app; it only writes notes.
