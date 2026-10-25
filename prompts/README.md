# Prompts

One meeting per `.txt` file. `eval_runner.py` only reads `*.txt`, so this README is never sent to a model.

Every file starts with the same instruction line:
`Extract action items from this meeting as a list: owner, task, deadline.`

| prompt | tier | words | why this tier |
|---|---|---|---|
| m01_pricing | S | 70 | baseline: can the model extract items at all |
| m02_offsite | S | 78 | |
| m03_newsletter | S | 108 | |
| m04_workshop | S | 77 | |
| m05_sprint | M | 258 | a short standup-sized chunk |
| m06_launch | L | 600 | ~5 min of speech: a realistic live-transcript chunk |
| m07_postmortem | L | 487 | second L in a different domain |
| m08_hiring | M | 197 | no deadlines at all: does the model invent them? |
| m09_escalation | S | 123 | **held-out** (round 2): written after the system prompt, never used to tune it |
| m10_budget | M | 242 | **held-out** (round 2): same |

**Size rule:** prompt tokens + `MAX_TOKENS` (3000) ≤ `CTX` (4096), so L ≤ ~1000 tokens.
Above that, a thinking run can overflow the context, and the runtimes handle overflow
differently (llama-server stops; Ollama drops the oldest tokens, i.e. the meeting). That would make the
comparison silently unfair. Longer meetings need a separate experiment at a larger context.

m01 was written by the author. m02–m10 were written by Claude (names chosen by the author); see `eval/02-protocol.md`.
