# 08 · Next iterations

The plan: **base eval (this round) → base model chosen → meeting-assistant app → DEV post →
optimisation rounds.** Every round is measured against this baseline with the same harness, gold
set and protocol, and changes **one parameter at a time**, so each stat change has a named cause.

## Round 1: base (done 2026-10-25)

Default settings, temperature 0, ctx 4096, max_tokens 3000. Results in `03-results.md`.

## Queued for the optimisation rounds

| # | experiment | why (evidence) |
|---|---|---|
| 1 | Bonsai think-on with a bigger output budget for m04, m06, m07 | all three hit the 3000-token cap with an empty answer; does it get there given more room, and at what time cost? Needs a larger ctx (prompt + budget ≤ ctx) |
| 2 | Capped thinking (`--reasoning-budget N`, or `reasoning_effort: medium`) | PrismML docs suggest capping beats disabling on slow machines; test whether it keeps quality and bounds time |
| 3 | Chunked + reconciled vs whole meeting (m06) | the product feeds live chunks; "we need a press release" is unassigned in an early chunk and assigned later |
| 4 | Decisions as a second extraction type | "Not action items" are deferred/rejected decisions, already labelled in `gold.md` |
| 5 | Model extracts flat items, code builds the graph (dependencies, reassignments) | keep the small model's job small |
| 6 | llama-server memory growth across requests (Q5) | affects real RAM cost in a long-running app |
| 7 | Moonshine speech-to-text → transcript → best model | the full local pipeline |
