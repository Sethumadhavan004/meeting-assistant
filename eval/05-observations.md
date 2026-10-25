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

## 2026-10-25 · Stage 5: author review closed

- All six scoring defaults accepted (`eval/scoring/REVIEW.md`); scores are final for the baseline round.
- **Product insight (author):** contradicting duplicates are captured items, not misses. A real app
  must add a **reconciliation step** that detects one task with two owners and resolves it (latest
  assignment wins, or flag for the user). Same need as the cross-chunk press-release case (m01–m07 check).
- **Format is a product requirement, not just a scoring detail.** The baseline accepted any line a
  person can read as owner / task / deadline. An app needs a format a program can parse, so the next
  round fixes the output format in the prompt.

## 2026-10-25 · Round 2: held-out gold, two-annotator check (m09, m10)

- The author wrote gold for m09/m10 without reading Claude's key. **Every trap was read the same way:**
  reported owner (Eric, absent), handover (Muhil), declined task (Akhash → Muhil), deadline changed
  twice (5th → 3rd → 2nd), both UNASSIGNED items, parked laptop idea.
- Differences, all resolved before any run:
  - m09: Elizabeth's address fix was a gold item for the author and Optional for Claude. It was done
    during the meeting, so → **Optional** (author agreed).
  - m10: the spreadsheet deadline was NONE for the author and "before the finance review" for Claude. It
    was said in the meeting, the same pattern as the author's m05 fix → **before the finance review**
    (author agreed).
  - m10: cancel seats + email the vendor: the author merged them, Claude split them → **merged**
    (the author's m08 precedent).
- Same as in m01–m07: content agreement is high; disagreements are about *classification*
  (done-in-meeting, implied deadline, merge vs split).

## 2026-10-25 · Round 2 runs (20:10–20:49)

- 36 runs, all valid: 30 with the system prompt (3 models × 10 meetings, `runs-r2.csv`), 6 baseline
  runs on held-out m09/m10 (`runs.csv`). All `finish = stop`; max context used 1441; lowest available RAM 0.78 GB.
- Machine: AC, Best performance. Edge "startup boost" background processes were running (6 processes,
  ~170 MB, <1 CPU-second per 5 s); judged too small to bias timings, noted here.
- With the system prompt, answers were much shorter (Granite 48–213 tokens, Phi 37–139, Bonsai
  42–157), consistent with the one-line-per-item format. Bonsai's time per meeting rose on long
  meetings (m06: 132 s), because the system prompt adds 292 prompt tokens and Bonsai reads prompts slowly.

## 2026-10-25 · Round 2 scoring draft (Claude; awaiting author review of `eval/scoring/r2/REVIEW.md`)

Tables: `eval/03b-round2-results.md` (generated by `eval/compare.py`). Seen = m01–m08, held-out = m09–m10.

- **The system prompt fixed deadlines, not owners.** Invented deadlines on seen meetings went 6 → 0
  (Phi) and 6 → 0 (Bonsai); deadline accuracy rose (Phi .86 → .93, Bonsai .85 → .96). Owner accuracy
  barely moved (Granite .84 → .83, Phi .78 → .84, Bonsai .92 → .86). "We need… → the speaker" survived
  an explicit rule: m02's venue still went to Akhash in 3/3 runs, m01's page to Priya in 3/3.
- **Shorter, faster answers, but fewer items for two models.** Median output fell ~50–60%, time-to-answer
  fell for Granite (44 → 24 s) and Phi (27 → 20 s). Recall fell for Granite (.94 → .87) and Phi
  (.94 → .85); Bonsai's rose (.91 → .94). Asking for terse output seems to cost recall on the Q4 models.
- **Precision went to ~1.** Phi had 0 wrong items on seen meetings; contradicting duplicates fell for
  Phi (3 → 0), not for Granite (4 → 4).
- **Bonsai got slower** (36 → 45 s) despite shorter answers: the system prompt adds 292 prompt
  tokens and Bonsai reads prompts slowly.
- **Format:** Bonsai 8/8 and Phi 7/8 parse strictly. Granite printed the format's header line in 6/10
  runs (decision B).
- **Prompt-design lesson: small models copy examples.** Two runs pasted the system prompt's example
  lines into the answer as action items. Examples must be clearly marked as examples, or replaced by a
  format description only.
- **Held-out (m09–m10, 8 items):** precision 1.00 for all three with the prompt, deadlines up for
  Granite and Phi, recall down for Phi and Bonsai. One item is 12.5 points here, so the held-out set
  shows direction only. It does not contradict the seen-meeting pattern.

## 2026-10-25 · App v0: code-side checks, measured on round-2 answers (no new model runs)

- **Owner rule in code** ("we need…" raised by X and given to X, X never committed → UNASSIGNED),
  replayed over all 30 round-2 answers (`eval/reconcile_check.py`): **11 wrong owners fixed, 0 false
  alarms.** Owner accuracy: Granite .81 → .94, Bonsai .86 → .89, Phi .84 → .88 (seen + held-out
  pooled). One fix is on held-out m09. The rule was written after seeing m01–m08, so treat the
  seen-meeting gain as optimistic. It cannot catch "we need" given to a third person (m10 spreadsheet → Akhash).
- **Duplicate detection by word overlap can't tell dependent tasks apart:** "draft" vs "review the press
  release", "fix the login bug" vs "review the fix", "submit iOS build" vs "submit Android build". At every
  threshold tried (0.3–0.7) it confused about as many different-task pairs as it found true duplicates.
  The first app draft dropped the second line of a pair, which would have deleted Darcy's review task.
  Changed to: merge only near-identical lines (≥ 0.8, same owner); flag similar lines with different
  owners and keep both. Replay: 0 items lost; true conflicts flagged (m02 caterer quotes, m07 replay);
  dependent tasks get a harmless "check" flag.
- **Determinism check (protocol "if time allows"):** the app's Bonsai answer for m01 was identical
  word for word to the round-2 run. Temperature 0 repeats on this setup.
- **Prompt caching in the app:** m01 took 11 s in the app vs 32 s in the eval, because the eval disables
  `cache_prompt` to measure prompt reading, and the app reuses the unchanged system prompt.
- **Moonshine base (ONNX, CPU):** a 5.6 s synthetic turn was transcribed exactly ("licences" →
  "licenses") in 0.5 s, ~11× faster than real time; a 45 s turn was split at quiet points into 21.8 s +
  28.6 s (model limit 64 s). Tested with Windows' built-in speech synthesis, not a real voice yet.

## 2026-10-25 · App: "possibly missed" suggestions, package, tests

- **The author's real-mic test:** Moonshine transcribed both turns exactly; Bonsai listed Akhash's task
  but **omitted** "Priya: We need someone to book the room". An omission, not a wrong owner, so the
  owner rule can't help: it only fixes items the model lists.
- **"Possibly missed" suggestions** (code: "we need…" sentences no item covers; shown for review,
  never added as items). Replayed on round 2: first version 9 suggestions (2 recovered skipped
  UNASSIGNED gold items, 2 pointed to other skipped items, 1 nudge, 1 Optional, **3 noise**, all from
  "it *has to be* live…"). Dropping "has to be / needs to be" from the suggestion pattern → 6
  suggestions, 0 noise. That tweak was made after seeing these meetings.
- Restructured into a package (`meeting_assistant/`, `pyproject.toml`, `meeting-assistant` command,
  `meeting-assistant.toml` for model servers, clear message when a server is down).
- **Tests:** 51 (unit tests per rule + regression replay of all 30 round-2 answers that locks in
  0 tasks lost, 11 fixed / 0 false alarms, 6 suggestions). Mutation check: restoring merge-on-similarity
  and switching off the owner rule each made 2 tests fail.

### 2026-10-25 · author's second mic test (web app)

- Bonsai + prompt, 6 spoken turns, 16 s. Speech-to-text good (one name misheard: "Sedu").
  Two UNASSIGNED items correct ("verify the customers are okay", "take care of customer service").
  **Deadline miss:** Goutham said "I will change it **today**"; the model wrote NONE.
- **Spoken-deadline step** (reconcile step c): deadline NONE + the source sentence (owner's own
  sentences first, word overlap ≥ 0.25 with the task) names a time → fill it, flag "check".
  Replayed on round 2: first version 1 fixed, 1 partial ("on the 30th" for gold "30th and 31st"),
  **1 false alarm** (phi m06 "find someone… after the 31st" got "on the 30th"). Cause: the task
  already carried its timing. Skip when the task text has a time word → **0 changes on round 2**
  (the m03 fix is lost too: its task says "next week's"). So the step is neutral on our 30 answers
  and fixes the live case; its value is unmeasured beyond that. Tests: 60 (3 new; mutation check:
  removing the skip rule fails 1).
