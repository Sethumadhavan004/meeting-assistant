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

## 2026-10-25 · Stage 4: Bonsai think-on batch

- **Interrupted at m06** by Claude Code's background-job memory rule (it stops its own background
  jobs when system memory looks low). Lowest available RAM during the finished runs was
  1.38–1.87 GB, so the eval itself wasn't swapping. m01–m05 rows were already written; m06 left no
  partial row. Added `--only` to `eval_runner.py` to resume m06–m08 without duplicating rows.
  Remaining batches run in the author's own terminal.
- **m04: thinking used the whole 3000-token budget and produced an empty answer** (`finish = length`,
  `answer_chars = 0`). The end of the thinking text already contained the correct items, including
  the "13th" refinement, then "Okay, ready." and the cap. On a 77-word meeting, thinking cost the answer.
- Bonsai thinking used 1,589–3,000 output tokens per S/M meeting, i.e. 3.5–7 minutes each.
- Prompt speed fell from 30.7 to 12.6 tok/s across m01–m05 while generation stayed at 7.3–8.0 tok/s
  and CPU at ~99%. Cause unknown (heat-related slowdown? prompt length?). See `06-questions.md`.

## 2026-10-25 · Stage 4: Bonsai think-off batch, and the Bonsai batch overall

- Think-off: 8/8 finished (`finish = stop`), all answers present, `thinking_chars = 0`, 17–125 s per meeting.
- **Think-on lost 3 of 8 answers to the 3000-token cap: m04 (S) and both L meetings (m06, m07).**
  At a 4096 context, Bonsai with thinking can't handle ~5-minute chunks; thinking costs the answer.
- m08 think-on (quick look before scoring): no invented deadlines ("TBD" throughout), but the
  "someone should" item was given to Akhash, the person who said it.
- **Prompt speed depends on prompt length, not temperature:** both batches show ~31 tok/s at ~113
  prompt tokens down to ~10.5 at ~925, with the same values whether the meeting ran early or late.
  Bonsai reads longer prompts more slowly per token, the opposite of a well-batched CPU path.
- **RAM delta rising across the batch is the server growing,** not other apps (Notepad was open
  from m01): llama-server peak working set 1.86 GB vs 1.23–1.41 GB at startup, 3.45 GB private
  memory committed, Windows Memory Compression at 2.1 GB. Earlier I blamed Notepad; that was wrong.
- **Laptop unusable during runs:** 4 threads on a 4-core CPU = ~99.5% CPU. Expected by design, but
  it should have been said up front. Rule added: hands off the laptop during scored runs.

## 2026-10-25 · Stage 4: Granite and Phi batches; all runs complete

- Granite and Phi were run as one detached Windows process per batch (`Start-Process`) and waited on
  with bounded `Wait-Process`. That avoids Claude Code's background-job memory rule and its
  10-minute command limit (Granite m06 think-on took 634 s).
- **Granite think-on lost 4 of 8 answers to the 3000-token cap: m04, m05, m06, m08.** Bonsai lost
  m04, m06, m07. **m04 (S, pronoun/absent owner) and m06 (L) defeated both thinking models.**
- **Granite's prompt speed is flat (~45–67 tok/s) across prompt lengths;** Bonsai's falls from ~31 to
  ~10.5. The slowdown is specific to Bonsai's runtime/format, not to the CPU (supports Q1/Q4).
- Granite's generation speed falls as its own output grows (6.5 → 4.9 tok/s at 3000 tokens):
  each new token reads all earlier ones, so long thinking slows itself down.
- RAM delta also rose across the Granite think-on batch (2.3 → 3.2 GB), so rising RAM is **not**
  llama-server-specific (Q5 reworded). Both runtimes are llama.cpp-based.
- Validity: 40/40 rows, max context used 3926 ≤ 4096, lowest available RAM 0.52 GB, no speed
  collapse. All runs valid.

## 2026-10-25 · Stage 5: scoring draft (Claude; awaiting author review)

Files: `eval/scoring/labels.csv` (208 item labels), `runs.csv` (format), `score.py` → `scores.csv`.
42 REVIEW flags grouped into 6 decisions in `eval/scoring/REVIEW.md`. Numbers below use Claude's
defaults and may change after review.

- **Thinking off beats thinking on, for every model.** Recall: Granite off 0.94 vs on 0.28; Bonsai
  off 0.91 vs on 0.47. Mostly because thinking-on runs lost answers to the token cap. When thinking
  did finish, precision was perfect and deadlines were good.
- **Granite off and Phi off tie on recall (0.94)** but fail differently. Granite: best deadlines
  (0.96) and zero invented deadlines. Phi: fastest (27 s median), always well formatted (8/8), but
  invents "ASAP" deadlines (m08) and has the weakest owner accuracy (0.78).
- **Bonsai off handles ownership best** (owner 0.92, ambiguity 1.25: it flags unowned tasks as
  unassigned more often) but loses recall on L meetings (0.83: it dropped all three of Goutham's
  m06 tasks), invents "Immediate (during meeting)" deadlines in m08, and mislabels fields (5/8 format).
- **The universal failure: the "we need…/someone should…" task goes to the person who said it.**
  m02 venue → Akhash in 5/5 configs. Phi never flagged an unassigned item (ambiguity 0).
- **Reporter ≠ owner (m04):** Granite off and Phi gave Darcy's invites to Elizabeth, who reported it.
  Only Bonsai off resolved the pronoun.
- **Contradicting duplicates** (same task, second owner) appeared 9 times in non-thinking runs, often
  the original owner of a reassigned task listed alongside the new one (m02, m03, m07).
- **Nobody extracted m06's last-line item** ("I'll send out the notes this afternoon"); the author
  missed it in the first gold draft too.
- Changed-deadline traps (m06): Granite off fell for both (iOS "Monday", listing "Wednesday"); Phi
  and Bonsai off didn't.
