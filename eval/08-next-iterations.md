# 08 · Next iterations

The plan: **base eval → base model chosen → meeting-assistant app → DEV post → optimisation
rounds.** Every round is measured against the baseline with the same harness, gold set and protocol,
and changes **one parameter at a time**, so each stat change has a named cause.

## Done

- **Round 1: base** (2026-10-25). Default settings, temperature 0, ctx 4096, max_tokens 3000.
  [`03-results.md`](03-results.md).
- **Round 2: system prompt** (2026-10-25), + 2 held-out meetings. [`03b-round2-results.md`](03b-round2-results.md).
  Base model chosen: Bonsai + prompt.
- **App v1** (2026-10-26): Moonshine → transcript → Bonsai → code checks (owner rule, flag-not-merge,
  spoken deadline, possibly missed), local web app, tests. Was queued as #7 below.

## Queued for the optimisation rounds

| # | experiment | why (evidence) |
|---|---|---|
| 1 | Bonsai think-on with a bigger output budget for m04, m06, m07 | all three hit the 3000-token cap with an empty answer; does it get there given more room, and at what time cost? Needs a larger ctx (prompt + budget ≤ ctx) |
| 2 | Capped thinking (`--reasoning-budget N`, or `reasoning_effort: medium`) | PrismML docs suggest capping beats disabling on slow machines; test whether it keeps quality and bounds time |
| 3 | Live chunking + cross-chunk reconciliation vs whole meeting (m06) | the product feeds live chunks; "we need a press release" is unassigned in an early chunk and assigned later |
| 4 | Reassigned tasks: one owner, not two | the demo: "Ram, can you…?" / "Done" came back as two notes (asker and doer); the code only flags it |
| 5 | A prompt without example lines | 2 of 30 round-2 runs copied the examples |
| 6 | Real-audio test set (real voices, accents, crosstalk) | everything so far is clean text or clean synthetic audio, plus the author's own mic tests |
| 7 | Decisions as a second extraction type | "Not action items" are deferred/rejected decisions, already labelled in `gold.md` |
| 8 | Model extracts flat items, code builds the graph (dependencies, reassignments) | keep the small model's job small |
| 9 | llama-server memory growth across requests (Q5) | affects real RAM cost in a long-running app |
| 10 | Speaker detection (diarization) as an option beside the buttons | owner accuracy depends on names; measure how much a guessed speaker costs |
| 11 | Actions with confirmation (calendar, task tracker) | the author's goal: an assistant that can act, with a human approving each action |
