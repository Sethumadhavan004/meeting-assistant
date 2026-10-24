# 06 · Open questions

| # | question | status | notes |
|---|---|---|---|
| 1 | Is Bonsai's low % of bandwidth ceiling (~30% in manual runs) caused by a missing optimized AVX2 kernel for PQ2_0? | open | The binary does ship AVX2 CPU code (`ggml-cpu-haswell.dll`), so if it's a kernel gap, it's specific to the PQ2_0 format. The smoke test showed ~43% on a 40-token prompt; wait for real prompts. |
| 2 | Why is % of ceiling higher in the smoke test (Granite ~79%, Bonsai ~43%) than in the manual runs (~65%, ~30%)? | open | Hypothesis: a tiny prompt means a tiny KV cache to read on each token. Possibly also the manual-run confounds (Vulkan offload, mmproj, multi-turn history). Compare on real meetings. |
| 3 | Would Granite score differently at its recommended sampling (temp 1.0, top_p 0.95) instead of temp 0? | open, out of scope | Protocol fixes temp 0 for every model; see `02-protocol.md`. |
| 4 | Why did Bonsai's prompt speed fall from 30.7 to 12.6 tok/s across the think-on batch while generation speed stayed flat? | **answered** | Prompt length, not heat: the think-off batch (cooler CPU) gives the same tok/s at the same prompt length (~31 at 113 tokens → ~10.5 at 925). Bonsai's prompt processing gets slower per token as prompts grow; supports Q1 (no efficient batched kernel for PQ2_0). Granite/Phi comparison pending. |
| 5 | Does llama-server's memory keep growing across requests (peak working set 1.23 → 1.86 GB, 3.45 GB private)? Context checkpoints? | open | Affects Bonsai's real RAM cost in a long-running app. Could test by sending the same prompt 10 times and logging the process's memory. |
