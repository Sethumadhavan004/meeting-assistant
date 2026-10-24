# 07 · Limitations

_Confounds and biases. Completed in Stage 6._

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
