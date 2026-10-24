# 02 · Protocol

_Frozen before the first scored run. Any change after that is logged at the bottom with a date and reason._

## Prompts

- One meeting per file in `prompts/` (`m01_pricing.txt`, `m02_*.txt`, ...).
- Every file starts with the same instruction line:
  `Extract action items from this meeting as a list: owner, task, deadline.`
- Every meeting contains at least one ambiguous "we need..." item with no clear owner.
- Meetings are short, English, and written by the author.

## Gold set

- `gold.md` holds the correct items for every meeting, **written by the author before any model was run on that meeting**.
- Ambiguous items are marked `UNASSIGNED`, with a note on what counts as best / acceptable / wrong.

## Fairness rules

| rule | how it's enforced |
|---|---|
| Same prompt text for every model | `eval_runner.py` sends the prompt file as-is |
| No chat history | every request is a fresh single-turn call |
| Same context size | `CTX = 4096` for Ollama (`num_ctx`) and llama-server (`BONSAI_CTX`) |
| Same output cap | `MAX_TOKENS = 3000` |
| Same sampling | temperature 0 for every model (see below); presence penalty 0 on llama-server (Ollama's default) |
| CPU only | Ollama drops the iGPU (its log: `inference compute: cpu`); Bonsai started with `--device none -ngl 0` via `scripts/start_bonsai.ps1` |
| Same threads | 4 = all physical cores, for both runtimes |
| Same model parts | Bonsai's vision projector not loaded (`/props` → `vision: false`) |
| One request at a time | llama-server `-np 1`; the runner sends requests one by one |
| One model in RAM at a time | Ollama models unloaded after each batch (`keep_alive: 0`); Bonsai server stopped before Ollama runs |
| Clean machine | browser closed; idle RAM recorded with `eval_runner.py baseline` |
| No prompt caching | `cache_prompt: false` on llama-server, so prompt speed is measured every time |
| Gold set before outputs | gold written before any scored run; scoring rules fixed here first |

### Temperature choice

All runs use **temperature 0** (greedy, deterministic), so one run per prompt is repeatable
and models are compared on identical sampling. This is **off-spec for Granite**, whose model
card recommends temperature 1.0 / top_p 0.95. Granite may score differently at its recommended
settings; this is listed in [07-limitations.md](07-limitations.md).

## Rubric: count, don't rate

Each run's answer is matched item by item against `gold.md`.

| metric | how |
|---|---|
| recall | correct items found ÷ gold items |
| precision | correct items ÷ items extracted |
| owner accuracy | correct owners ÷ matched items |
| deadline accuracy | correct deadlines ÷ matched items |
| ambiguity handling | 2 = flagged unassigned, 1 = omitted, 0 = invented an owner |
| format valid | 1 if the answer can be parsed into owner / task / deadline |

**Matching:** an extracted item matches a gold item if it describes the same task, even when
the wording differs (e.g. "complete the copy" = "write copy"). Claude drafts the matches with a
one-line justification each; **the author makes the final call** on every judgment match.

**Not merged into one score.** Quality, time and RAM are reported side by side per
model × thinking mode. The models that no other model beats on every axis at once are the answer.

## Efficiency metrics (from `runs.csv`)

gen tok/s · prompt tok/s · output tokens · thinking share (thinking chars ÷ total chars) ·
time-to-answer (`wall_s`) · peak RAM delta vs idle · % of bandwidth ceiling.

A run with `finish = length` hit the 3000-token cap. That's recorded as a finding about
thinking, not discarded. A run where `ram_min_avail_gb` falls near 0 and speed collapses is
marked **invalid (swapping)**.

## Change log

| date | change | reason |
|---|---|---|
