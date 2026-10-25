# 02 · Protocol

_**Frozen 2026-10-25**, before the first scored run, together with `gold.md` (8 meetings, 53 items).
Any change after this is logged at the bottom with a date and reason._

## Prompts

- One meeting per file in `prompts/` (`m01_pricing.txt`, `m02_*.txt`, ...).
- Every file starts with the same instruction line:
  `Extract action items from this meeting as a list: owner, task, deadline.`
- Every meeting contains at least one ambiguous "we need..." item with no clear owner.
- English only. m01 written by the author; m02–m08 written by Claude to a design brief (one trap per
  meeting: reassignment, decoy, declined task, pronoun, corrected deadline, no deadlines at all, ...).
- **Three length tiers** (details in `prompts/README.md`), because the product will feed live
  transcript chunks, and chunk size is a design decision this eval should inform:
  S (~100–150 tokens: m01–m04) · M (~260–350: m05, m08) · L (~650–800: m06, m07).
- **Size rule:** prompt tokens + `MAX_TOKENS` ≤ `CTX` (here ≤ ~1000 prompt tokens). Above it, a
  thinking run can overflow the context, and Ollama (drops oldest tokens) and llama-server (stops)
  handle that differently. Checked after each run from `prompt_tok + out_tok`.

## Gold set

- `gold.md` holds the correct items for every meeting, **written by the author before any model was run on that meeting**.
- Ambiguous items are marked `UNASSIGNED`, with a note on what counts as best / acceptable / wrong.
- Decoys (discussed but not agreed) are listed per meeting under **Not action items**; extracting one counts against precision.
- Borderline items are listed under **Optional**; they don't count for recall or precision.
- **Two-annotator check:** Claude, who wrote m02–m08, keeps its intended answers in
  `eval/design/claude-key.md`. The author writes `gold.md` without reading it. Every disagreement is
  resolved (fix the meeting, or mark the item as a judgment call) before any model run. Agreement is
  reported in `05-observations.md`.

## Fairness rules

| rule | how it's enforced |
|---|---|
| Same prompt text for every model | `eval_runner.py` sends the prompt file as-is |
| No chat history | every request is a fresh single-turn call |
| Same context size | `CTX = 4096` for Ollama (`num_ctx`) and llama-server (`-c 4096` in `scripts/start_bonsai.ps1`) |
| Same output cap | `MAX_TOKENS = 3000` |
| Same sampling | temperature 0 for every model (see below); presence penalty 0 on llama-server (Ollama's default) |
| CPU only | Ollama drops the iGPU (its log: `inference compute: cpu`); Bonsai started with `--device none -ngl 0` via `scripts/start_bonsai.ps1` |
| Same threads | 4 = all physical cores, for both runtimes |
| Same model parts | Bonsai's vision projector not loaded (`/props` → `vision: false`) |
| One request at a time | llama-server `-np 1`; the runner sends requests one by one |
| One model in RAM at a time | Ollama models unloaded after each batch (`keep_alive: 0`); Bonsai server stopped before Ollama runs |
| Clean machine | browser closed; **hands off the laptop during runs** (inference uses all 4 cores, and interactive use would bias timings); idle RAM recorded with `eval_runner.py baseline` |
| Same CPU clock behaviour | on AC power; Windows power mode **Best performance** for every run (it was "Best power efficiency" during the manual and smoke runs, which lowers clock speed) |
| No prompt caching | `cache_prompt: false` on llama-server, so prompt speed is measured every time |
| Gold set before outputs | gold written before any scored run; scoring rules fixed here first |

### Temperature choice

All runs use **temperature 0** (greedy, deterministic), so one run per prompt is repeatable
and models are compared on identical sampling. This is **off-spec for Granite**, whose model
card recommends temperature 1.0 / top_p 0.95. Granite may score differently at its recommended
settings; this is listed in [07-limitations.md](07-limitations.md).

## Rubric: count, don't rate

Each run's answer is matched item by item against `gold.md`.

**Step 1: match.** Each extracted item is labelled exactly one of:

| label | when |
|---|---|
| **matched** to gold item N | same task as gold item N, even if worded differently ("complete the copy" = "write copy"). The owner or deadline may still be wrong; those are scored separately |
| **optional** | matches an Optional item: ignored entirely |
| **wrong** | matches a Not action item, or matches nothing in gold (invented) |
| **duplicate** | same gold item as an earlier extracted item. Ignored, not penalised, so splitting one task into two lines (e.g. m08 salary + remote option) costs nothing |

**Step 2: count.**

| metric | how |
|---|---|
| recall | matched gold items ÷ gold items (UNASSIGNED items included) |
| precision | matched ÷ (matched + wrong) |
| owner accuracy | correct owners ÷ matched items |
| deadline accuracy | correct deadlines ÷ matched items. A deadline written for a gold `NONE` item is wrong |
| invented deadlines | count of deadlines written for gold `NONE` items (m08 tests this on purpose) |
| ambiguity handling | per gold UNASSIGNED item: 2 = flagged unassigned, 1 = omitted, 0 = invented an owner. Reported as the mean |
| format valid | 1 if every line can be read as owner / task / deadline |

An UNASSIGNED item that's omitted costs recall *and* scores 1 on ambiguity, so the order
"flag (best) > omit (ok) > invent (wrong)" holds in both metrics.

Claude drafts the labels with a one-line justification each; **the author makes the final call**
on every judgment match.

**Not merged into one score.** Quality, time and RAM are reported side by side per
model × thinking mode. The models that no other model beats on every axis at once are the answer.

## Efficiency metrics (from `runs.csv`)

gen tok/s · prompt tok/s · output tokens · thinking share (thinking chars ÷ total chars) ·
time-to-answer (`wall_s − load_s`, so Ollama's first-prompt model load isn't counted; load time is
reported separately) · peak RAM delta vs idle · % of bandwidth ceiling.

**Validity checks on every run:**
- `finish = length`: hit the 3000-token cap. Recorded as a finding about thinking, not discarded.
- `prompt_tok + out_tok > 4096`: context overflowed. **Invalid** (the size rule above failed).
- `ram_min_avail_gb` near 0 with collapsing speed: **invalid (swapping)**.

Single run per prompt at temperature 0. If time allows, one prompt is repeated to confirm the
outputs are identical (determinism check).

## Change log

| date | change | reason |
|---|---|---|
| 2026-10-25 | Clean machine rule: added hands-off during runs | Bonsai runs used ~99.5% CPU; any interactive use would bias timings. Clarifies an existing condition, no runs affected |
| 2026-10-25 | **Round 2 added** (baseline above unchanged). `eval_runner.py` gained `--system FILE` (system message, sent identically to both backends) and `--round NAME` (writes `runs-<name>.csv`, `outputs-<name>/`, never the baseline files). System prompt: `prompts/system/meeting-assistant.md`, frozen before any scored round-2 run, after one format smoke test on m01 | Tests whether a meeting-assistant system prompt fixes the baseline's ownership, deadline and format errors. Changes one parameter: the system prompt |
| 2026-10-25 | **Held-out meetings m09, m10** added (Claude-written after the system prompt; author writes gold blind; two-annotator check as before). Run with and without the system prompt | The prompt's rules were chosen after seeing baseline failures on m01–m08, so gains there may be overfitting. m09/m10 were never used to write the prompt |
| 2026-10-25 | Round 2 size note: the system prompt adds 292 tokens (m01: 99 → 391), so prompt + `MAX_TOKENS` can exceed 4096 on L meetings. Accepted for thinking-off runs only; the per-run validity check (actual `prompt_tok + out_tok` ≤ 4096) still applies | Thinking-off answers are 130–600 tokens; changing `MAX_TOKENS` would change a second parameter |
| 2026-10-25 | Round 2 format rule: **strict**. Format valid = every line parses as `owner \| task \| deadline` with nothing else. Matching rules unchanged | The app needs output a program can parse; the system prompt asks for this exact format |
