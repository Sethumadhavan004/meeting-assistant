# 07 · Limitations

_Confounds and biases: what this eval can and cannot claim._

## Test set

- Small: 8 meetings, 53 gold items (4 + 3 + 3 + 4 + 9 + 15 + 9 + 6), 8 of them UNASSIGNED.
- m02–m08 were written by an AI (Claude). Scripted dialogue is cleaner than real speech: no
  crosstalk, no speech-to-text errors, full sentences. Real transcripts will be harder.
- Longest meeting is ~800 tokens (context-size rule). Behaviour on longer chunks is untested here.

## Manual runs (`raw/manual/`, Oct 22–23) are historical only

Not comparable with the scripted runs, because they had:
- multi-turn chat history on Ollama
- slightly different prompt wording for Bonsai
- different context sizes (8192 vs 4096)
- Bonsai started via the demo script, so likely Vulkan op-offload, presence penalty 1.0, and the vision projector loaded (found 2026-10-24, see `05-observations.md`)
- Windows power mode "Best power efficiency" (lower CPU clocks), found 2026-10-25. The smoke test ran in this mode too

## RAM measurement

- `ram_delta_gb` is system-wide (used minus the idle baseline), not per process. Anything that
  changes on the machine during a batch shows up in it. For Bonsai the delta rose across the batch
  because the server process grew, so later rows include more than the model's own footprint.
- RAM delta also rose in the Ollama batches (Granite think-on 2.3 → 3.2 GB), so the max deltas in
  `03-results.md` are upper bounds, not per-model footprints (Q5).

## Sample size and repeatability

- **One run per prompt, temperature 0.** Greedy decoding is repeatable on the same build and
  machine, but the planned determinism check (repeat one prompt) was not run.
- **8 meetings, 53 items:** one item is ~2 points of recall. Differences of one or two items between
  the thinking-off setups (e.g. Granite and Phi 50/53 vs Bonsai 48/53) are not meaningful.
- No confidence intervals: too few samples to make them honest.

## Scoring

- **Gold and labels come from two people who know the meetings well:** the author wrote the gold
  set; Claude wrote m02–m08 and drafted every label; the author made the final call on all 42
  judgment rows. No blind third annotator.
- The baseline format rule ("a person can read every line as owner / task / deadline") is looser
  than an app needs. Format results would be lower under a parser.

## Settings

- **Temperature 0 is off-spec for Granite** (card: 1.0 / top_p 0.95). Granite may do better at its
  recommended settings (Q3).
- **Thinking budget:** 3000 tokens at ctx 4096 is a constraint of this 8 GB machine. Thinking-on
  results measure "thinking within this budget", not thinking in general.
- **Two runtimes.** Granite and Phi ran on Ollama (llama.cpp inside); Bonsai on PrismML's llama.cpp
  fork, because PQ2_0 needs it. Runtime differences are part of every Bonsai-vs-others comparison;
  Bonsai's slow prompt reading may be the runtime, not the model.
- **Quantisation is not equal:** Q4_K_M vs a 2.13-bit ternary format. The comparison is "what you can
  actually run", not "which architecture is better".

## Machine

- One laptop: Ryzen 3 4300U (4 cores), 8 GB single-channel DDR4-2667, Windows 11, CPU only.
  Speeds scale with memory bandwidth; another machine gives different absolute numbers, though the
  ceiling arithmetic should transfer.
- Inference used all 4 cores; timings assume nobody touched the laptop during runs.

## Transfer to real meetings

- Clean text input. The real pipeline adds speech-to-text errors and, without diarization, no
  speaker names. Owner accuracy depends on speaker names, so real-world owner scores will be lower.
