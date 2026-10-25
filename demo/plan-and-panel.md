# Plan for panel review: sticky-note redesign + demo video

Status: DRAFT, awaiting panel approval. Author: Claude (acting as engineer/director for the user, Sethu).

## Context (read this first)

- Product: **Meeting Assistant**, a privacy-first meeting note-taker that runs entirely on an 8 GB,
  4-core, CPU-only Windows laptop. Click your name, talk; Moonshine (open speech model) transcribes;
  a small open model (Ternary Bonsai 4B via llama.cpp) extracts **owner | task | deadline**; plain
  code then checks the model (wrong owners from "we need…", missing deadlines, possibly missed tasks).
  Repo: `D:\projects\meeting-assistant` (app: `meeting_assistant/web/static/index.html`, pipeline:
  `meeting_assistant/core.py`, research: `eval/` especially `eval/04-analysis.md`, `eval/05-observations.md`).
- Purpose: DEV.to Hacktoberfest "Slow and Steady" challenge (open-source AI at the core, "rewards
  laziness", explain why open innovation matters). Judged: writing quality most, then relevance,
  creativity, technical execution. **Deadline: Mon 26 Oct 2026 12:29 IST (~12 h from now).**
  The video goes in the post's "Demo" section.
- Research finding the product is built on: small models find tasks easily but get **owners**
  wrong ("we need to book the venue" gets assigned to whoever said it). Code fixes it, not prompts.
- Constraints: 7.4 GB RAM total, ~1.2–2 GB free with the model server + app + user's Chrome/VS Code
  open. Everything must run locally. No retakes to make the model look better (see Honesty).
- User's direction this turn (verbatim gist): current black/white design "too generic"; try
  **unique, note-taking-friendly fonts**; action items as **sticky notes, yellow plus picked
  colours, a bit papery, unruled**; then a demo video (Remotion / brag-style) of a **real use case:
  friends planning a trip to Hyderabad — Sethu, Goutham, Akhash, Ram**, simulated in real time,
  **super smooth, proper pop-outs, no abrupt edits, directed for the audience**; must not break
  while the model server and web app run.

---

## A. Redesign: "the paper desk"

**Concept.** The transcript is a sheet of unruled paper; the action items are sticky notes on the
desk beside it. **Each person has a sticky-note colour**, and it follows them: their speaker button,
their name dot in the transcript, and every note they own. Ownership is the hard part the research
found, so the design makes "who owns what" readable at a glance. Unowned tasks are plain white
cards asking "Who's taking this?". Things to check are marked in **red pencil** (the teacher's red
pen = review), the only red besides the recording dot.

**Type** (both open-licence, bundled in the app, no font CDN):
- **Kalam** (Indian Type Foundry, handwriting): sticky-note text, the brand word, panel titles.
  Handwriting = "written by people"; Kalam is legible at small sizes and fits the Indian context.
- **iA Writer Quattro** (the typeface of the iA Writer note app): transcript, controls, labels.
  A writing-app face, calm and very readable; tabular numbers for timers.
- Rejected: Caveat (overused), a monospace (labels-in-mono is a cliché), a serif display face.

**Colour tokens.**
| token | light | dark |
|---|---|---|
| desk (page) | #efece5 + faint paper fibre texture | #1d1c1a + same texture, darker |
| sheet (transcript paper) | #fffdf8 | #2a2825 |
| ink / ink-2 | #2a2925 / #6e695f | #efe9dc / #a9a294 |
| sticky palette, fixed order per person | yellow #ffe27a, pink #ffb3c8, blue #aedcf4, green #c4e4a3, orange #ffc58c, lilac #d8c6f3 | same papers at ~92% brightness; ink on notes stays dark |
| unowned card | #ffffff, dashed outline | #f1ede4 |
| red pencil (check / recording) | #d1453b | #ff6b5e |

**Layout** (desktop; stacks on phones):
```
┌ ✎ Meeting Assistant (Kalam)          [● bonsai ▾]  [Light|Auto|Dark] ┐
├──── transcript sheet ───────────┬──── the desk: sticky notes ────────┤
│ Transcript            ● 0:07    │ Action items          5 notes  21 s│
│ (●Sethu)(●Goutham)(●Akhash)(●Ram) + add person                       │
│                                 │ ┌───────┐ ┌───────┐ ┌───────┐      │
│ ● Sethu  0:00                   │ │Goutham│ │ Who's │ │  Ram  │      │
│ Okay, Hyderabad trip…           │ │book   │ │taking │ │collect│      │
│                                 │ │tickets│ │this?  │ │money  │      │
│ ● Goutham 0:05                  │ │by tmrw│ │hotel  │ │by Wed │      │
│ I'll book the tickets…          │ └───────┘ └───────┘ └───────┘      │
│                                 │   ~ torn scrap: "Possibly missed" ~│
│ [Extract action items] Open Clear│ [Copy as Markdown] [Save]          │
└─────────────────────────────────┴────────────────────────────────────┘
```
- Notes sit at slight, fixed tilts (−1.5°…+1.5°, by position), with a darker adhesive band at the top
  and a soft lifted-corner shadow. Hover straightens a note (motion answers the user only).
- **One orchestrated moment:** when extraction finishes, the notes are stuck down one by one
  (80 ms stagger, small drop + settle). Nothing else animates on its own except the recording dot
  and the live mic meter.
- Notes stay fully editable (owner, task, deadline) and deletable; "Possibly missed" becomes a torn
  paper scrap with "Stick it on" (adds an unowned note).
- **Participants become editable** in the app (+ add person / remove), default list from
  `meeting-assistant.toml`, remembered per browser. Needed anyway for real use (the user's friends).
- Light and dark both kept; the existing toggle stays.
- Accessibility: owner name always written on the note (colour is never the only cue); visible
  focus; reduced-motion respected; contrast of ink on every sticky colour ≥ 7:1.

## B. Demo video

### Method (the important engineering decision)
A live screen recording would stutter exactly when it matters: transcription and the model use all
4 CPU cores. So, two phases, as the brag skill also prescribes ("every frame a pure function of time"):

1. **Real run (once, one take).** Headless Chrome drives the real app at 127.0.0.1:8765. Each
   friend's line is spoken by a Windows offline text-to-speech voice and fed in as the
   **microphone** (the browser's getUserMedia is pointed at that audio), so the app's real capture,
   resampling, Moonshine transcription, Bonsai extraction and code checks all run for real. Every
   response and timing is logged; the result is also saved by the app's own Save button.
2. **Deterministic render.** The **real app page** (same HTML/CSS/JS) is replayed from that log in a
   headless browser with a virtual clock: every frame is computed, then screenshotted, so the video
   is perfectly smooth regardless of CPU load. Camera moves (zoom/pan), captions, a drawn cursor and
   pop-outs live in a stage layer around the app. ffmpeg encodes 1920×1080, 30 fps, with audio.
   - Considered Remotion: it would need the UI re-implemented in React (a copy that could drift from
     the real app) plus ~300 MB of installs. The replay renders the real page instead.

### Honesty rules (non-negotiable)
- One take. No re-running or re-wording the script to get nicer model output. If the model gets
  something wrong, the video shows the app flagging it / the user fixing it.
- On-screen disclosure: "Voices are synthetic. Speech recognition, notes and timings are real, from
  one run on this laptop." The model wait is time-compressed with a visible "4× speed" badge.
- Every number shown comes from the run log or `eval/` files. No invented stats or testimonials.

### Script (first draft, ~35 s of speech; scripted to include the cases the app handles)
1. **Sethu:** "Okay, Hyderabad trip. We leave on the twelfth, so let's split the work."
2. **Goutham:** "I'll book the train tickets for all four of us by tomorrow."
3. **Akhash:** "We need a hotel near Charminar, something under three thousand a night."  ← "we need" = no owner
4. **Ram:** "I'll find a good biryani place for the first night."  ← commitment, no deadline
5. **Goutham:** "Ram, can you collect the money from everyone by Wednesday?"  ← owner is Ram, not the speaker
6. **Ram:** "Sure, I'll do that."
7. **Akhash:** "And I'll make the itinerary and share it in the group on Friday."

### Storyboard (~62 s, landscape 1920×1080, 30 fps)
| # | time | scene | on screen | audio |
|---|---|---|---|---|
| 1 | 0–4 s | **Hook** | Paper desk. Handwritten (Kalam): "Four friends plan a trip to Hyderabad." then "Who's booking the hotel?" | soft paper sound; music bed starts low |
| 2 | 4–8 s | **Reveal** | The app slides in; caption: "A meeting assistant that runs on an 8 GB laptop. Nothing leaves it." | |
| 3 | 8–42 s | **The meeting** | Drawn cursor clicks each name; the pill fills with that person's colour, mic meter moves with the voice; the line appears as a subtitle while spoken; then the real Moonshine text lands on the sheet. Camera eases to ~1.2× on the transcript. | the TTS voices; music ducked |
| 4 | 42–50 s | **Extract** | Cursor clicks "Extract action items"; counter runs with a "4× speed" badge; sticky notes stuck down one by one; camera glides to the desk. | light paper taps per note |
| 5 | 50–60 s | **Pop-outs (3 × ~3.5 s)** | (a) a note lifts out, enlarged: "Goutham said 'I'll'. Owner, task, deadline: from his own words." (b) the white card: "'We need a hotel' isn't a promise. It stays unowned until someone takes it." (c) whichever real check fired (red pencil / possibly missed), or Ram's note: "Goutham asked, Ram agreed: the owner is Ram." Exact copy follows the real output. | |
| 6 | 60–66 s | **Outro** | "Open models, on a CPU: Moonshine for speech, Bonsai 4B for notes." + two real numbers from the run (e.g. speech ~N× real time, notes in N s) + disclosure line + title. | music resolves |

Transitions: one continuous camera, no jump cuts; scene 1→2 dips through the paper background;
pop-outs scale out from the element they explain and back into it.

### Resource plan (RAM is the risk)
- A background monitor logs free RAM / CPU every 5 s for the whole job.
- Phase 1: one headless Chrome (~300 MB) + the running app and model server. Abort if free RAM < 500 MB.
- Phase 2: model server idle; one headless Chrome at 1920×1080, frames piped straight into ffmpeg
  (no 1,800 PNGs on disk). Abort/pause if free RAM < 500 MB.
- Uses Node (installed) + puppeteer-core with the already-installed Chrome: no browser download.

## C. Post outline
Mapped onto the DEV template in `Hacktoberfest-2026/post-outline.md` (tags show whose idea each
pointer is). The user writes the post; Claude edits and fact-checks.

## Questions for the panel
1. Is the redesign concept distinctive and right for the product, or gimmicky?
2. Is the video's story, length and pacing right for DEV readers and judges?
3. Is the real-run + deterministic-replay method honest enough to call it a demo?
4. Anything that would embarrass the author in front of ML-literate readers?

---

## Panel decisions (2026-10-25 ~23:55 IST) — all four: APPROVE WITH CHANGES

Reviewers: marketing lead, motion designer, senior PM, ML research scientist. Conflicts resolved by Claude:

- **Length ~55 s** (motion wanted ~72, marketing ~48): cut script line 1 and the itinerary line;
  pop-outs use the ML-approved wording, held 0.3 s/word + 0.6 s.
- **Hook:** open mid-meeting on Akhash's "We need a hotel near Charminar…", Kalam card "Who's
  booking the hotel?". No claim about what the model says before the run shows it.
- **Ending answers the hook (PM):** cursor types "Akhash" onto the white card; it turns his colour.
- **Pop-out order (PM):** white card → Ram (owner ≠ speaker) → red-pencil check (if one fired).
  Copy (ML, exact): (b) model left it unowned → "'We need a hotel' isn't a promise. The model left
  it unowned." / code rule fired → "The model gave it to Akhash. A code check saw he never took it,
  so it's unowned." (c) right → "Goutham asked, Ram agreed. Here the model got the owner right."
  Wrong → show the error and the fix.
- **Disclosure (ML, exact):** "Scripted conversation, written to include the cases the app is built
  for. One take, not retried. Voices are synthetic and fed straight in as clean audio. Transcript,
  notes and timings are real, from that run, re-rendered frame by frame." Plus a persistent corner
  label "Synthetic voices · real run" and "Real voices, accents and crosstalk: untested."
- **Numbers on screen:** only this run's log: "This run: X s of synthetic speech transcribed in Y s;
  notes in Z s (4-core laptop, CPU only)." No eval "~11×". "Your audio and notes stay on the laptop."
- **Motion (motion designer):** ≤ 3 camera moves, cubic-bezier(0.65,0,0.35,1), ≥ 1.5 s hold after
  each; cursor curved paths 450–700 ms, 250 ms settle, click = 0.9× for 80 ms + 24 px ring 300 ms;
  subtitles top-centre band (never bottom), Quattro 34 px, max 2 lines, fade out before the real
  Moonshine text lands; 4× wait in-camera with 300 ms speed ramps, badge in red pencil, real seconds
  on the counter; note drop 180 ms stagger, 1.06→1.0 scale, 12 px drop, 320 ms
  cubic-bezier(0.34,1.4,0.64,1); scene 1→2 = app sheet slides onto the desk (24 px + fade, 600 ms).
- **Audio:** voices ≈ −16 LUFS, music −30 dB under speech / −20 dB elsewhere, 400 ms ducks, ≤ 2 paper SFX.
- **Design:** Kalam ≥ 22 px at 1.0×; owner colour with a fallback colour for unknown names; hold
  longest on the white unowned card; 2% grain against banding.
- **Scope cut list (PM, in order):** editable participants UI (→ config only) · torn-scrap styling ·
  dark-mode tuning · Quattro · texture/shadows · camera + music · replay renderer (fallback: real-time
  capture with the wait cut and labelled). UI freeze ~02:00 IST; ≥ 4 h kept for the user's post.
- **Not done:** Wi-Fi-off proof (needs the user's system; their call). Script lines are frozen
  below; "Hyderabad" was misheard as "hadraba" in a voice test, and the mishearing stays if it recurs.

### Frozen script
1. Sethu: "Okay guys, let's split the Hyderabad work."
2. Goutham: "I'll book the train tickets for all four of us by tomorrow."
3. Akhash: "We need a hotel near Charminar, something under three thousand a night."
4. Ram: "I'll find a good biryani place for the first night."
5. Goutham: "Ram, can you collect the money from everyone by Wednesday?"
6. Ram: "Done, I'll do it."
