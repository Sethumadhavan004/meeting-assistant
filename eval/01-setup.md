# 01 · Setup

## Hardware

| item | value | why it matters |
|---|---|---|
| machine | HP L14 | |
| CPU | AMD Ryzen 3 4300U (Zen 2), 4 cores / 4 threads | every runtime uses 4 threads (verified 2026-10-24) |
| SIMD | AVX2 yes, AVX-512 / VNNI no | decides which optimized kernels llama.cpp can use |
| RAM | 8 GB DDR4-2667, **single channel** (1 of 2 slots) | caps memory bandwidth |
| visible RAM | 7.4 GB (650 MB reserved for integrated Radeon graphics) | |
| available RAM | ~2.7 GB with a browser open, more with it closed | browser closed for all runs |
| GPU | integrated AMD Radeon, not used | **all runs are CPU-only** |
| OS / shell | Windows 11, PowerShell | |

### Memory bandwidth ceiling

Generating one token reads (roughly) every weight once, so on a memory-bound CPU:

```
max tokens/s ≈ memory bandwidth ÷ model file size
bandwidth    = 2667 MT/s × 8 bytes × 1 channel = 21.3 GB/s
```

`eval_runner.py` logs this ceiling and the % of it each run reaches (`bw_ceiling_tps`, `pct_of_ceiling`).

## Runtimes

| runtime | version | endpoint | used for |
|---|---|---|---|
| Ollama | 0.40.10 | `http://localhost:11434/api/chat` (native, exact token counts and durations) | granite, phi |
| PrismML llama.cpp fork (Bonsai demo repo) | [PrismML-Eng/Bonsai-demo](https://github.com/PrismML-Eng/Bonsai-demo) | `http://localhost:8080/v1/chat/completions` (with `timings` block) | bonsai |
| Python | 3.13.5, deps in `requirements.txt` | | `eval_runner.py` |

## Models under test

| key | model | runtime | quant | file size | thinking? |
|---|---|---|---|---|---|
| granite | `granite4.2:3b` | Ollama | Q4_K_M | 2.244 GB | yes (on/off) |
| phi | `phi4-mini` | Ollama | Q4_K_M | 2.492 GB | no |
| bonsai | Ternary-Bonsai-2-4B (`Ternary-Bonsai-2-4B-PQ2_0.gguf`) | llama-server (PrismML fork) | PQ2_0, 2.13 bpw, group 128 | 1.146 GB (+ 0.367 GB mmproj) | yes (on/off) |

Sizes are decimal GB (10⁹ bytes), measured 2026-10-24 from Ollama's `/api/tags` and the `.gguf`
files on disk. They use the same unit as the 21.3 GB/s bandwidth figure.

| model | bandwidth ceiling (21.3 ÷ size) |
|---|---|
| granite | 9.5 tok/s |
| phi | 8.5 tok/s |
| bonsai | 18.6 tok/s |

Bonsai's model lives in `models/Bonsai-demo/models/bonsai2-gguf/4B/` (not committed).
The server also auto-loads a multimodal projector (`...mmproj-Q8_0.gguf`), which adds RAM
that the text task doesn't need. See [07-limitations.md](07-limitations.md).

## Starting the Bonsai server

It must run in **its own terminal, left open** (the server exits when its terminal closes):

```powershell
cd D:\projects\meeting-assistant
.\scripts\start_bonsai.ps1      # every flag is written out and commented in this file
```

The script saves its log and exact command line to `eval/raw/server-logs/`.

### Why not the demo's `start_llama_server.ps1`

Read from the demo script and the binary on 2026-10-24. For the 4B model it:

| demo default | effect on a fair eval | our launcher |
|---|---|---|
| uses 27B unless `BONSAI_MODEL` is set | wrong model | model path is explicit |
| only the **Vulkan** build is installed; `-ngl 0` still allows `--op-offload` to the iGPU | prompt processing may not be CPU-only | `--device none -ngl 0` |
| context sized by RAM tier (8192 here) | different from Ollama | `-c 4096` |
| server slots "auto" | context may be split across slots | `-np 1` |
| 4B sampling profile sets **presence penalty 1.0** | changes greedy picks even at temperature 0; Ollama uses 0 | `--presence-penalty 0` |
| loads the vision projector (mmproj) when the file exists; `--no-mmproj` can't override it | +0.37 GB RAM the text task doesn't use | mmproj not passed |

### Verified CPU-only and matched settings (2026-10-24)

- `/props`: 1 slot, `n_ctx` 4096, presence penalty 0, `vision: false`
- server log: `n_threads = 4`, `n_slots = 1, n_ctx_slot = 4096`
- Windows GPU counters: llama-server holds ~0.6 MB of GPU memory, so no model buffers on the iGPU
- Ollama log: `dropping integrated GPU` → `inference compute: cpu`; default threads = 4 physical cores
- The binary ships `ggml-cpu-haswell.dll` (AVX2), so AVX2 CPU code is available to it
