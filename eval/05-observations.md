# 05 · Observations

_Qualitative notes from runs, dated. Append, don't rewrite._

## 2026-10-24 · Stage 2 setup and smoke test

Evidence: `raw/smoke-2026-10-24/` (one-line trivial prompt; **not** part of the results).

- **The demo start script didn't match the eval settings for the 4B model.** It used the Vulkan
  binary (prompt ops could go to the iGPU), presence penalty 1.0, auto server slots, and always
  loaded the vision projector; `--no-mmproj` couldn't override it (`/props` still showed
  `vision: true`). Replaced with `scripts/start_bonsai.ps1`, where every flag is explicit. Details in `01-setup.md`.
  Lesson: **check `/props` after starting a server**. A flag on the command line isn't proof it was applied.
- **The earlier manual Bonsai runs probably had these confounds too** (Vulkan op-offload, presence
  penalty 1.0, mmproj RAM). The manual numbers stay historical; see `07-limitations.md`.
- **The thinking toggle works both ways** on Bonsai and Granite: think off → `thinking_chars = 0`;
  think on → thinking separated from the answer. Even on a one-line meeting, thinking took
  ~14× the output tokens (24 → 333) and ~7× the time.
- **RAM pressure is real.** Granite running while the Bonsai server was still loaded left
  `ram_min_avail_gb = 0.12`, at the edge of swapping. Confirms the run order: stop the Bonsai server
  before the Ollama runs, browser closed.
- **First-prompt load time.** Ollama's `wall_s` for the first prompt of a batch includes model
  load (`load_s` 5.9–8.1 s); the Bonsai server is preloaded (`load_s = 0`). Compare
  time-to-answer as `wall_s − load_s`.
- Tooling: `Tee-Object` in Windows PowerShell 5.1 writes UTF-16 and locks the file, so the
  first server log (`raw/server-logs/bonsai-20261024-185627.log`) mixes encodings. The launcher
  now uses llama-server's own `--log-file`. That log is kept as captured.

## 2026-10-24 · Gold set: two-annotator check (m01–m07)

The author wrote `gold.md` without reading Claude's key; Claude compared the two before any model run.

- **Items:** the author found 45 of Claude's 47 intended items. Both misses were in the L-tier
  m06 (15 items): "Goutham fixes the Android crash by Friday" (only in a note) and "Elizabeth sends
  the notes this afternoon" (last line of the meeting).
- **Extra items from the author:** 3, all judgment calls. Resolved as: app launch → Optional;
  fire drill → Optional; "we need a press release" → removed, since it's assigned later in the same
  meeting (keeping it would double-count one task).
- **Field errors:** 3 deadlines missed or wrong, all on items in M/L meetings (m05 release notes
  "morning" vs "evening"; m05 docs and m06 onboarding marked "open" when the transcript says "before
  it ships" / "before launch").
- **Every trap was read the same way by both annotators**: reassignments, declined tasks, pronoun,
  deadline correction, changed deadlines.
- **Takeaway:** a careful human missed 2 items and 3 deadlines, all in the longer meetings. Length is
  hard for people too, which is the case for the product and the reason for testing L-tier chunks.
- **Product insight (author):** "we need a press release" is unassigned at minute 3 and assigned at
  minute ~10. In a live, chunked app, the early chunk's UNASSIGNED is *correct for that chunk*, so the
  app needs a reconciliation pass across chunks once the meeting ends.

## 2026-10-25 · Gold set: two-annotator check (m08)

- All 5 items the author listed matched Claude's key. The author merged "salary range" and "remote
  option" into one item; that settled Claude's borderline (split = duplicate, not penalised).
- Disagreement on classification, not content: the author first put "someone should let the
  non-shortlisted candidates know" under Optional, then Not action items. Resolved to **UNASSIGNED**
  for consistency with the identical "someone should" pattern in m03 and m06.
- Pattern across m04, m06, m08: annotators agree on *what* happened; consistency on *how a pattern
  is classified* needs explicit rules (the "How to read this file" key in `gold.md`).
- Before freezing, the protocol review also found Windows power mode on "Best power efficiency"
  (lower CPU clocks). Set to Best performance for all scored runs.
