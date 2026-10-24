# 07 · Limitations

_Confounds and biases. Completed in Stage 6._

## Manual runs (`raw/manual/`, Oct 22–23) are historical only

Not comparable with the scripted runs, because they had:
- multi-turn chat history on Ollama
- slightly different prompt wording for Bonsai
- different context sizes (8192 vs 4096)
- Bonsai started via the demo script, so likely Vulkan op-offload, presence penalty 1.0, and the vision projector loaded (found 2026-10-24, see `05-observations.md`)
