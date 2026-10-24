# 06 · Open questions

| # | question | status | notes |
|---|---|---|---|
| 1 | Is Bonsai's low % of bandwidth ceiling (~30% in manual runs) caused by a missing optimized AVX2 kernel for PQ2_0? | open | The binary does ship AVX2 CPU code (`ggml-cpu-haswell.dll`), so if it's a kernel gap, it's specific to the PQ2_0 format. The smoke test showed ~43% on a 40-token prompt; wait for real prompts. |
| 2 | Why is % of ceiling higher in the smoke test (Granite ~79%, Bonsai ~43%) than in the manual runs (~65%, ~30%)? | open | Hypothesis: a tiny prompt means a tiny KV cache to read on each token. Possibly also the manual-run confounds (Vulkan offload, mmproj, multi-turn history). Compare on real meetings. |
| 3 | Would Granite score differently at its recommended sampling (temp 1.0, top_p 0.95) instead of temp 0? | open, out of scope | Protocol fixes temp 0 for every model; see `02-protocol.md`. |
