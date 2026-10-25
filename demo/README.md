# The demo video: how it was made

**This is a scripted re-enactment.** The app was first used live, offline, with friends planning a
trip to Hyderabad. On this 8 GB, CPU-only laptop, screen-recording a live meeting while Moonshine and
the model are running wasn't feasible (free RAM drops below 1 GB during extraction). So the video
replays one scripted take of the same kind of meeting, and everything the app does in it is real.

## What is real and what is staged

| | |
|---|---|
| **Staged** | The conversation: 6 lines written for the demo ([`script.json`](script.json)) to include the cases the app is built for ("we need…", a reassigned task). The voices: synthetic, from Kokoro (an open-weight text-to-speech model), fed into the app as clean audio, each line 250 ms after the mic was live. Camera moves, cursor, captions and pop-outs. |
| **Real** | The app (same page, same code), Moonshine's transcription, Bonsai's notes, the code checks, and every timing shown. All from one recorded run, re-rendered frame by frame so the video is smooth regardless of CPU load. The model wait is shown at 4× with a badge. |

## Two takes

- **Take 1 was discarded** because it exposed a bug: each speaker click opened a new microphone, so
  the first ~0.5 s of every turn was lost. "We need a hotel near Charminar" became "Tell near
  Charminar", and the hotel went to Akhash with no "we need" left for the code to catch.
  Log: [`logs/take1-run-log.json`](logs/take1-run-log.json).
- The fix (one microphone stream per meeting) has its own commit and a browser test that fails on the
  old code ([`../tests/browser/mic_switch.test.js`](../tests/browser/mic_switch.test.js)).
- **Take 2 ran once**, with the same script, model, prompt and settings (checksums in the log), and
  stands as recorded. Log: [`logs/take2-run-log.json`](logs/take2-run-log.json).

What take 2 shows: the transcript is exact except "Hyderabad" → "Hiderabad"; the model gave the hotel
to Akhash (who said "we need") and the code moved it to unowned; the model listed the money task twice
(Goutham, who asked; Ram, who agreed) and the code flagged both. Notes took 20.9 s on CPU.

The plan, the four-reviewer panel's decisions and the retake ruling: [`plan-and-panel.md`](plan-and-panel.md).

## Files

| file | what |
|---|---|
| `script.json`, `clips/` | the 6 lines and their Kokoro audio (voices chosen by the author by ear) |
| `tts.py` | makes the clips (`pip install kokoro-onnx soundfile`, model files in `kokoro/`) |
| `record.js` | the real run: drives the app in headless Chrome, plays each clip into its mic, logs every request |
| `render.js` | re-renders the real app page from a log with a virtual clock, plus camera, cursor, captions |
| `popouts.json` | pop-out text, written after take 2 from its real output |
| `mix.js` | voices + two quiet Kenney (CC0) sounds, loudness-normalised; no music |
| `logs/` | both takes: transcripts, notes, every API call with timings, final screenshots |

## Reproduce

```powershell
cd demo
npm install
python tts.py script                 # needs kokoro/ model files (see tts.py)
# with `meeting-assistant serve` and the Bonsai server running:
node record.js                       # writes logs/new-run-log.json (never overwrites take 1/2)
node render.js                       # RUN_LOG=logs/new-run-log.json to render a new take
node mix.js                          # -> out/brag.mp4 ; SFX=<folder with Kenney sounds>
```
