# 04 · Analysis

_Interpretation of [03-results.md](03-results.md). Baseline round, 2026-10-25: 40 runs, 8 meetings,
53 gold items, temperature 0, one run per prompt. Small sample: read differences of one or two items
as noise (see [07-limitations.md](07-limitations.md))._

## What the numbers mean

**There is no single winner with thinking off.** Granite, Phi and Bonsai each lead on something,
and none beats another on every axis at once, so by the protocol's rule all three are "the answer":

| | strongest at | weakest at |
|---|---|---|
| Granite 4.2 3B | deadlines (0.96), never invents one | flags unowned tasks rarely (ambiguity 0.25); fell for both changed-deadline traps in m06; most contradicting duplicates (4) |
| Phi-4-mini | fastest (27 s median), always well formatted (8/8) | owners (0.78); writes "ASAP" where no deadline exists (6 in m08); **never** flagged an unowned task (ambiguity 0) |
| Bonsai 4B ternary | owners (0.92), flags unowned tasks most often (1.25) | recall on long meetings (0.83: dropped all three of Goutham's m06 tasks); field format (5/8); "Immediate" deadlines in m08 |

**Recall is not the problem; ownership is.** All three thinking-off setups found 91–94% of items and
were ≥ 96% precise. The errors that matter for a meeting assistant are about *who* and *when*:

- **"We need… / someone should…" goes to the speaker.** In m02 all 5 setups gave the venue to Akhash,
  who only said it was needed. Across the 8 UNASSIGNED items, the best setup (Bonsai off) flagged
  fewer than half. A wrong owner is worse than a missing one: it tells a real person they agreed to
  something they didn't.
- **Reporter ≠ owner.** In m04 Elizabeth reports that Darcy will send invites; Granite off and Phi
  gave the task to Elizabeth.
- **Contradicting duplicates.** 9 times a thinking-off answer listed one task twice with two owners,
  usually the original owner of a reassigned task beside the new one. The task was captured; the
  model didn't resolve the reassignment.

None of these is a recall failure, so a bigger model is not the only fix. They are candidates for
(a) explicit rules in a system prompt (round 2) and (b) a reconciliation step in code.

## Bandwidth ceiling vs measured speed

On a CPU, each generated token reads the whole model from RAM once, so
`ceiling ≈ memory bandwidth ÷ model size` (21.3 GB/s here).

- **The two Q4 models run at 72–73% of their ceiling.** The arithmetic predicted their speed before
  any run. The gap is expected overhead: the KV cache is also read every token, and real bandwidth
  is below the spec figure.
- **Bonsai, at 1.15 GB, has twice their ceiling (18.6 tok/s) but reaches only 45%** (8.4 tok/s). It is
  still the fastest generator, just by 1.2–1.4×, not the 2× its size suggests.
- **Bonsai reads prompts 3× slower** (17.6 vs ~50 tok/s median) **and gets slower as prompts grow**
  (~31 → ~10.5 tok/s from 113 to 925 prompt tokens), while Granite stays flat. Generation is
  bandwidth-bound; prompt reading is compute-bound, and the PQ2_0 format seems to lack an efficient
  batched CPU path (Q1, Q4). For a meeting app, which reads long transcripts and writes short lists,
  **prompt speed matters as much as generation speed.**
- **Q2 (why the manual runs reached a lower % of ceiling):** now 73% / 45% on real meetings vs ~65% /
  ~30% in the manual runs. Consistent with the manual-run confounds, the biggest being Windows "Best
  power efficiency" mode. Not proven per factor.

## Cost of thinking

| | thinking off | thinking on |
|---|---|---|
| Bonsai: recall · median time | 0.91 · 36 s | 0.47 · 382 s |
| Granite: recall · median time | 0.94 · 44 s | 0.28 · 454 s |

- **Thinking cost ~10× the time and lost half or more of the recall.** Thinking was 97–98% of the
  output. 7 of 16 thinking runs hit the 3000-token cap before writing any answer (Bonsai 3/8,
  Granite 4/8), including m04, a 77-word meeting.
- **When thinking did finish, it was careful:** precision 1.00 and deadlines 0.96–1.00. The reasoning
  isn't useless; the budget is. Whether a bigger or capped budget recovers the answers is queued in
  [08-next-iterations.md](08-next-iterations.md) (#1, #2).
- **Long outputs slow themselves down:** Granite's generation fell from 6.5 to 4.9 tok/s as output
  approached 3000 tokens, because every new token also reads all earlier ones.

On this machine, for this task, **thinking off is the right default**.

## Implications for a model-swappable local app

1. **Thinking off by default**, with a hard output cap. An empty answer after 7 minutes is the worst
   outcome for a user.
2. **Never trust an owner the model infers from "we".** The app should show such items as unassigned,
   or ask, rather than silently assign them.
3. **Reconcile in code, after the model.** Merge duplicates, keep the latest owner of a reassigned
   task, and flag conflicts. This also fixes the cross-chunk case (a task unassigned early in a
   meeting and assigned later).
4. **Fix the output format.** "Readable by a person" (the baseline rule) is not enough for an app; the
   prompt must ask for a format code can parse, and the app must validate it.
5. **Keep the model swappable.** No model won on every axis, and the right choice depends on the
   machine (bandwidth for generation, compute for prompt reading). The app talks to a local
   OpenAI-style endpoint, so Ollama and llama-server are interchangeable.
6. **Chunk size:** all three thinking-off setups held up to ~800-token meetings (L recall 0.83–0.92),
   with the losses concentrated in L. Shorter chunks plus reconciliation is the safer design.

**Base model choice is deferred to round 2.** The three thinking-off setups are within one or two
items of each other on recall, and the round-2 system prompt targets exactly the errors that separate
them (owners, invented deadlines, format).
